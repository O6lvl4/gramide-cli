# Reproducible checks

Run `bash ci/check.sh` from a checkout with Almide installed, or set
`ALMIDE_BIN` to an absolute compiler path. This builds `gramide` (`almide build --release -o gramide`) — fetching
the engine and the four language packages at the commits `almide.lock`
records — and checks the built CLI against temporary fixtures: one file per
language through `check` and `outline`, the discovery contract of
`gramide languages`, and the `symbols` schema over every package. No model API
or credentials are used.

Everything about one language — its grammar tests, its corpus, its oracle
against the reference parser — is checked in that language's own repository,
by its own binary. This repository checks only that the composition holds.

CI pins Almide to `dff9a458f2e581631bb6537c856a7974036e4153` and Rust to
`1.94.0`. Upgrade these deliberately and rerun the checks together. The compiler
binary cache is keyed by both versions.
