# Dudley Factory CI Reference

This repository is a BuildStream experiment for the Dudley Factory testing
images:

- `ghcr.io/joshyorko/dudley-bluefin:testing`
- `ghcr.io/joshyorko/dudley-bluefin-nvidia:testing`

The stable promotion is disabled until both variants pass boot, update, rollback,
installer, and NVIDIA parity checks. The production release path remains
`joshyorko/dudley-os`.

## Jobs

| Job | Trigger | What it proves |
|---|---|---|
| `validate` | pull requests and merge queue for `main` | Unit contracts, publish workflow contract, and BuildStream graph resolution for both variants |
| `build` | daily schedule and manual dispatch | Full x86_64 BuildStream build for `oci/bluefin.bst` and `oci/bluefin-nvidia.bst`; NVIDIA may continue-on-error while the base image remains blocking |
| `publish` | successful build workflow or manual dispatch | Exports, chunks, lints, signs, attests, and publishes immutable `:$sha` tags; `:testing` only advances from `main` after the boot check |
| `build-aarch64` | publish workflow follow-up or manual dispatch | ARM64 build path for the base Bluefin variant |

## Local Validation

Run the same lightweight checks before reporting graph-valid work:

```bash
python3 -m unittest tests.test_factory_contract -v
python3 scripts/check_publish_workflow.py
just --list
just bst show --deps all oci/bluefin.bst
just bst show --deps all oci/bluefin-nvidia.bst
git diff --check
```

`just validate` runs the unit and workflow checks, then resolves both
BuildStream graphs through the pinned `bst2` container.

If the host lacks `podman`, open this repo in the included devcontainer. It uses
`ghcr.io/ublue-os/devcontainer:latest`, which carries the container tooling the
`just bst` wrapper expects. When the devcontainer itself is running under
Docker, the wrapper automatically uses isolated `vfs` podman storage so the
pinned `bst2` image can unpack correctly.

## Variant Wiring

Dudley follows Dakota's BuildStream shape:

- `oci/bluefin.bst` assembles the base Dudley Bluefin image.
- `oci/bluefin-nvidia.bst` composes from `oci/bluefin.bst` and adds the
  `bluefin-nvidia/deps.bst` stack.
- The workflow matrices build and publish `bluefin` and `bluefin-nvidia`
  explicitly.
- Local helpers accept `bluefin` and `bluefin-nvidia` variants where variant
  behavior matters.

## Reporting

Keep proof layers separate:

- `graph-valid`: unit contracts, workflow contract, and `bst show` passed.
- `built`: `just build <variant>` completed.
- `booted`: `just boot-test <variant>` completed.
- `stable-ready`: boot, update, rollback, installer, and NVIDIA parity are all
  documented.
