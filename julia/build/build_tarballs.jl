using BinaryBuilder, TOML

# CI supplies a clean git archive, so untracked files cannot enter a release.
source = abspath(ENV["LWBGT_SOURCE_DIR"])
version = VersionNumber(TOML.parsefile(joinpath(source, "julia", "Project.toml"))["version"])
sources = [DirectorySource(source; target="lwbgt")]

script = raw"""
cd ${WORKSPACE}/srcdir/lwbgt
cmake -B build \
    -DCMAKE_INSTALL_PREFIX=${prefix} \
    -DCMAKE_TOOLCHAIN_FILE=${CMAKE_TARGET_TOOLCHAIN} \
    -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=OFF
cmake --build build --parallel ${nproc}
cmake --install build
install_license LICENSE NOTICE src/LicenseRef-UChicago-Argonne-WBGT-1.1.txt

# CI-only probes: same compiler and floating-point settings as the library.
# artifacts.jl removes these executables from the published runtime archives.
fp=(-O2 -fno-fast-math -ffp-contract=off -fno-strict-aliasing)
runtime=()
if [[ ${target} == *mingw* ]]; then
    runtime=(-static-libgcc)
fi
${CC} "${fp[@]}" -std=gnu89 -Wno-implicit-int -Wno-implicit-function-declaration \
    -Dmain=lwbgt_reference_demo_main -x c -c upstream/wbgt.c.original -o reference.o
mkdir -p ${bindir}
for probe in probe esat_probe; do
    ${CC} "${fp[@]}" -std=c11 -D__USE_MINGW_ANSI_STDIO=1 -Iinclude tests/${probe}.c build/liblwbgt.a \
        -lm "${runtime[@]}" -o ${bindir}/lwbgt_${probe}${exeext}
    ${CC} "${fp[@]}" -std=c11 -D__USE_MINGW_ANSI_STDIO=1 -Iinclude tests/${probe}.c reference.o \
        -lm "${runtime[@]}" -o ${bindir}/lwbgt_reference_${probe}${exeext}
done
"""

platforms = [
    Platform("x86_64", "linux"; libc="glibc"),
    Platform("aarch64", "linux"; libc="glibc"),
    Platform("x86_64", "macos"),
    Platform("aarch64", "macos"),
    Platform("x86_64", "windows"),
]

build_tarballs(ARGS, "lwbgt", version, sources, script, platforms,
    [LibraryProduct(["liblwbgt", "lwbgt"], :liblwbgt)], Dependency[];
    julia_compat="1.10", ignore_audit_errors=false)
