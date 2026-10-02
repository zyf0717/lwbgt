"""Exercise approval-result handling and stale PR revision rejection."""

from copy import deepcopy
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location(
    "pr_validation", Path(__file__).resolve().parents[1] / ".github/scripts/pr_validation.py"
)
validation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validation)


class PRValidation(unittest.TestCase):
    def test_current_revision(self):
        pr = dict(state="open", head=dict(sha="head"), base=dict(sha="base"))
        validation.validate_current(pr, pr)
        for field in ("head", "base", "state"):
            with self.subTest(field=field):
                changed = deepcopy(pr)
                changed[field] = "closed" if field == "state" else dict(sha="new")
                with self.assertRaises(RuntimeError):
                    validation.validate_current(pr, changed)

    def results(self, metadata):
        needs = {name: dict(result="success") for name in ("approve", "native", "python", "r", "julia")}
        needs["approve"]["outputs"] = dict(metadata_only=metadata)
        if metadata == "true":
            for name in ("native", "python", "r"):
                needs[name]["result"] = "skipped"
        return needs

    def test_full_and_metadata_only_success(self):
        for metadata in ("true", "false"):
            validation.validate_results(self.results(metadata))

    def test_failed_cancelled_and_unexpectedly_skipped_checks(self):
        for metadata in ("true", "false"):
            needs = self.results(metadata)
            for job in needs:
                for result in ("failure", "cancelled", "skipped", "success"):
                    if result == needs[job]["result"]:
                        continue
                    with self.subTest(metadata=metadata, job=job, result=result):
                        changed = deepcopy(needs)
                        changed[job]["result"] = result
                        with self.assertRaises(RuntimeError):
                            validation.validate_results(changed)

    def test_missing_classification_cannot_pass(self):
        needs = self.results("false")
        needs["approve"] = dict(result="failure", outputs={})
        with self.assertRaises(RuntimeError):
            validation.validate_results(needs)


if __name__ == "__main__":
    unittest.main()
