using Test
include("../build/artifacts.jl")

@testset "prepared source identity" begin
    mktempdir() do root
        git = `git -C $root -c user.name=Test -c user.email=test@example.invalid -c commit.gpgsign=false`
        run(`$git init -q`)
        write(joinpath(root, "kernel.c"), "source")
        run(`$git add .`)
        run(`$git commit -qm source`)
        original = source_tree(root)
        mkpath(joinpath(root, "julia"))
        for path in GENERATED
            write(joinpath(root, path), "generated metadata")
        end
        run(`$git add .`)
        run(`$git commit -qm metadata`)
        @test source_tree(root) == original
        write(joinpath(root, "kernel.c"), "changed source")
        run(`$git commit -qam change`)
        @test source_tree(root) != original
    end
end

@testset "release archive identity" begin
    mktempdir() do work
        products, output = joinpath(work, "products"), joinpath(work, "native")
        mkpath(products)
        for target in TARGETS
            hash = create_artifact() do root
                mkpath(joinpath(root, "lib"))
                write(joinpath(root, "lib", "fixture"), target)
                mkpath(joinpath(root, "bin"))
                for name in ("probe", "esat_probe", "reference_probe", "reference_esat_probe")
                    write(joinpath(root, "bin", "lwbgt_" * name * (occursin("mingw", target) ? ".exe" : "")), "probe")
                end
            end
            archive_artifact(hash, joinpath(products, "lwbgt.v$(version()).$(target).tar.gz"))
        end
        withenv("GITHUB_RUN_ID" => "123") do
            prepare(products, output)
        end
        manifest, provenance = joinpath(output, "Artifacts.toml"), joinpath(output, "native-build.toml")
        @test verify(output, manifest, provenance) === nothing
        for target in TARGETS
            hash = artifact_hash("lwbgt", manifest; platform=parse(Platform, target))
            @test read(joinpath(artifact_path(hash), "lib", "fixture"), String) == target
            @test isempty(readdir(joinpath(artifact_path(hash), "bin")))
        end
        metadata = TOML.parsefile(provenance)
        open(provenance, "w") do io
            TOML.print(io, merge(metadata, Dict("source_tree" => "stale")))
        end
        @test_throws ErrorException verify(output, manifest, provenance)
        open(provenance, "w") do io
            TOML.print(io, metadata)
        end
        first_archive = joinpath(output, asset_name(first(TARGETS)))
        open(first_archive, "a") do io
            write(io, "corrupt")
        end
        @test_throws ErrorException verify(output, manifest, provenance)
        rm(first_archive)
        @test_throws SystemError verify(output, manifest, provenance)
    end
end
