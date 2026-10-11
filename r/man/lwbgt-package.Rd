\name{lwbgt-package}
\alias{lwbgt-package}
\alias{lwbgt}
\docType{package}
\title{Reference-Compatible Outdoor Wet Bulb Globe Temperature}
\description{
Dependency-free, vectorized access to the Liljegren outdoor wet bulb globe
temperature numerical model.
}
\details{
The R, Python, Julia, Swift, and native C interfaces share the same Liljegren
numerical C kernel.

Inputs use the same explicit field names and units as the native and Python
interfaces. The R interface performs row-level validation and reports failures
without aborting calculations for other rows.
}
\seealso{
Other interfaces to the shared kernel:
\href{https://pypi.org/project/lwbgt/}{Python on PyPI},
\href{https://github.com/zyf0717/LWBGT.jl}{Julia (LWBGT.jl)},
\href{https://github.com/zyf0717/lwbgt#swiftpm}{Swift}, and
\href{https://github.com/zyf0717/lwbgt#native-c}{native C}.
See the
\href{https://github.com/zyf0717/lwbgt/blob/main/docs/README.md}{documentation index}
for the shared kernel and its interfaces.
}
\references{
Liljegren, J. C., Carhart, R. A., Lawday, P., Tschopp, S., and Sharp, R.
(2008). Modeling the Wet Bulb Globe Temperature Using Standard Meteorological
Measurements. \emph{Journal of Occupational and Environmental Hygiene},
5(10), 645--655. \doi{10.1080/15459620802310770}.
}
