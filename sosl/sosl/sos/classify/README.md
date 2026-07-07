# sosl.sos.classify — classification read-offs on the invariant table

Pure scans of an `Invariant`'s multiplication table, one subpackage per band
of the classification. Normative math: `research_notes/sos_classification.md`
(procedures and sources); tool shape of the full classifier:
`research_notes/sos_classifier_spec.md`.

## Map

    aperiodic/   Band 1 — power orbits of every class; the algebra is
                 aperiodic (the language LTL-definable) iff every orbit has
                 eventual period 1; on failure, the first group carrier in
                 shortlex order, with its index, period, and power cycle.

No module here touches an automaton or an external tool: every verdict is a
table computation on `(𝒞, λ, M, P)`, exact by canonicity of the invariant.
