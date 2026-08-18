#define _GNU_SOURCE
#include "lwbgt.h"

#include <errno.h>
#include <math.h>
#include <sched.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define FIELD_COUNT 19
#define LINE_CAPACITY 1024
#define MAX_COHORTS 8

typedef struct {
    char cohort[32];
    int year, month, day, hour, minute, gmt, avg, urban;
    double lat, lon, solar, pressure, air, rh, wind, height, delta;
} Case;

typedef struct {
    char name[32];
} Cohort;

static volatile double consumed_checksum;

static void fail(const char *message)
{
    fprintf(stderr, "benchmark-error: %s\n", message);
    exit(2);
}

static int split(char *line, char **fields)
{
    int count = 0;
    char *start = line;
    for (char *cursor = line;; ++cursor) {
        if (*cursor == ',' || *cursor == '\0') {
            if (count >= FIELD_COUNT) return count + 1;
            fields[count++] = start;
            if (*cursor == '\0') return count;
            *cursor = '\0'; start = cursor + 1;
        }
    }
}

static long integer(const char *text)
{
    char *end = NULL; errno = 0;
    long value = strtol(text, &end, 10);
    if (errno || end == text || *end) fail("invalid integer");
    return value;
}

static double number(const char *text)
{
    char *end = NULL; errno = 0;
    double value = strtod(text, &end);
    if (errno || end == text || *end) fail("invalid number");
    return value;
}

static Case *load_cases(const char *path, size_t *count_out)
{
    FILE *stream = fopen(path, "r");
    if (!stream) fail("cannot open cases");
    char line[LINE_CAPACITY]; size_t count = 0, capacity = 512;
    if (!fgets(line, sizeof(line), stream)) fail("cases are empty");
    Case *cases = calloc(capacity, sizeof(*cases));
    if (!cases) fail("allocation failed");
    while (fgets(line, sizeof(line), stream)) {
        line[strcspn(line, "\r\n")] = '\0';
        char *field[FIELD_COUNT];
        if (split(line, field) != FIELD_COUNT) fail("case width differs");
        if (!strcmp(field[1], "invalid") || !strcmp(field[1], "solver-boundary")) continue;
        if (count == capacity) {
            capacity *= 2;
            Case *grown = realloc(cases, capacity * sizeof(*grown));
            if (!grown) fail("allocation failed");
            cases = grown;
        }
        Case *item = &cases[count++];
        snprintf(item->cohort, sizeof(item->cohort), "%s", field[1]);
        item->year = (int)integer(field[2]); item->month = (int)integer(field[3]);
        item->day = (int)integer(field[4]); item->hour = (int)integer(field[5]);
        item->minute = (int)integer(field[6]); item->gmt = (int)integer(field[7]);
        item->avg = (int)integer(field[8]); item->lat = number(field[9]);
        item->lon = number(field[10]); item->solar = number(field[11]);
        item->pressure = number(field[12]); item->air = number(field[13]);
        item->rh = number(field[14]); item->wind = number(field[15]);
        item->height = number(field[16]); item->delta = number(field[17]);
        item->urban = (int)integer(field[18]);
    }
    if (ferror(stream) || fclose(stream)) fail("cannot read cases");
    if (!count) fail("no benchmark cases");
    *count_out = count;
    return cases;
}

static void pin_cpu(void)
{
#ifdef __linux__
    cpu_set_t available;
    if (sched_getaffinity(0, sizeof(available), &available) != 0) return;
    for (int cpu = 0; cpu < CPU_SETSIZE; ++cpu) if (CPU_ISSET(cpu, &available)) {
        cpu_set_t selected; CPU_ZERO(&selected); CPU_SET(cpu, &selected);
        (void)sched_setaffinity(0, sizeof(selected), &selected);
        return;
    }
#endif
}

static double now(void)
{
    struct timespec value;
#ifdef CLOCK_MONOTONIC_RAW
    const clockid_t clock_id = CLOCK_MONOTONIC_RAW;
#else
    const clockid_t clock_id = CLOCK_MONOTONIC;
#endif
    if (clock_gettime(clock_id, &value)) fail("clock failed");
    return value.tv_sec + value.tv_nsec * 1e-9;
}

static size_t exercise(const Case *cases, size_t count, const char *cohort,
                       long iterations)
{
    double checksum = 0.0; size_t calls = 0;
    for (long repeat = 0; repeat < iterations; ++repeat) {
        for (size_t index = 0; index < count; ++index) {
            const Case *item = &cases[index];
            if (cohort && strcmp(cohort, item->cohort)) continue;
            float estimated = 0, globe = 0, natural = 0, psychrometric = 0, wbgt = 0;
            int status = calc_wbgt(
                item->year, item->month, item->day, item->hour, item->minute,
                item->gmt, item->avg, item->lat, item->lon, item->solar,
                item->pressure, item->air, item->rh, item->wind, item->height,
                item->delta, item->urban, &estimated, &globe, &natural,
                &psychrometric, &wbgt
            );
            checksum += estimated + globe + natural + psychrometric + wbgt + status;
            ++calls;
        }
    }
    consumed_checksum += checksum;
    return calls;
}

static double measure(const Case *cases, size_t count, const char *cohort,
                      long iterations)
{
    (void)exercise(cases, count, cohort, 1);
    double start = now();
    size_t calls = exercise(cases, count, cohort, iterations);
    double elapsed = now() - start;
    return calls / elapsed;
}

int main(int argc, char **argv)
{
    if (argc != 3) fail("expected CASES.csv ITERATIONS");
    long iterations = integer(argv[2]);
    if (iterations < 1) fail("iterations must be positive");
    size_t count = 0; Case *cases = load_cases(argv[1], &count);
    Cohort cohorts[MAX_COHORTS]; size_t cohort_count = 0;
    for (size_t index = 0; index < count; ++index) {
        size_t found = 0;
        while (found < cohort_count && strcmp(cohorts[found].name, cases[index].cohort)) ++found;
        if (found == cohort_count) {
            if (cohort_count == MAX_COHORTS) fail("too many cohorts");
            snprintf(cohorts[cohort_count++].name, sizeof(cohorts[0].name), "%s", cases[index].cohort);
        }
    }
    pin_cpu();
    printf("{\"rows_per_second\":{\"overall\":%.17g", measure(cases, count, NULL, iterations));
    for (size_t index = 0; index < cohort_count; ++index)
        printf(",\"%s\":%.17g", cohorts[index].name,
               measure(cases, count, cohorts[index].name, iterations));
    printf("},\"checksum\":%.17g}\n", consumed_checksum);
    free(cases);
    return 0;
}
