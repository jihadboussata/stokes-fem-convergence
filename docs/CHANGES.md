# Portfolio revision

- Consolidated two element-pair experiments around one manufactured-solution solver template.
- Added a headless Python runner with parameter validation, automatic directories and configurable mesh lists.
- Regenerated all convergence errors and figures using FreeFEM 4.13; increased forcing/error quadrature order.
- Made zero-mean pressure and the pressure penalty explicit; distinguished regularization from equal-order stabilization.
- Corrected and documented total versus free velocity DOF counts; compute rates from actual refinement ratios.
- Exported canonical CSV errors, finest-mesh fields and reproducible parameter records.
- Added numerical refinement/pressure/DOF checks and explained the stable versus unstable comparison.
