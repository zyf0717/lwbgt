#include "lwbgt.h"

#include <errno.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define FIELD_COUNT 19
#define LINE_CAPACITY 1024
#define MAX_CASES 512

static void fail(const char *message)
{
    fprintf(stderr, "batch-test-error: %s\n", message);
    exit(2);
}

static int split(char *line, char **fields)
{
    int count = 0;
    char *start = line;
    char *cursor;

    for (cursor = line;; ++cursor) {
        if (*cursor == ',' || *cursor == '\0') {
            if (count >= FIELD_COUNT) return count + 1;
            fields[count++] = start;
            if (*cursor == '\0') return count;
            *cursor = '\0';
            start = cursor + 1;
        }
    }
}

static int32_t integer(const char *text)
{
    char *end = NULL;
    long value;

    errno = 0;
    value = strtol(text, &end, 10);
    if (errno || end == text || *end) fail("invalid integer field");
    return (int32_t)value;
}

static double number(const char *text)
{
    char *end = NULL;
    double value;

    errno = 0;
    value = strtod(text, &end);
    if (errno || end == text || *end) fail("invalid numeric field");
    return value;
}

static lwbgt_input_v1 parse_input(char **field)
{
    lwbgt_input_v1 input;

    input.year = integer(field[2]);
    input.month = integer(field[3]);
    input.day = integer(field[4]);
    input.hour = integer(field[5]);
    input.minute = integer(field[6]);
    input.gmt_offset_hours = integer(field[7]);
    input.averaging_minutes = integer(field[8]);
    input.urban = integer(field[18]);
    input.latitude_deg_north = number(field[9]);
    input.longitude_deg_east = number(field[10]);
    input.solar_w_m2 = number(field[11]);
    input.pressure_hpa = number(field[12]);
    input.air_temperature_c = number(field[13]);
    input.relative_humidity_percent = number(field[14]);
    input.wind_speed_m_s = number(field[15]);
    input.wind_height_m = number(field[16]);
    input.vertical_temperature_difference_c = number(field[17]);
    return input;
}

static lwbgt_output_v1 scalar(const lwbgt_input_v1 *input)
{
    lwbgt_output_v1 output;

    output.estimated_wind_speed_m_s = (float)input->wind_speed_m_s;
    output.status = calc_wbgt(
        input->year,
        input->month,
        input->day,
        input->hour,
        input->minute,
        input->gmt_offset_hours,
        input->averaging_minutes,
        input->latitude_deg_north,
        input->longitude_deg_east,
        input->solar_w_m2,
        input->pressure_hpa,
        input->air_temperature_c,
        input->relative_humidity_percent,
        input->wind_speed_m_s,
        input->wind_height_m,
        input->vertical_temperature_difference_c,
        input->urban,
        &output.estimated_wind_speed_m_s,
        &output.globe_temperature_c,
        &output.natural_wet_bulb_c,
        &output.psychrometric_wet_bulb_c,
        &output.wbgt_c
    );
    return output;
}

static int same_float(float left, float right)
{
    uint32_t left_bits;
    uint32_t right_bits;

    memcpy(&left_bits, &left, sizeof(left_bits));
    memcpy(&right_bits, &right, sizeof(right_bits));
    return left_bits == right_bits;
}

static int same_output(const lwbgt_output_v1 *left, const lwbgt_output_v1 *right)
{
    return left->status == right->status &&
        same_float(left->estimated_wind_speed_m_s, right->estimated_wind_speed_m_s) &&
        same_float(left->globe_temperature_c, right->globe_temperature_c) &&
        same_float(left->natural_wet_bulb_c, right->natural_wet_bulb_c) &&
        same_float(left->psychrometric_wet_bulb_c, right->psychrometric_wet_bulb_c) &&
        same_float(left->wbgt_c, right->wbgt_c);
}

static void check_argument_contract(const lwbgt_input_v1 *input)
{
    lwbgt_output_v1 output;
    lwbgt_output_v1 unchanged;

    if (lwbgt_calc_batch_v1(NULL, NULL, 0) != LWBGT_BATCH_OK)
        fail("zero-count null call failed");

    memset(&output, 0xa5, sizeof(output));
    unchanged = output;
    if (lwbgt_calc_batch_v1(NULL, &output, 1) != LWBGT_BATCH_INVALID_ARGUMENT)
        fail("null input was accepted");
    if (memcmp(&output, &unchanged, sizeof(output)) != 0)
        fail("invalid call modified output");
    if (lwbgt_calc_batch_v1(input, NULL, 1) != LWBGT_BATCH_INVALID_ARGUMENT)
        fail("null output was accepted");
}

int main(int argc, char **argv)
{
    lwbgt_input_v1 inputs[MAX_CASES];
    lwbgt_output_v1 expected[MAX_CASES];
    lwbgt_output_v1 actual[MAX_CASES];
    char identifiers[MAX_CASES][32];
    char line[LINE_CAPACITY];
    size_t count = 0;
    size_t index;
    FILE *stream;

    if (argc != 2) fail("expected CASES.csv");
    stream = fopen(argv[1], "r");
    if (stream == NULL) fail("cannot open cases");
    if (fgets(line, sizeof(line), stream) == NULL) fail("cases are empty");

    while (fgets(line, sizeof(line), stream) != NULL) {
        char *field[FIELD_COUNT];

        if (count == MAX_CASES) fail("too many cases");
        line[strcspn(line, "\r\n")] = '\0';
        if (split(line, field) != FIELD_COUNT) fail("case width differs");
        if (strlen(field[0]) >= sizeof(identifiers[count])) fail("case id is too long");
        strcpy(identifiers[count], field[0]);
        inputs[count] = parse_input(field);
        expected[count] = scalar(&inputs[count]);
        ++count;
    }
    if (ferror(stream) || fclose(stream)) fail("cannot read cases");
    if (count == 0) fail("no cases generated");

    check_argument_contract(&inputs[0]);
    memset(actual, 0xa5, count * sizeof(*actual));
    if (lwbgt_calc_batch_v1(inputs, actual, count) != LWBGT_BATCH_OK)
        fail("batch call failed");

    for (index = 0; index < count; ++index) {
        if (!same_output(&expected[index], &actual[index])) {
            fprintf(stderr, "batch-test-error: mismatch for %s\n", identifiers[index]);
            return 2;
        }
        if (inputs[index].wind_height_m == 2.0 &&
            !same_float(actual[index].estimated_wind_speed_m_s,
                        (float)inputs[index].wind_speed_m_s))
            fail("2 m wind output is not deterministic");
    }

    printf("batch-equivalence: %zu bit-identical cases\n", count);
    return 0;
}
