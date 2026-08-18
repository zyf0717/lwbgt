#include "lwbgt.h"

#include <R.h>
#include <R_ext/Rdynload.h>
#include <Rinternals.h>

enum { INPUT_FIELD_COUNT = 17, OUTPUT_FIELD_COUNT = 6 };

static void require_column(SEXP column, SEXPTYPE type, R_xlen_t count, const char *name)
{
    if (TYPEOF(column) != type)
        error("%s has the wrong R storage type", name);
    if (XLENGTH(column) != count)
        error("%s has the wrong length", name);
}

static SEXP lwbgt_batch_example(SEXP frame)
{
    static const char *output_names[OUTPUT_FIELD_COUNT] = {
        "status", "estimated_wind_speed_m_s", "globe_temperature_c",
        "natural_wet_bulb_c", "psychrometric_wet_bulb_c", "wbgt_c"
    };
    SEXP columns[INPUT_FIELD_COUNT];
    SEXP result;
    SEXP names;
    lwbgt_input_v1 *inputs;
    lwbgt_output_v1 *outputs;
    R_xlen_t count;
    R_xlen_t index;
    int field;

    if (TYPEOF(frame) != VECSXP || XLENGTH(frame) != INPUT_FIELD_COUNT)
        error("input must contain exactly 17 columns in lwbgt_input_v1 order");
    count = XLENGTH(VECTOR_ELT(frame, 0));
    for (field = 0; field < 8; ++field) {
        columns[field] = VECTOR_ELT(frame, field);
        require_column(columns[field], INTSXP, count, "integer input column");
    }
    for (; field < INPUT_FIELD_COUNT; ++field) {
        columns[field] = VECTOR_ELT(frame, field);
        require_column(columns[field], REALSXP, count, "numeric input column");
    }

    inputs = (lwbgt_input_v1 *)R_alloc((size_t)count, sizeof(*inputs));
    outputs = (lwbgt_output_v1 *)R_alloc((size_t)count, sizeof(*outputs));
    for (index = 0; index < count; ++index) {
        inputs[index].year = INTEGER(columns[0])[index];
        inputs[index].month = INTEGER(columns[1])[index];
        inputs[index].day = INTEGER(columns[2])[index];
        inputs[index].hour = INTEGER(columns[3])[index];
        inputs[index].minute = INTEGER(columns[4])[index];
        inputs[index].gmt_offset_hours = INTEGER(columns[5])[index];
        inputs[index].averaging_minutes = INTEGER(columns[6])[index];
        inputs[index].urban = INTEGER(columns[7])[index];
        inputs[index].latitude_deg_north = REAL(columns[8])[index];
        inputs[index].longitude_deg_east = REAL(columns[9])[index];
        inputs[index].solar_w_m2 = REAL(columns[10])[index];
        inputs[index].pressure_hpa = REAL(columns[11])[index];
        inputs[index].air_temperature_c = REAL(columns[12])[index];
        inputs[index].relative_humidity_percent = REAL(columns[13])[index];
        inputs[index].wind_speed_m_s = REAL(columns[14])[index];
        inputs[index].wind_height_m = REAL(columns[15])[index];
        inputs[index].vertical_temperature_difference_c = REAL(columns[16])[index];
    }
    if (lwbgt_calc_batch_v1(inputs, outputs, (size_t)count) != LWBGT_BATCH_OK)
        error("lwbgt_calc_batch_v1 rejected the input");

    PROTECT(result = allocVector(VECSXP, OUTPUT_FIELD_COUNT));
    PROTECT(names = allocVector(STRSXP, OUTPUT_FIELD_COUNT));
    for (field = 0; field < OUTPUT_FIELD_COUNT; ++field) {
        SEXP column = PROTECT(allocVector(field == 0 ? INTSXP : REALSXP, count));
        SET_VECTOR_ELT(result, field, column);
        SET_STRING_ELT(names, field, mkChar(output_names[field]));
        UNPROTECT(1);
    }
    setAttrib(result, R_NamesSymbol, names);
    for (index = 0; index < count; ++index) {
        INTEGER(VECTOR_ELT(result, 0))[index] = outputs[index].status;
        REAL(VECTOR_ELT(result, 1))[index] = outputs[index].estimated_wind_speed_m_s;
        REAL(VECTOR_ELT(result, 2))[index] = outputs[index].globe_temperature_c;
        REAL(VECTOR_ELT(result, 3))[index] = outputs[index].natural_wet_bulb_c;
        REAL(VECTOR_ELT(result, 4))[index] = outputs[index].psychrometric_wet_bulb_c;
        REAL(VECTOR_ELT(result, 5))[index] = outputs[index].wbgt_c;
    }
    UNPROTECT(2);
    return result;
}

static SEXP lwbgt_esat_example(SEXP temperature_k, SEXP phase)
{
    if (XLENGTH(temperature_k) != 1 || TYPEOF(temperature_k) != REALSXP ||
        XLENGTH(phase) != 1 || TYPEOF(phase) != INTSXP)
        error("esat expects one numeric temperature and one integer phase");
    return ScalarReal(esat(REAL(temperature_k)[0], INTEGER(phase)[0]));
}

static const R_CallMethodDef call_methods[] = {
    {"lwbgt_batch_example", (DL_FUNC)&lwbgt_batch_example, 1},
    {"lwbgt_esat_example", (DL_FUNC)&lwbgt_esat_example, 2},
    {NULL, NULL, 0}
};

void R_init_lwbgt_r_example(DllInfo *dll)
{
    R_registerRoutines(dll, NULL, call_methods, NULL, NULL);
    R_useDynamicSymbols(dll, FALSE);
}
