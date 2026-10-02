function read_inputs(path)
    return map(readlines(path)[2:end]) do line
        row = split(line, ',')
        # CSV starts with case_id, cohort; the native struct puts urban before doubles.
        Input(parse.(Int32, row[3:9])..., parse(Int32, row[19]),
              parse.(Float64, row[10:18])...)
    end
end

bits(result) = reinterpret(UInt32, Float32[getfield(result, i) for i in 2:6])

@testset "shared numerical corpus" begin
    inputs = read_inputs(ENV["LWBGT_CASES"])
    expected = readlines(ENV["LWBGT_EXPECTED"])[2:end]
    @test length(expected) == length(inputs)
    results = calculate_batch(inputs)
    for (input, result, line) in zip(inputs, results, expected)
        row = split(line, ',')
        @test result.status == parse(Int32, row[2])
        @test bits(result) == parse.(UInt32, row[3:7]; base=16)
        @test reinterpret(UInt32, esat(input.air_temperature_c + 273.15)) == parse(UInt32, row[8]; base=16)
        scalar = calculate(input)
        @test scalar.status == result.status
        @test bits(scalar) == bits(result)
    end
end

if haskey(ENV, "LWBGT_WEATHER_CASES")
    @testset "non-finite weather API consistency" begin
        inputs = read_inputs(ENV["LWBGT_WEATHER_CASES"])
        for (input, result) in zip(inputs, calculate_batch(inputs))
            scalar = calculate(input)
            @test scalar.status == result.status
            @test bits(scalar) == bits(result)
        end
    end
end

if haskey(ENV, "LWBGT_ESAT_EXPECTED")
    @testset "saturation-pressure corpus" begin
        cases = readlines(ENV["LWBGT_ESAT_CASES"])[2:end]
        expected = readlines(ENV["LWBGT_ESAT_EXPECTED"])[2:end]
        @test length(cases) == length(expected)
        for (line, reference) in zip(cases, expected)
            row = split(line, ',')
            result = esat(parse(Float64, row[1]), parse(Int, row[2]))
            @test reinterpret(UInt32, result) == parse(UInt32, split(reference, ',')[end]; base=16)
        end
    end
end
