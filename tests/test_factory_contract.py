#!/usr/bin/env python3
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


class FactoryContractTests(unittest.TestCase):
    def test_project_identity_is_dudley_factory(self) -> None:
        self.assertIn("name: dudley-factory", read("project.conf"))
        self.assertIn('env("BUILD_IMAGE_NAME", "dudley-bluefin")', read("Justfile"))

    def test_payload_element_uses_pinned_dsb_common_git_source(self) -> None:
        payload = read("elements/dudley/dsb-common-payload.bst")
        self.assertIn("url: github:joshyorko/dsb-common.git", payload)
        self.assertIn("ref: 4da9f72ec6f770feb3ba8e4dda2a1c31ac45c440", payload)
        self.assertNotIn("2ba6c6e39093b5d87797e6fee59b445ed2fd384e", payload)
        self.assertNotIn("placeholder", payload)
        self.assertIn("scripts/install-payload.py --profile bluefin", payload)
        self.assertIn("--dest \"%{install-root}\"", payload)
        self.assertNotIn("ghcr.io/joshyorko/dsb-common", payload)

    def test_bluefin_stack_includes_dudley_payload(self) -> None:
        stack = read("elements/bluefin/deps.bst")
        self.assertIn("dudley/dsb-common-payload.bst", stack)

    def test_oci_metadata_targets_dudley_images(self) -> None:
        bluefin = read("elements/oci/bluefin.bst")
        self.assertIn("'org.opencontainers.image.title': 'Dudley Bluefin'", bluefin)
        self.assertIn("'org.opencontainers.image.source': 'https://github.com/joshyorko/dudley-factory'", bluefin)
        self.assertIn("'org.opencontainers.image.ref.name': 'ghcr.io/joshyorko/dudley-bluefin:testing'", bluefin)

        nvidia = read("elements/oci/bluefin-nvidia.bst")
        self.assertIn("filename: oci/bluefin.bst", nvidia)
        self.assertIn("'org.opencontainers.image.title': 'Dudley Bluefin NVIDIA'", nvidia)
        self.assertIn("'org.opencontainers.image.ref.name': 'ghcr.io/joshyorko/dudley-bluefin-nvidia:testing'", nvidia)

    def test_os_release_targets_dudley_bluefin(self) -> None:
        os_release = read("elements/oci/os-release.bst")
        self.assertIn('IMAGE_NAME: "dudley-bluefin"', os_release)
        self.assertIn('IMAGE_VENDOR: "joshyorko"', os_release)
        self.assertIn('IMAGE_REF: "ostree-image-signed:docker://ghcr.io/joshyorko/dudley-bluefin"', os_release)
        self.assertIn('ID: "dudley-bluefin"', os_release)

    def test_workflows_publish_dudley_image_names(self) -> None:
        build = read(".github/workflows/build.yml")
        publish = read(".github/workflows/publish.yml")
        check = read("scripts/check_publish_workflow.py")
        self.assertIn("IMAGE_NAME: dudley-bluefin", build)
        self.assertIn("IMAGE_NAME: dudley-bluefin", publish)
        self.assertIn("dudley-bluefin.spdx.json", publish)
        self.assertIn("dudley-bluefin-nvidia.spdx.json", publish)
        self.assertIn("dudley-bluefin.spdx.json", check)

    def test_patchraptor_replaces_inherited_bot_automation(self) -> None:
        renovate = read(".github/renovate.json5")
        self.assertIn("github>joshyorko/renovate-config:org-inherited-config", renovate)
        self.assertNotIn("projectbluefin/" + "renovate-config", renovate)
        self.assertNotIn('"baseBranchPatterns": ["testing"]', renovate)
        self.assertNotIn('"branchPrefix": "renovate' + '/"', renovate)

        workflows = "\n".join(
            path.read_text(encoding="utf-8")
            for path in sorted((ROOT / ".github/workflows").glob("*.yml"))
        )
        self.assertNotIn("MERGE" + "RAPTOR", workflows)
        self.assertNotIn("merge" + "raptor", workflows)
        self.assertNotIn("reusable-renovate-" + "automerge", workflows)
        self.assertFalse((ROOT / ".github/workflows" / ("sync" + "-next-from-main.yml")).exists())
        self.assertFalse((ROOT / ".github/workflows/track-next-junctions.yml").exists())
        self.assertTrue((ROOT / ".github/workflows/track-bst-sources.yml").exists())
        source_tracking = read(".github/workflows/track-bst-sources.yml")
        self.assertIn("patchraptor/track-dsb-common-payload", source_tracking)
        self.assertIn("bluefin-nvidia/nvidia-container-toolkit.bst", source_tracking)
        self.assertIn("BASE_BRANCH: main", source_tracking)

    def test_stable_promotion_is_disabled_until_parity(self) -> None:
        execute_release = read(".github/workflows/execute-release.yml")
        self.assertIn("stable promotion is disabled", execute_release)
        self.assertIn("Current dudley-os remains the production release path", execute_release)
        self.assertNotIn("reusable-execute-release.yml", execute_release)


if __name__ == "__main__":
    unittest.main()
