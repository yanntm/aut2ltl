"""survey.cluster — shard a survey run across the OAR cluster.

Two halves of one contract, and nothing else: `plan` enumerates the examples
once and cuts them into index ranges; `shard` re-enumerates the same inputs on a
compute node and runs one of those ranges. Both lean on
`survey.discovery.discover`, whose order is documented as deterministic
(sorted), so an index range names the same examples on both sides.

Agnostic to what discovery finds. The only quantity that shapes the split is the
worst-case time of a single example — `--build-timeout + --equiv-timeout` — which
says how many examples a command's cap can bound. Throughput then comes from the
number of jobs, never from wide ones: a command is a sequential run and wants one
core.
"""
