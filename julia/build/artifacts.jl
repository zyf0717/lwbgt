# Build metadata for the exact archives that the release workflow will publish.
# Run with Julia's default environment; this uses only standard libraries.
using Pkg.Artifacts, Pkg.PlatformEngines, SHA, TOML
using Base.BinaryPlatforms

const TARGETS = ["x86_64-linux-gnu", "aarch64-linux-gnu", "x86_64-apple-darwin",
                 "aarch64-apple-darwin", "x86_64-w64-mingw32"]
const ROOT = normpath(joinpath(@__DIR__, "..", ".."))
const GENERATED = ["julia/Artifacts.toml", "julia/native-build.toml"]

version() = TOML.parsefile(joinpath(ROOT, "julia", "Project.toml"))["version"]
digest(path) = bytes2hex(open(sha256, path))
asset_name(target) = "lwbgt-v$(version())-$(target).tar.gz"
asset_url(target) = "https://github.com/zyf0717/lwbgt/releases/download/v$(version())/$(asset_name(target))"

function source_tree(root=ROOT)
    # Compare the entire tracked tree except the output of this preparation step.
    entries = split(read(`git -C $root ls-tree -rz HEAD`, String), '\0'; keepempty=false)
    filter!(entry -> last(split(entry, '\t'; limit=2)) ∉ GENERATED, entries)
    return bytes2hex(sha256(join(entries, '\0')))
end

function raw_archive(directory, target)
    name = "lwbgt.v$(version()).$(target).tar.gz"
    path = joinpath(directory, name)
    isfile(path) || error("missing BinaryBuilder archive: $path")
    return path
end

function prepare(products, output)
    mkpath(output)
    manifest = joinpath(output, "Artifacts.toml")
    isfile(manifest) && rm(manifest)
    for target in TARGETS
        hash = create_artifact() do staging
            unpack(raw_archive(products, target), staging)
            for name in ("probe", "esat_probe", "reference_probe", "reference_esat_probe")
                rm(joinpath(staging, "bin", "lwbgt_" * name * (occursin("mingw", target) ? ".exe" : "")))
            end
        end
        archive = joinpath(output, asset_name(target))
        checksum = archive_artifact(hash, archive)
        bind_artifact!(manifest, "lwbgt", hash; platform=parse(Platform, target),
                       download_info=[(asset_url(target), checksum)], lazy=true)
    end
    metadata = Dict("version" => version(), "source_tree" => source_tree(),
                    "source_commit" => readchomp(`git -C $ROOT rev-parse HEAD`),
                    "run_id" => ENV["GITHUB_RUN_ID"])
    open(joinpath(output, "native-build.toml"), "w") do io
        TOML.print(io, metadata; sorted=true)
    end
end

function verify(directory, manifest=joinpath(ROOT, "julia", "Artifacts.toml"),
                provenance=joinpath(ROOT, "julia", "native-build.toml"))
    metadata = TOML.parsefile(provenance)
    metadata["version"] == version() || error("prepared native version differs")
    metadata["source_tree"] == source_tree() || error("source changed since native preparation; prepare again before tagging")
    entries = TOML.parsefile(manifest)["lwbgt"]
    length(entries) == length(TARGETS) || error("expected all five native platforms")
    for target in TARGETS
        meta = artifact_meta("lwbgt", manifest; platform=parse(Platform, target))
        meta === nothing && error("missing platform: $target")
        only(meta["download"])["url"] == asset_url(target) || error("unexpected release URL")
        archive = joinpath(directory, asset_name(target))
        digest(archive) == only(meta["download"])["sha256"] || error("archive checksum differs: $target")
        mktempdir() do staging
            unpack(archive, staging)
            hash = create_artifact() do destination
                for file in readdir(staging)
                    cp(joinpath(staging, file), joinpath(destination, file); follow_symlinks=false)
                end
            end
            string(hash) == meta["git-tree-sha1"] || error("artifact tree differs: $target")
        end
    end
    println("Prepared native archives: version, source, platforms, and hashes verified")
end

if abspath(PROGRAM_FILE) == @__FILE__
    if length(ARGS) == 3 && ARGS[1] == "prepare"
        prepare(ARGS[2], ARGS[3])
    elseif length(ARGS) == 2 && ARGS[1] == "verify"
        verify(ARGS[2])
    else
        error("usage: artifacts.jl prepare PRODUCTS OUTPUT | verify ARCHIVES")
    end
end
