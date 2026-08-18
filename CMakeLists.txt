cmake_minimum_required(VERSION 3.16)
project(lwbgt VERSION 0.1.0 LANGUAGES C)

include(CTest)
find_package(Python3 REQUIRED COMPONENTS Interpreter)

set(LWBGT_FP_OPTIONS
    -std=gnu89
    -O2
    -fno-fast-math
    -ffp-contract=off
    -fno-strict-aliasing
)
set(LWBGT_LEGACY_WARNINGS
    -Wno-implicit-int
    -Wno-implicit-function-declaration
)

set_source_files_properties(src/wbgt.c PROPERTIES
    LANGUAGE C
    COMPILE_DEFINITIONS "main=lwbgt_original_demo_main"
)
add_library(lwbgt STATIC src/wbgt.c)
target_compile_options(lwbgt PRIVATE ${LWBGT_FP_OPTIONS} ${LWBGT_LEGACY_WARNINGS})
target_include_directories(lwbgt PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)
target_link_libraries(lwbgt PUBLIC m)

set_source_files_properties(upstream/wbgt.c.original PROPERTIES
    LANGUAGE C
    COMPILE_DEFINITIONS "main=lwbgt_reference_demo_main"
)
add_library(lwbgt_reference STATIC upstream/wbgt.c.original)
target_compile_options(lwbgt_reference PRIVATE
    -x c ${LWBGT_FP_OPTIONS} ${LWBGT_LEGACY_WARNINGS}
)
target_link_libraries(lwbgt_reference PUBLIC m)

function(lwbgt_add_harness target source core)
    add_executable(${target} ${source})
    target_compile_options(${target} PRIVATE
        -std=c11 -O2 -fno-fast-math -ffp-contract=off -Wall -Wextra -Werror
    )
    target_include_directories(${target} PRIVATE include)
    target_link_libraries(${target} PRIVATE ${core} m)
endfunction()

lwbgt_add_harness(lwbgt_probe tests/probe.c lwbgt)
lwbgt_add_harness(lwbgt_reference_probe tests/probe.c lwbgt_reference)
lwbgt_add_harness(lwbgt_benchmark benchmarks/benchmark.c lwbgt)
lwbgt_add_harness(lwbgt_reference_benchmark benchmarks/benchmark.c lwbgt_reference)

set(LWBGT_CASES "${CMAKE_CURRENT_BINARY_DIR}/cases.csv")
add_test(
    NAME generate_cases
    COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/tests/generate_cases.py"
            "${LWBGT_CASES}"
)
add_test(
    NAME exact_equivalence
    COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/tests/compare.py"
            exact "$<TARGET_FILE:lwbgt_reference_probe>" "$<TARGET_FILE:lwbgt_probe>"
            "${LWBGT_CASES}"
)
set_tests_properties(exact_equivalence PROPERTIES DEPENDS generate_cases)

install(TARGETS lwbgt ARCHIVE DESTINATION lib)
install(FILES include/lwbgt.h DESTINATION include)
