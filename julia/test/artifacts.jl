# Exercise a standalone package copy, real downloads, precompilation, and reloads.
# The Python runner supplies a local HTTP server before publication.
using TOML, Pkg.Artifacts, Test
using Base.BinaryPlatforms

package, manifest, base_url = ARGS
cp(manifest, joinpath(package, "Artifacts.toml"); force=true)
entries = TOML.parsefile(joinpath(package, "Artifacts.toml"))
for meta in entries["lwbgt"], download in meta["download"]
    download["url"] = base_url * "/" * split(download["url"], '/')[end]
end
open(joinpath(package, "Artifacts.toml"), "w") do io
    TOML.print(io, entries; sorted=true)
end

# Fail loudly rather than attempting a system-library fallback.
manifest_path = joinpath(package, "Artifacts.toml")
@test artifact_hash("lwbgt", manifest_path; platform=Platform("i686", "linux")) === nothing

command = `$(Base.julia_cmd()) --startup-file=no --project=$package`
run(`$command -e 'using LWBGT; include(joinpath(pkgdir(LWBGT), "test", "runtests.jl"))'`)
# A fresh process must resolve the artifact again, not reuse serialized pointers.
run(`$command -e 'using LWBGT; @assert LWBGT.esat(273.15) > 0'`)

# With no cached library, Julia must reject an archive with the wrong checksum.
for meta in entries["lwbgt"], download in meta["download"]
    download["sha256"] = repeat("0", 64)
end
open(manifest_path, "w") do io
    TOML.print(io, entries; sorted=true)
end
mktempdir() do depot
    output = IOBuffer()
    process = run(pipeline(ignorestatus(addenv(
        `$command -e 'using LWBGT; LWBGT.esat(273.15)'`, "JULIA_DEPOT_PATH" => depot,
    )); stdout=output, stderr=output))
    @test !success(process)
    @test occursin("sha256", lowercase(String(take!(output))))
end
