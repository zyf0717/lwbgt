\name{lwbgt_input}
\alias{lwbgt_input}
\title{Construct WBGT Input Records}
\usage{
lwbgt_input(
  year, month, day, hour, minute, gmt_offset_hours, averaging_minutes,
  urban, latitude_deg_north, longitude_deg_east, solar_w_m2,
  pressure_hpa, air_temperature_c, relative_humidity_percent,
  wind_speed_m_s, wind_height_m, vertical_temperature_difference_c
)
}
\arguments{
\item{year}{Integer-valued Gregorian year from 1950 through 2049.}
\item{month, day, hour, minute}{Integer-valued local standard date and time.
Months are 1--12 and days must be valid for the selected year and month.
A \code{month} of zero makes \code{day} a day-of-year value (1--365 or 366).
Hours are 0--23 and minutes are 0--59.}
\item{gmt_offset_hours}{Local standard time minus GMT, in whole hours from
-12 through 14. Convert daylight-saving or fractional-offset timestamps to
standard time or UTC before constructing inputs.}
\item{averaging_minutes}{Integer averaging interval from 0 through 1440 minutes.
The kernel subtracts half this interval from the supplied timestamp to center
the calculation. Use zero for instantaneous or already centered observations.}
\item{urban}{Zero for rural wind scaling or one for urban wind scaling.}
\item{latitude_deg_north, longitude_deg_east}{Finite coordinates in degrees
north (-90 through 90) and degrees east (-180 through 180).}
\item{solar_w_m2}{Finite, nonnegative solar irradiance in watts per square metre.}
\item{pressure_hpa}{Finite, positive barometric pressure in hectopascals.}
\item{air_temperature_c}{Finite dry-bulb temperature in degrees Celsius,
strictly above -273.15.}
\item{relative_humidity_percent}{Finite relative humidity from 0 through 100 percent.}
\item{wind_speed_m_s}{Finite, nonnegative wind speed in metres per second.}
\item{wind_height_m}{Finite, positive wind measurement height in metres.}
\item{vertical_temperature_difference_c}{Finite upper-minus-lower temperature
difference in degrees Celsius. Only whether it is \code{< 0} or \code{>= 0} is
used. It can affect results only for rural nighttime records when
\code{wind_height_m} differs from 2 m and \code{wind_speed_m_s} is below 2.5.}
}
\value{A plain data frame with the 17 native input columns.}
\description{
Constructs one or more input rows. All arguments are required; scalar values
are recycled to the common non-scalar length. Row values are validated by
\code{\link{calculate}}, rather than by this constructor. Valid input ranges
do not guarantee solver convergence.
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
}
