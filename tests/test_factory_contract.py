#!/usr/bin/env python3
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def tracked_text_files() -> list[Path]:
    return [
        path
        for path in ROOT.rglob("*")
        if path.is_file()
        and ".git" not in path.parts
        and ".cache" not in path.parts
        and path.suffix not in {".png", ".jpg", ".jpeg", ".gif", ".ico", ".fd", ".raw", ".qcow2"}
    ]


class FactoryContractTests(unittest.TestCase):
    def test_project_identity_is_dudley_factory(self) -> None:
        self.assertIn("name: dudley-factory", read("project.conf"))
        self.assertIn('env("BUILD_IMAGE_NAME", "dudley-bluefin")', read("Justfile"))

    def test_devcontainer_uses_bluefin_devcontainer_image(self) -> None:
        devcontainer = read(".devcontainer/devcontainer.json")
        self.assertIn('"name": "bluefin-devcontainer"', devcontainer)
        self.assertIn('"image": "ghcr.io/ublue-os/devcontainer:latest"', devcontainer)

    def test_bst_wrapper_supports_nested_devcontainer_storage(self) -> None:
        justfile = read("Justfile")
        self.assertIn("BST_PODMAN_GLOBAL_ARGS", justfile)
        self.assertIn("--storage-driver=vfs", justfile)
        self.assertIn("${BST_PODMAN_GLOBAL_ARGS_ARRAY[@]}", justfile)

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

    def test_repo_does_not_document_nonexistent_factory_image_refs(self) -> None:
        forbidden = [
            "ghcr.io/joshyorko/" + "dudley-factory",
            "dudley-factory" + "-nvidia",
        ]
        offenders: list[str] = []
        for path in tracked_text_files():
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for token in forbidden:
                if token in text:
                    offenders.append(f"{path.relative_to(ROOT)} contains {token}")
        self.assertEqual([], offenders)

    def test_local_registry_push_is_variant_aware(self) -> None:
        justfile = read("Justfile")
        self.assertIn('push-local variant="bluefin" registry="localhost:5000"', justfile)
        self.assertIn('bluefin-nvidia|nvidia)  FINAL_NAME="{{image_name}}-nvidia" ;;', justfile)
        self.assertIn('Run \'just export {{variant}}\' first.', justfile)

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

    def test_build_skips_remote_cas_push_without_credentials(self) -> None:
        action = read(".github/actions/generate-bst-ci-config/action.yml")
        build = read(".github/workflows/build.yml")
        self.assertIn("cache-credentials-present", action)
        self.assertIn("CACHE_CREDENTIALS_PRESENT=true", action)
        self.assertIn("CACHE_CREDENTIALS_PRESENT=false", action)
        self.assertIn("id: bst_config", build)
        self.assertIn("if: steps.bst_config.outputs.cache-credentials-present == 'true'", build)
        self.assertIn("Skip remote CAS push without credentials", build)

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

    def test_top_level_docs_describe_dudley_factory_policy(self) -> None:
        ci = read("docs/ci.md")
        workflow = read("docs/workflow.md")
        gen_filemap = read("scripts/gen-filemap.py")
        for doc in (ci, workflow):
            self.assertIn("Dudley Factory", doc)
            self.assertIn("stable promotion is disabled", doc)
            self.assertIn("dudley-bluefin-nvidia", doc)
            self.assertNotIn("ghcr.io/projectbluefin/dakota", doc)
            self.assertNotIn("gh workflow run", doc)
            self.assertNotIn("fast-forwarded by `execute-release.yml`", doc)
        self.assertNotIn("dakota image", gen_filemap)
        self.assertNotIn("dakota project root", gen_filemap)


if __name__ == "__main__":
    unittest.main()
