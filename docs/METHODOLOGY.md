# Manufactured solution and mixed formulation

Let A(x)=x²(1-x)², B(y)=y²(1-y)² and ψ=A B. Set u=(A B', -A' B), which is divergence free because ∂x u1 + ∂y u2=A'B'-A'B'=0. A, A', B and B' vanish on the corresponding square boundaries, so u=0 there.

Pressure is p=sin(πx)sin(πy)-4/π². Its domain integral is zero. For viscosity ν, the exact forcing is:

- f1=-ν(A″B′+AB‴)+π cos(πx)sin(πy).
- f2=ν(A‴B+A′B″)+π sin(πx)cos(πy).

For velocity v and pressure test q, the implemented symmetric saddle-point form is ν(∇u,∇v)-(p,div v)-(q,div u)-ε(p,q)=(f,v), with no-slip boundary velocity. Default ν=1 and ε=1e-10. This pressure-mass perturbation regularizes the pressure null mode but also slightly perturbs incompressibility. Pressure is shifted to zero mean after solving. It is not an LBB/inf-sup stabilization for P1/P1.

Taylor–Hood uses P2 velocity and P1 pressure; equal-order uses P1/P1 on the same square triangulations. N is the number of intervals per coordinate and h=1/N is the reported mesh scale. The maximum triangle diameter is sqrt(2)/N; the fixed factor does not change refinement rates. UMFPACK solves each assembled mixed system. Quadrature order 8 is used for forcing and errors to reduce underintegration of the trigonometric pressure.

Errors: vector velocity L², velocity gradient H¹ seminorm, pressure L² after mean normalization, and divergence L². Rates are log(error_coarse/error_fine)/log(h_coarse/h_fine). The first mesh has no rate. For this smooth solution, stable Taylor–Hood behavior approaches orders 3 (velocity L²), 2 (H¹) and 2 (pressure L²), as verified numerically. Equal-order pressure oscillations and weak pressure convergence illustrate the unstable comparator; results are not advertised as a valid equal-order solver.

Total algebraic space dimensions include boundary velocity nodes: 2*dim(Vh)+dim(Qh). Free velocity DOFs subtract 4N boundary nodes per scalar P1 field, or 8N for P2. The two methods have different dimensions for the same mesh; plots compare approximation behavior, not equal-computational-budget efficiency. Timings are omitted because hardware and solver configuration would dominate a superficial comparison.

Tests run N=8 and 16, check substantial Taylor–Hood error reduction and a near-zero pressure integral, and verify DOF accounting. These are regression/verification checks for this manufactured case, not a proof of general stability. Pressure regularization, fixed smooth geometry and no adaptive mesh are explicit limits.

Reference: https://doc.freefem.org/tutorials/stokes.html.
