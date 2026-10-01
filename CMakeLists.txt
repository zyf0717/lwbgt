cmake_minimum_required(VERSION 3.16)
project(lwbgt VERSION 1.0.1 LANGUAGES C)

include(CTest)
include(GNUInstallDirs)
include(CMakePackageConfigHelpers)

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
add_library(lwbgt_python SHARED ${LWBGT_OBJECTS})
set_target_properties(lwbgt PROPERTIES EXPORT_NAME static)
set_target_properties(lwbgt_shared PROPERTIES
    EXPORT_NAME shared
    OUTPUT_NAME lwbgt
    VERSION ${PROJECT_VERSION}
    # The C ABI is unchanged by the package's 1.0 release.
    SOVERSION 0
)
set_target_properties(lwbgt_python PROPERTIES
    OUTPUT_NAME lwbgt
    LIBRARY_OUTPUT_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/python-runtime"
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/python-runtime"
    ARCHIVE_OUTPUT_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/python-runtime"
)

function(lwbgt_restrict_shared_exports target)
    if(WIN32)
        set_target_properties(${target} PROPERTIES PREFIX "")
        target_sources(${target} PRIVATE cmake/lwbgt.def)
    elseif(APPLE)
        target_link_options(${target} PRIVATE
            "LINKER:-exported_symbols_list,${CMAKE_CURRENT_SOURCE_DIR}/cmake/lwbgt.exports"
        )
    elseif(UNIX)
        target_link_options(${target} PRIVATE
            "LINKER:--version-script=${CMAKE_CURRENT_SOURCE_DIR}/cmake/lwbgt.map"
        )
    endif()
endfunction()

if(WIN32)
    set_target_properties(lwbgt_shared PROPERTIES ARCHIVE_OUTPUT_NAME lwbgt_dll)
endif()
lwbgt_restrict_shared_exports(lwbgt_shared)
lwbgt_restrict_shared_exports(lwbgt_python)

foreach(target lwbgt lwbgt_shared)
    target_include_directories(${target} PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
    )
endforeach()
target_link_libraries(lwbgt PUBLIC m)
target_link_libraries(lwbgt_shared PRIVATE m)
target_link_libraries(lwbgt_python PRIVATE m)
if(MINGW)
    target_link_options(lwbgt_python PRIVATE -static-libgcc)
