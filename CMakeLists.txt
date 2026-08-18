cmake_minimum_required(VERSION 3.16)
project(lwbgt VERSION 0.2.0 LANGUAGES C)

include(CTest)
include(GNUInstallDirs)
include(CMakePackageConfigHelpers)

option(LWBGT_BUILD_BINDING_TESTS "Build tests for the Python, R, and Julia examples" ON)
option(LWBGT_REQUIRE_ALL_BINDING_TESTS "Fail if a binding-test runtime is unavailable" OFF)

if(NOT CMAKE_C_COMPILER_ID MATCHES "GNU|Clang")
    message(FATAL_ERROR
        "lwbgt requires GCC, Clang, AppleClang, or MinGW GCC; MSVC cannot compile the preserved GNU89 source"
    )
endif()

set(LWBGT_FP_OPTIONS
    -O2
    -fno-fast-math
    -ffp-contract=off
    -fno-strict-aliasing
)
set(LWBGT_LEGACY_OPTIONS
    -std=gnu89
    -Wno-implicit-int
    -Wno-implicit-function-declaration
)

set_source_files_properties(src/wbgt.c PROPERTIES
    LANGUAGE C
    COMPILE_DEFINITIONS "main=lwbgt_original_demo_main"
)
add_library(lwbgt_core OBJECT src/wbgt.c)
target_compile_options(lwbgt_core PRIVATE ${LWBGT_FP_OPTIONS} ${LWBGT_LEGACY_OPTIONS})
set_target_properties(lwbgt_core PROPERTIES POSITION_INDEPENDENT_CODE ON)

add_library(lwbgt_ffi OBJECT src/lwbgt_ffi.c)
target_compile_features(lwbgt_ffi PRIVATE c_std_11)
target_compile_options(lwbgt_ffi PRIVATE ${LWBGT_FP_OPTIONS} -Wall -Wextra -Werror)
target_include_directories(lwbgt_ffi PRIVATE include)
set_target_properties(lwbgt_ffi PROPERTIES POSITION_INDEPENDENT_CODE ON)

set(LWBGT_OBJECTS
    $<TARGET_OBJECTS:lwbgt_core>
    $<TARGET_OBJECTS:lwbgt_ffi>
)

add_library(lwbgt STATIC ${LWBGT_OBJECTS})
add_library(lwbgt_shared SHARED ${LWBGT_OBJECTS})
set_target_properties(lwbgt PROPERTIES EXPORT_NAME static)
set_target_properties(lwbgt_shared PROPERTIES
    EXPORT_NAME shared
    OUTPUT_NAME lwbgt
    VERSION ${PROJECT_VERSION}
    SOVERSION ${PROJECT_VERSION_MAJOR}
)
if(WIN32)
    set_target_properties(lwbgt_shared PROPERTIES ARCHIVE_OUTPUT_NAME lwbgt_dll)
    target_sources(lwbgt_shared PRIVATE cmake/lwbgt.def)
elseif(APPLE)
    target_link_options(lwbgt_shared PRIVATE
        "LINKER:-exported_symbols_list,${CMAKE_CURRENT_SOURCE_DIR}/cmake/lwbgt.exports"
    )
elseif(UNIX)
    target_link_options(lwbgt_shared PRIVATE
        "LINKER:--version-script=${CMAKE_CURRENT_SOURCE_DIR}/cmake/lwbgt.map"
    )
endif()

foreach(target lwbgt lwbgt_shared)
    target_include_directories(${target} PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
    )
endforeach()
target_link_libraries(lwbgt PUBLIC m)
target_link_libraries(lwbgt_shared PRIVATE m)

