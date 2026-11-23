# Round 03 evaluation contract, fixed before candidate execution

The research clarified the original rubric without changing it. Page overflow is not by itself a Reflow failure; a local scroll container is recommended, not universally required. Rectangular bounds do not prove effective pointer geometry. The implementation is an input-model precheck, not browser automation or WCAG certification.

## Required outcomes

1. Reflow model: complete non-excepted observations at 320 CSS px vertical / 256 CSS px horizontal may pass the input model. Known lost required items or known non-excepted failure must be reported. Missing observations and claimed two-dimensional exceptions require review. A justified exception candidate causing page overflow must not be automatically failed merely because it is not in a local container.
2. Geometry model: confirmed filled axis-aligned rectangles use exact decimal/rational arithmetic. 24×24 satisfies the size relation; 23.999 must not be rounded up. Undersized spacing checks both circle/circle and circle/every-other-effective-target relations. Touching boundaries follow the documented inference from official examples.
3. Unsupported/clipped/nonrectangular/overlapping/uncertain geometry and incomplete neighborhoods must not yield unqualified spacing success. Negative positions are valid; nonpositive dimensions, booleans, nonfinite data and mixed contexts are rejected.
4. All named exceptions retain conditions and evidence references. The precheck does not substantively validate them. A valid-looking exception remains HOLD for review; contradicted conditions are recorded. An exempted target is not removed from another target's neighborhood.
5. Synthetic or supplied input never creates browser/AT execution, full UI acceptance, or WCAG conformance. DOM/visual/keyboard/AT order and actual input method remain separate protocol observations.

## Fixed comparison and limitations

Use two deliberately shallow controls: `not page_overflow`, and `every bounding rectangle is >=24 in both axes`. They are authored experimental controls, not previous production behavior or model generation. Compare both false-positive and false-negative counterexamples with exact expected model labels. Do not publish an improvement percentage.

The task uses a booking-layout specimen, a two-dimensional data-table scenario, and a different-product toolbar model. Synthetic coordinates are explicitly authored, not extracted from the HTML. Browser execution is blocked. Both complete instruction units will remain HOLD without runtime observation; the pure precheck may pass its narrowly defined tests.

The critic must add independent malformed/boundary/counterexample probes, preserve initial failures, and recheck corrections separately. All critical findings require a location, input, observed/expected outcome, impact, source or contract, and repair direction.
