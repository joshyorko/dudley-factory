# Dudley Factory

Dudley Factory is the BuildStream-based OS assembly repo for Dudley images.
It is seeded from Project Bluefin Dakota's BuildStream model, but it is not the
current production Dudley release path. The existing `dudley-os` Containerfile
image remains production until these factory images boot and pass parity checks.

## First Targets

| Target | Image | Status |
|---|---|---|
| Dudley Bluefin | `ghcr.io/joshyorko/dudley-bluefin:testing` | first factory target |
| Dudley Bluefin NVIDIA | `ghcr.io/joshyorko/dudley-bluefin-nvidia:testing` | composes from Dudley Bluefin plus NVIDIA elements |
| Dudley Ubuntu | `ghcr.io/joshyorko/dudley-ubuntu:experimental` | deferred feasibility track |

Stable tags are promotion targets only after the matching testing images boot,
update, roll back, and pass parity checks.

## Architecture

- BuildStream owns OS assembly through `project.conf` and `elements/`.
- The Containerfile remains only a bootc lint helper.
- `dsb-common` owns the portable Dudley payload contract.
- `elements/dudley/dsb-common-payload.bst` installs that payload by pinned git
  source with `scripts/install-payload.py --profile bluefin`.
- Final OCI assembly still runs Dakota's proven order: `prepare-image.sh`,
  `systemd-sysusers`, `glib-compile-schemas`, `/etc` normalization,
  `dconf update`, `ldconfig`, then `build-oci`.

## Local Commands

```bash
just validate
BUILD_SKIP_NVIDIA=1 just build bluefin
just boot-test bluefin
just build bluefin-nvidia
just boot-test bluefin-nvidia
```

`bcvk` boot tests are the factory VM path. Keep the current `dudley-os`
`bootc-image-builder` and QCOW2 flow as the comparison baseline until this repo
proves parity.

## Ubuntu Track

Do not force Ubuntu through the Bluefin/GNOME/Freedesktop graph in v1. The first
Ubuntu milestone is only: Dudley payload installs, bootc update semantics are
feasible, and the image boots to SSH/systemd. Ubuntu remains experimental until
install, update, rollback, and publishing paths are proven.

## Chrome

Chrome is not installed through live `dnf` in BuildStream. Keep Chrome as a
runtime/user payload until a pinned manual element exists with version and
checksum control.