if(BUILD_TESTING)
    find_package(Python3 REQUIRED COMPONENTS Interpreter)

    set_source_files_properties(upstream/wbgt.c.original PROPERTIES
        LANGUAGE C
        COMPILE_DEFINITIONS "main=lwbgt_reference_demo_main"
    )
    add_library(lwbgt_reference STATIC upstream/wbgt.c.original)
    target_compile_options(lwbgt_reference PRIVATE
        -x c ${LWBGT_FP_OPTIONS} ${LWBGT_LEGACY_OPTIONS}
    )
    target_link_libraries(lwbgt_reference PUBLIC m)

    function(lwbgt_add_harness target source core)
        add_executable(${target} ${source})
        target_compile_options(${target} PRIVATE
            -std=c11 ${LWBGT_FP_OPTIONS} -Wall -Wextra -Werror
        )
        target_include_directories(${target} PRIVATE include)
        target_link_libraries(${target} PRIVATE ${core} m)
    endfunction()

    lwbgt_add_harness(lwbgt_probe tests/probe.c lwbgt)
    lwbgt_add_harness(lwbgt_reference_probe tests/probe.c lwbgt_reference)
    lwbgt_add_harness(lwbgt_benchmark benchmarks/benchmark.c lwbgt)
    lwbgt_add_harness(lwbgt_reference_benchmark benchmarks/benchmark.c lwbgt_reference)
    lwbgt_add_harness(lwbgt_batch_test tests/batch.c lwbgt)

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

    add_test(NAME batch_equivalence COMMAND lwbgt_batch_test "${LWBGT_CASES}")
    set_tests_properties(batch_equivalence PROPERTIES DEPENDS generate_cases)

    add_test(
        NAME shared_exports
        COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/tests/check_exports.py"
                "${CMAKE_SYSTEM_NAME}" "$<TARGET_FILE:lwbgt_shared>"
                "${CMAKE_NM}" "${CMAKE_OBJDUMP}"
    )

    if(LWBGT_BUILD_BINDING_TESTS)
        find_program(LWBGT_R_EXECUTABLE NAMES R)
        find_program(LWBGT_RSCRIPT_EXECUTABLE NAMES Rscript)
        find_program(LWBGT_JULIA_EXECUTABLE NAMES julia)
        if(LWBGT_REQUIRE_ALL_BINDING_TESTS AND
           (NOT LWBGT_R_EXECUTABLE OR NOT LWBGT_RSCRIPT_EXECUTABLE OR NOT LWBGT_JULIA_EXECUTABLE))
            message(FATAL_ERROR "Python, R, Rscript, and Julia are required for binding tests")
        endif()

        add_test(
            NAME python_binding_example
            COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/examples/python/example.py"
                    "$<TARGET_FILE:lwbgt_shared>"
        )

        if(LWBGT_JULIA_EXECUTABLE)
            add_test(
                NAME julia_binding_example
                COMMAND "${LWBGT_JULIA_EXECUTABLE}"
                        "${CMAKE_CURRENT_SOURCE_DIR}/examples/julia/example.jl"
                        "$<TARGET_FILE:lwbgt_shared>"
            )
        else()
            message(STATUS "Julia not found; skipping the Julia binding example")
        endif()

        if(LWBGT_R_EXECUTABLE AND LWBGT_RSCRIPT_EXECUTABLE)
            execute_process(
                COMMAND "${LWBGT_R_EXECUTABLE}" CMD config --cppflags
                OUTPUT_VARIABLE LWBGT_R_CPPFLAGS
                OUTPUT_STRIP_TRAILING_WHITESPACE
                RESULT_VARIABLE LWBGT_R_CPPFLAGS_RESULT
            )
            execute_process(
                COMMAND "${LWBGT_R_EXECUTABLE}" CMD config --ldflags
                OUTPUT_VARIABLE LWBGT_R_LDFLAGS
                OUTPUT_STRIP_TRAILING_WHITESPACE
                RESULT_VARIABLE LWBGT_R_LDFLAGS_RESULT
            )
            if(NOT LWBGT_R_CPPFLAGS_RESULT EQUAL 0 OR NOT LWBGT_R_LDFLAGS_RESULT EQUAL 0)
                message(FATAL_ERROR "R CMD config failed while preparing the R binding example")
            endif()
            separate_arguments(LWBGT_R_CPPFLAGS_LIST NATIVE_COMMAND "${LWBGT_R_CPPFLAGS}")
            separate_arguments(LWBGT_R_LDFLAGS_LIST NATIVE_COMMAND "${LWBGT_R_LDFLAGS}")

            add_library(lwbgt_r_example MODULE examples/r/lwbgt_r.c)
            target_compile_features(lwbgt_r_example PRIVATE c_std_11)
            target_compile_options(lwbgt_r_example PRIVATE ${LWBGT_R_CPPFLAGS_LIST})
            target_link_options(lwbgt_r_example PRIVATE ${LWBGT_R_LDFLAGS_LIST})
            target_link_libraries(lwbgt_r_example PRIVATE lwbgt_shared)
            set_target_properties(lwbgt_r_example PROPERTIES
                PREFIX ""
                OUTPUT_NAME lwbgt_r_example
            )
            if(WIN32)
                set_target_properties(lwbgt_r_example PROPERTIES WINDOWS_EXPORT_ALL_SYMBOLS ON)
            endif()
            add_test(
                NAME r_binding_example
                COMMAND "${LWBGT_RSCRIPT_EXECUTABLE}"
                        "${CMAKE_CURRENT_SOURCE_DIR}/examples/r/example.R"
                        "$<TARGET_FILE:lwbgt_r_example>"
            )
            set_tests_properties(r_binding_example PROPERTIES
                WORKING_DIRECTORY "$<TARGET_FILE_DIR:lwbgt_shared>"
            )
        else()
            message(STATUS "R not found; skipping the R binding example")
        endif()
    endif()

    add_test(
        NAME installed_consumer
        COMMAND "${CMAKE_COMMAND}"
                -DBUILD_DIR=${CMAKE_CURRENT_BINARY_DIR}
                -DSOURCE_DIR=${CMAKE_CURRENT_SOURCE_DIR}/tests/consumer
                -DINSTALL_DIR=${CMAKE_CURRENT_BINARY_DIR}/test-install
                -DCONFIG=$<CONFIG>
                -DEXECUTABLE_SUFFIX=${CMAKE_EXECUTABLE_SUFFIX}
                -DINSTALL_BINDIR=${CMAKE_INSTALL_BINDIR}
                -DINSTALL_LIBDIR=${CMAKE_INSTALL_LIBDIR}
                -DSYSTEM_NAME=${CMAKE_SYSTEM_NAME}
                "-DGENERATOR=${CMAKE_GENERATOR}"
                -P "${CMAKE_CURRENT_SOURCE_DIR}/tests/test_install.cmake"
    )
