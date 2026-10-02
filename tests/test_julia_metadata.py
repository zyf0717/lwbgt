"""Regression tests for release preparation and archive provenance checks."""

import importlib.util
import os
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location(
    "preparation", Path(__file__).resolve().parents[1] / "julia/build/preparation.py"
)
preparation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(preparation)


class PreparationGates(unittest.TestCase):
    def run_record(self):
        return dict(status="completed", conclusion="success", event="workflow_dispatch",
                    head_branch="main", path=".github/workflows/julia.yml", head_sha="tested",
                    head_repository=dict(full_name="owner/repo"))

    def test_successful_manual_preparation(self):
        self.assertIsNone(preparation.validate_run(self.run_record(), "owner/repo", "tested"))

    def test_other_sources_or_runs_cannot_authorize_release(self):
        changes = dict(status="in_progress", conclusion="failure", event="pull_request",
                       head_branch="feature", path=".github/workflows/ci.yml", head_sha="other",
                       head_repository=dict(full_name="fork/repo"))
        for key, value in changes.items():
            with self.subTest(key=key):
                run = self.run_record()
                run[key] = value
                with self.assertRaises(RuntimeError):
                    preparation.validate_run(run, "owner/repo", "tested")

    def test_manual_preparation_requires_main_and_an_unused_version(self):
        with patch.dict(os.environ, GITHUB_REF="refs/heads/main"), \
                patch.object(Path, "read_text", return_value='version = "1.0.2"'), \
                patch.object(preparation.subprocess, "run") as tags, \
                patch.object(preparation, "output") as output:
            tags.return_value = subprocess.CompletedProcess([], 1)
            preparation.preflight()
            output.assert_called_once_with(version="1.0.2")
            tags.return_value = subprocess.CompletedProcess([], 0)
            with self.assertRaisesRegex(RuntimeError, "already exists"):
                preparation.preflight()
            tags.return_value = subprocess.CompletedProcess([], 2)
            with self.assertRaisesRegex(RuntimeError, "could not check"):
                preparation.preflight()
            with patch.dict(os.environ, GITHUB_REF="refs/heads/feature"):
                with self.assertRaisesRegex(RuntimeError, "on main"):
                    preparation.preflight()

    def test_preparation_rejects_nonrelease_versions(self):
        with patch.dict(os.environ, GITHUB_REF="refs/heads/main"):
            for version in ("1.2", "1.2.3-rc1", "1.2.3+1"):
                with self.subTest(version=version), \
                        patch.object(Path, "read_text", return_value=f'version = "{version}"'):
                    with self.assertRaisesRegex(RuntimeError, "stable shared release version"):
                        preparation.preflight()


if __name__ == "__main__":
    unittest.main()
