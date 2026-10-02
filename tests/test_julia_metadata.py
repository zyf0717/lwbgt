"""Regression tests for the metadata commit's source and CI gates."""

import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location(
    "commit_metadata", Path(__file__).resolve().parents[1] / "julia/build/commit_metadata.py"
)
metadata = importlib.util.module_from_spec(spec)
spec.loader.exec_module(metadata)


class MetadataGates(unittest.TestCase):
    def runs(self):
        return [dict(id=i, path=path, event="pull_request", head_sha="tested",
                     status="completed", conclusion="success")
                for i, path in enumerate(sorted(metadata.WORKFLOWS))]

    def test_all_workflows_must_pass_for_this_source(self):
        runs = self.runs()
        self.assertEqual(metadata.pending_workflows(runs, "tested"), set())
        self.assertEqual(metadata.pending_workflows(runs, "new-source"), metadata.WORKFLOWS)
        self.assertEqual(metadata.pending_workflows(runs[:-1], "tested"), {runs[-1]["path"]})

    def test_newer_run_replaces_earlier_success(self):
        runs = self.runs()
        runs.append(dict(runs[0], id=100, status="in_progress", conclusion=None))
        self.assertEqual(metadata.pending_workflows(runs, "tested"), {runs[0]["path"]})

    def test_failure_or_cancellation_prevents_commit(self):
        for conclusion in ("failure", "cancelled", "skipped", "timed_out", "neutral"):
            with self.subTest(conclusion=conclusion):
                runs = self.runs()
                runs[0]["conclusion"] = conclusion
                with self.assertRaises(RuntimeError):
                    metadata.pending_workflows(runs, "tested")

    def test_other_events_do_not_count(self):
        runs = self.runs()
        runs[0]["event"] = "push"
        self.assertEqual(metadata.pending_workflows(runs, "tested"), {runs[0]["path"]})

    def test_only_unchanged_open_same_repository_pr(self):
        pr = dict(state="open", head=dict(repo=dict(full_name="owner/repo"), sha="tested", ref="feat/test"))
        self.assertEqual(metadata.check_pr(pr, "owner/repo", "tested"), "feat/test")
        for repository, head in (("fork/repo", "tested"), ("owner/repo", "changed")):
            with self.assertRaises(RuntimeError):
                metadata.check_pr(pr, repository, head)
        pr["state"] = "closed"
        with self.assertRaises(RuntimeError):
            metadata.check_pr(pr, "owner/repo", "tested")


if __name__ == "__main__":
    unittest.main()
