# Copilot Instructions for Dudley Factory

Read `AGENTS.md` and `README.md` before changing this repository.

## Identity

This repo is `joshyorko/dudley-factory`, seeded from Project Bluefin Dakota's
BuildStream model. It builds Dudley factory images, not upstream Dakota images.

Active targets:

- `ghcr.io/joshyorko/dudley-bluefin:testing`
- `ghcr.io/joshyorko/dudley-bluefin-nvidia:testing`

Stable promotion is disabled until `dudley-bluefin` and
`dudley-bluefin-nvidia` pass boot, update, rollback, and installer parity.
The current production release path remains `joshyorko/dudley-os`.

## Hard Rules

- Never push to `projectbluefin/dakota` or `castrojo/dakota` from this repo.
- Never publish `ghcr.io/projectbluefin/dakota` images from this repo.
- Do not re-enable stable promotion without explicit maintainer approval and
  parity evidence.
- Do not introduce live `dnf`, COPR, RPM, or Containerfile package layering into
  the factory image path.
- Source reusable Dudley payload from `joshyorko/dsb-common` by pinned git ref
  through `elements/dudley/dsb-common-payload.bst`.
- Keep Ubuntu experimental until the Bluefin target boots and the portable
  payload path is proven.

## Build Commands

```bash
just validate
BUILD_SKIP_NVIDIA=1 just build bluefin
just build bluefin-nvidia
just boot-test bluefin
just boot-test bluefin-nvidia
just lint bluefin
```

`just validate` is the lightweight graph and workflow gate. Full image builds
and boot tests are heavy and must be reported separately from graph validation.

## Current Architecture

- `elements/bluefin/deps.bst` is the Dudley Bluefin package graph despite the
  historical directory name.
- `elements/dudley/dsb-common-payload.bst` installs shared Dudley payload.
- `elements/oci/bluefin.bst` assembles the Dudley Bluefin OCI image.
- `elements/oci/bluefin-nvidia.bst` composes from `oci/bluefin.bst` plus NVIDIA
  elements.
- `publish.yml` may publish `:testing` after its boot check.
- `execute-release.yml` and `rollback-stable.yml` intentionally fail until
  stable parity is proven.

## Reporting

Be precise about what was validated:

- "graph-valid" means `bst show` and unit checks passed.
- "built" means `just build <variant>` completed.
- "booted" means `just boot-test <variant>` completed.
- "stable-ready" means boot, update, rollback, installer, and NVIDIA parity
  gates are all proven.
