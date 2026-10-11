\name{calculate}
\alias{calculate}
\title{Calculate Outdoor Wet Bulb Globe Temperature}
\usage{
calculate(input, psychrometric = TRUE)
}
\arguments{
\item{input}{A data frame containing the columns produced by
\code{lwbgt_input()}. Additional columns are ignored.}
\item{psychrometric}{Calculate psychrometric wet-bulb temperature, default
\code{TRUE}. With \code{FALSE}, that column is \code{NA}; the other
calculations are unchanged. Skipping a failed psychrometric solve can allow
a row to succeed.}
}
\value{
A plain data frame with the following columns:
\itemize{
\item \code{status}: integer status; zero means all requested solves succeeded,
-1 means a requested solver did not converge, 1 means missing input, 2 means
invalid input, and 3 means an invalid native result.
\item \code{status_message}: character description of the row status.
\item \code{estimated_wind_speed_m_s}: estimated wind at 2 m, in metres per second.
\item \code{globe_temperature_c}: globe temperature, in degrees Celsius.
\item \code{natural_wet_bulb_c}: natural wet-bulb temperature, in degrees Celsius.
\item \code{psychrometric_wet_bulb_c}: psychrometric wet-bulb temperature, in
degrees Celsius; \code{NA} when skipped.
\item \code{wbgt_c}: outdoor wet bulb globe temperature, in degrees Celsius.
}
All numerical outputs are \code{NA} for nonzero statuses.
}
\description{
Calculates one result per input row while preserving row order. Invalid rows do
not prevent valid rows from being calculated.
}
\examples{
input <- lwbgt_input(
  year = 2024, month = 4, day = 15, hour = 14, minute = 30,
  gmt_offset_hours = 8, averaging_minutes = 60, urban = 1,
  latitude_deg_north = 1.3521, longitude_deg_east = 103.8198,
  solar_w_m2 = 742, pressure_hpa = 1008.4,
  air_temperature_c = 32.1, relative_humidity_percent = 68,
  wind_speed_m_s = 2.8, wind_height_m = 10,
  vertical_temperature_difference_c = 1
)
calculate(input)
}