endif()

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
    lwbgt_add_harness(lwbgt_python_probe tests/probe.c lwbgt_python)
    if(WIN32)
        set_target_properties(lwbgt_python_probe PROPERTIES
            RUNTIME_OUTPUT_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/python-runtime"
        )
    endif()
    lwbgt_add_harness(lwbgt_reference_probe tests/probe.c lwbgt_reference)
    lwbgt_add_harness(lwbgt_esat_probe tests/esat_probe.c lwbgt)
    lwbgt_add_harness(lwbgt_python_esat_probe tests/esat_probe.c lwbgt_python)
    lwbgt_add_harness(lwbgt_reference_esat_probe tests/esat_probe.c lwbgt_reference)
    lwbgt_add_harness(lwbgt_branch_probe tests/branch_probe.c lwbgt)
    lwbgt_add_harness(lwbgt_reference_branch_probe tests/branch_probe.c lwbgt_reference)
    target_compile_definitions(lwbgt_reference_branch_probe PRIVATE LWBGT_REFERENCE)
    add_test(
        NAME internal_branch_equivalence
        COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/tests/compare.py"
                exact "$<TARGET_FILE:lwbgt_reference_branch_probe>" "$<TARGET_FILE:lwbgt_branch_probe>"
    )
    if(WIN32)
        set_target_properties(lwbgt_python_esat_probe PROPERTIES
            RUNTIME_OUTPUT_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/python-runtime"
        )
    endif()
    lwbgt_add_harness(lwbgt_benchmark benchmarks/benchmark.c lwbgt)
    lwbgt_add_harness(lwbgt_reference_benchmark benchmarks/benchmark.c lwbgt_reference)
    lwbgt_add_harness(lwbgt_batch_test tests/batch.c lwbgt)
    add_executable(lwbgt_demo src/wbgt.c)
    target_compile_definitions(lwbgt_demo PRIVATE LWBGT_BUILD_DEMO)
    target_compile_options(lwbgt_demo PRIVATE ${LWBGT_FP_OPTIONS} ${LWBGT_LEGACY_OPTIONS})
    target_link_libraries(lwbgt_demo PRIVATE m)

    set(LWBGT_CASES "${CMAKE_CURRENT_BINARY_DIR}/cases.csv")
    set(LWBGT_ESAT_CASES "${CMAKE_CURRENT_BINARY_DIR}/esat-cases.csv")
    set(LWBGT_WEATHER_CASES "${CMAKE_CURRENT_BINARY_DIR}/weather-cases.csv")
    add_test(
        NAME generate_cases
        COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/tests/generate_cases.py"
                "${LWBGT_CASES}" --esat-output "${LWBGT_ESAT_CASES}"
                --weather-output "${LWBGT_WEATHER_CASES}"
    )
    add_test(
        NAME r_source_sync
        COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/tests/check_r_sources.py"
    )
    add_test(
        NAME compatibility_equivalence
        COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/tests/compare.py"
                compat "$<TARGET_FILE:lwbgt_reference_probe>" "$<TARGET_FILE:lwbgt_probe>"
                "${LWBGT_CASES}"
    )
    set_tests_properties(compatibility_equivalence PROPERTIES DEPENDS generate_cases)
    add_test(
        NAME python_runtime_compatibility_equivalence
        COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/tests/compare.py"
                compat "$<TARGET_FILE:lwbgt_reference_probe>" "$<TARGET_FILE:lwbgt_python_probe>"
                "${LWBGT_CASES}"
    )
    set_tests_properties(python_runtime_compatibility_equivalence PROPERTIES DEPENDS generate_cases)

    add_test(NAME batch_equivalence COMMAND lwbgt_batch_test "${LWBGT_CASES}")
    set_tests_properties(batch_equivalence PROPERTIES DEPENDS generate_cases)
    foreach(runtime IN ITEMS native python_runtime)
        if(runtime STREQUAL "native")
            set(esat_probe lwbgt_esat_probe)
        else()
            set(esat_probe lwbgt_python_esat_probe)
        endif()
        add_test(
            NAME ${runtime}_esat_equivalence
            COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/tests/compare.py"
                    exact "$<TARGET_FILE:lwbgt_reference_esat_probe>" "$<TARGET_FILE:${esat_probe}>"
                    "${LWBGT_ESAT_CASES}"
        )
        set_tests_properties(${runtime}_esat_equivalence
            PROPERTIES DEPENDS generate_cases)
    endforeach()
    add_test(NAME invalid_weather_batch_equivalence COMMAND lwbgt_batch_test "${LWBGT_WEATHER_CASES}")
    set_tests_properties(invalid_weather_batch_equivalence PROPERTIES DEPENDS generate_cases)
    add_test(
        NAME benchmark_accounting
        COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/tests/check_benchmark.py"
                "$<TARGET_FILE:lwbgt_reference_benchmark>" "$<TARGET_FILE:lwbgt_benchmark>"
    )
    add_test(
        NAME demo_smoke
        COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/tests/check_demo.py"
                "$<TARGET_FILE:lwbgt_demo>"
    )

    add_test(
        NAME shared_exports
        COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/tests/check_exports.py"
                "${CMAKE_SYSTEM_NAME}" "$<TARGET_FILE:lwbgt_shared>"
                "${CMAKE_NM}" "${CMAKE_OBJDUMP}"
    )
    add_test(
        NAME python_runtime_exports
        COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/tests/check_exports.py"
                "${CMAKE_SYSTEM_NAME}" "$<TARGET_FILE:lwbgt_python>"
                "${CMAKE_NM}" "${CMAKE_OBJDUMP}"
    )

    add_test(
        NAME installed_consumer
        COMMAND "${CMAKE_COMMAND}"
                -DBUILD_DIR=${CMAKE_CURRENT_BINARY_DIR}
                -DSOURCE_DIR=${CMAKE_CURRENT_SOURCE_DIR}/tests/consumer
                -DINSTALL_DIR=${CMAKE_CURRENT_BINARY_DIR}/test-install
                -DCONFIG=$<CONFIG>
                -DEXECUTABLE_SUFFIX=${CMAKE_EXECUTABLE_SUFFIX}
                -DINSTALL_BINDIR=${CMAKE_INSTALL_BINDIR}
                -DINSTALL_DATADIR=${CMAKE_INSTALL_DATAROOTDIR}
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
install(TARGETS lwbgt_python EXCLUDE_FROM_ALL
    LIBRARY DESTINATION lwbgt COMPONENT python
    RUNTIME DESTINATION lwbgt COMPONENT python
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
install(FILES
    LICENSE
    docs/ABI.md
    docs/INPUTS.md
    NOTICE
    LICENSES/LicenseRef-UChicago-Argonne-WBGT-1.1.txt
    DESTINATION "${CMAKE_INSTALL_DATAROOTDIR}/doc/lwbgt"
)