endif()

configure_package_config_file(
    cmake/lwbgtConfig.cmake.in
    "${CMAKE_CURRENT_BINARY_DIR}/lwbgtConfig.cmake"
    INSTALL_DESTINATION "${CMAKE_INSTALL_LIBDIR}/cmake/lwbgt"
)
write_basic_package_version_file(
    "${CMAKE_CURRENT_BINARY_DIR}/lwbgtConfigVersion.cmake"
    VERSION ${PROJECT_VERSION}
    COMPATIBILITY SameMinorVersion
)
configure_file(cmake/lwbgt.pc.in "${CMAKE_CURRENT_BINARY_DIR}/lwbgt.pc" @ONLY)

install(TARGETS lwbgt lwbgt_shared
    EXPORT lwbgtTargets
    ARCHIVE DESTINATION "${CMAKE_INSTALL_LIBDIR}"
    LIBRARY DESTINATION "${CMAKE_INSTALL_LIBDIR}"
    RUNTIME DESTINATION "${CMAKE_INSTALL_BINDIR}"
)
install(FILES include/lwbgt.h DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}")
install(EXPORT lwbgtTargets
    FILE lwbgtTargets.cmake
    NAMESPACE lwbgt::
    DESTINATION "${CMAKE_INSTALL_LIBDIR}/cmake/lwbgt"
)
install(FILES
    "${CMAKE_CURRENT_BINARY_DIR}/lwbgtConfig.cmake"
    "${CMAKE_CURRENT_BINARY_DIR}/lwbgtConfigVersion.cmake"
    DESTINATION "${CMAKE_INSTALL_LIBDIR}/cmake/lwbgt"
)
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/lwbgt.pc"
    DESTINATION "${CMAKE_INSTALL_LIBDIR}/pkgconfig"
)
install(FILES NOTICE LICENSES/LicenseRef-UChicago-Argonne-WBGT-1.1.txt
    DESTINATION "${CMAKE_INSTALL_DATAROOTDIR}/doc/lwbgt"
)
