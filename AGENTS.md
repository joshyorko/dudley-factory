# AGENTS.md

Dudley Factory is a BuildStream 2 OS factory seeded from Project Bluefin Dakota.
It is not the current production Dudley release path. Current production remains
`joshyorko/dudley-os` until the factory `dudley-bluefin` and
`dudley-bluefin-nvidia` images build, boot, and pass parity checks.

## Current Scope

- First supported factory targets:
  - `ghcr.io/joshyorko/dudley-bluefin:testing`
  - `ghcr.io/joshyorko/dudley-bluefin-nvidia:testing`
- Stable promotion is intentionally disabled until boot, update, rollback, and
  installer parity are proven.
- Ubuntu is a later experimental adapter. Do not force Ubuntu through the
  Bluefin/GNOME/Freedesktop graph in v1.
- Chrome is not installed through live `dnf` in BuildStream. Keep it runtime or
  add a pinned manual element later.

## Repo Boundaries

- `dudley-factory` owns OS assembly, BuildStream elements, image metadata,
  factory CI, and `bcvk` boot-test workflows.
- `dsb-common` owns the reusable Dudley payload contract:
  `contract/dudley-payload.v1.json` and `scripts/install-payload.py`.
- `dudley-os` remains the production Bluefin-layered Containerfile image until
  the factory proves parity.

## Hard Rules

- Do not push, open PRs, dispatch workflows, or create releases without explicit
  user approval.
- Do not push anything to `projectbluefin/dakota`, `castrojo/dakota`, or
  `ublue-os/*` from this repo.
- Treat inherited Dakota docs and `docs/skills/` as implementation source
  material, not current Dudley Factory policy, unless this file or `README.md`
  says otherwise.
- Build image content with BuildStream elements. Do not add Containerfile
  package overlays, live `dnf`, COPR, or RPM script layering to factory images.
- Keep stable promotion disabled until the parity gate is explicitly completed
  and documented.
- Source Dudley payload from `joshyorko/dsb-common` by pinned git `ref`, not from
  a mutable OCI layer.
- Use `dudley/dsb-common-payload.bst` for shared payload installation before
  final OCI assembly steps such as schema compilation, `dconf update`, and image
  metadata generation.

## Common Commands

```bash
just validate
BUILD_SKIP_NVIDIA=1 just build bluefin
just build bluefin-nvidia
just boot-test bluefin
just boot-test bluefin-nvidia
just lint bluefin
```

BuildStream runs inside the pinned `bst2` container through the `just bst`
wrapper. Use `BST_FLAGS` when CI or local cache configuration requires it.

## Verification Expectations

Before reporting a change as ready, run the narrow tests that cover it and read
the output. For this seed work, the minimum local checks are:

```bash
python3 -m unittest tests.test_factory_contract -v
python3 scripts/check_publish_workflow.py
just --list
just bst show --deps all oci/bluefin.bst
just bst show --deps all oci/bluefin-nvidia.bst
git diff --check
```

Full image build and boot parity are separate heavy gates. Do not claim they
passed unless `just build ...` and `just boot-test ...` were actually run and
their outputs were inspected.

## Branching

Use feature branches. `testing` is the active factory stream branch once the
GitHub repository exists. `main`/`:stable` are promotion targets only after
factory parity is proven.
