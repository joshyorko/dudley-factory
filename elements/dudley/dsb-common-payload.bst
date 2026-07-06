kind: manual

sources:
  - kind: git_repo
    url: github:joshyorko/dsb-common.git
    track: patchraptor/dudley-payload-contract
    # Pinned to the pushed payload contract branch commit.
    ref: 4da9f72ec6f770feb3ba8e4dda2a1c31ac45c440

build-depends:
  - freedesktop-sdk.bst:components/python3.bst

depends:
  - freedesktop-sdk.bst:public-stacks/runtime-minimal.bst

variables:
  strip-binaries: ""

config:
  install-commands:
    - |
      python3 scripts/install-payload.py --profile bluefin --dest "%{install-root}"
      install -d "%{install-root}%{sysconfdir}/dudley"
      cat >"%{install-root}%{sysconfdir}/dudley/build-manifest.json" <<'EOF'
      {
        "schema": "dudley-build-manifest.v1",
        "factory": "dudley-factory",
        "profile": "bluefin",
        "payload": {
          "source": "github:joshyorko/dsb-common.git",
          "track": "patchraptor/dudley-payload-contract",
          "ref": "4da9f72ec6f770feb3ba8e4dda2a1c31ac45c440",
          "contract": "contract/dudley-payload.v1.json"
        }
      }
      EOF
