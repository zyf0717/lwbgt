using LWBGT
using Test

const SINGAPORE = Input(
    year=2024,
    month=4,
    day=15,
    hour=14,
    minute=30,
    gmt_offset_hours=8,
    averaging_minutes=60,
    urban=1,
    latitude_deg_north=1.3521,
    longitude_deg_east=103.8198,
    solar_w_m2=742.0,
    pressure_hpa=1008.4,
    air_temperature_c=32.1,
    relative_humidity_percent=68.0,
    wind_speed_m_s=2.8,
    wind_height_m=10.0,
    vertical_temperature_difference_c=-0.4,
)

const SOLVER_FAILURE = Input(
    year=2024,
    month=3,
    day=20,
    hour=12,
    minute=0,
    gmt_offset_hours=0,
    averaging_minutes=0,
    urban=0,
    latitude_deg_north=0.0,
    longitude_deg_east=0.0,
    solar_w_m2=1000.0,
    pressure_hpa=300.0,
    air_temperature_c=60.0,
    relative_humidity_percent=100.0,
    wind_speed_m_s=0.129,
    wind_height_m=2.0,
    vertical_temperature_difference_c=0.0,
)

@testset "ABI records" begin
    @test isbitstype(Input)
    @test isbitstype(Result)
    @test sizeof(Input) == 104
    @test sizeof(Result) == 24
    @test SINGAPORE.year === Int32(2024)
    @test SINGAPORE.solar_w_m2 === 742.0
    @test_throws ErrorException setproperty!(SINGAPORE, :year, Int32(2023))
end

@testset "empty batch" begin
    @test calculate_batch(Input[]) == Result[]
    @test calculate_batch(()) == Result[]
end

@testset "concurrent first use" begin
    results = fetch.([Threads.@spawn(calculate(SINGAPORE)) for _ in 1:16])
    @test all(==(first(results)), results)
    @test first(results).status == 0
end

@testset "native FFI" begin
    result = calculate(SINGAPORE)
    @test result.status == 0
    # Golden values permit a few binary32 ULPs across platform math libraries.
    @test isapprox(result.wbgt_c, reinterpret(Float32, 0x42020259); rtol=4eps(Float32))
    batch = calculate_batch((SINGAPORE, SOLVER_FAILURE))
    @test batch[1] == result
    @test batch[2].status == -1
    @test batch[2].globe_temperature_c == -9999.0f0
    @test calculate([SINGAPORE]) == [result]
    @test isapprox(esat(273.15), reinterpret(Float32, 0x40c45e95); rtol=4eps(Float32))
    @test isapprox(esat(273.15, 1), reinterpret(Float32, 0x40c459a5); rtol=4eps(Float32))
    @test esat(273.15; phase=1) == esat(273.15, 1)
    before = [SINGAPORE, SOLVER_FAILURE]
    @test calculate_batch(before) == [calculate(record) for record in before]
    @test before == [SINGAPORE, SOLVER_FAILURE]
    withenv("LWBGT_LIBRARY" => joinpath(@__DIR__, "does-not-exist")) do
        @test_throws ErrorException LWBGT._library_path()
    end
end

# CI provides output from the C probe built alongside the shipped library.
# An installed package remains independently testable without repository files.
if haskey(ENV, "LWBGT_CASES") || haskey(ENV, "LWBGT_EXPECTED")
    include("corpus.jl")
end
