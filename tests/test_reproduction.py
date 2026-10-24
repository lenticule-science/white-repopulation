"""Every quantitative sentence in the paper must follow from the records."""

import hashlib
import json
import unittest
from pathlib import Path

from analysis import reproduce

ROOT = Path(__file__).resolve().parent.parent


class ManuscriptClaims(unittest.TestCase):
    def test_every_stated_number_is_derived_from_records(self):
        disagreements = [c for c in reproduce.claims() if not c["agrees"]]
        self.assertEqual(disagreements, [])

    def test_headline_shares(self):
        births = reproduce.BirthReconstruction.from_record(reproduce.load(reproduce.BIRTH_SERIES))
        self.assertEqual(births.share(1, 5), (5_167_522, 30_038_000))
        self.assertEqual(str(reproduce.percent(*births.share(1, 5))), "17.20")
        self.assertEqual(str(reproduce.percent(*births.share(0, 6))), "16.82")

    def test_sensitivity_moves_only_the_1790s_denominator(self):
        births = reproduce.BirthReconstruction.from_record(reproduce.load(reproduce.BIRTH_SERIES))
        low = births.share(1, 5)
        for rate in reproduce.SENSITIVITY_RATES:
            assumed = reproduce.BirthReconstruction.assumed_1790s_births(births.mean_population_1790s, rate)
            self.assertEqual(births.share(1, 5, assumed), low)


class DerivedTables(unittest.TestCase):
    def setUp(self):
        reproduce.main()

    def test_tables_match_the_v0_1_0_release_bundle(self):
        # The v0.1.0 bundle stored these tables with CRLF line endings; its
        # recorded digests must still be reproducible from the records.
        manifest = json.loads((ROOT / "archive" / "v0.1.0-release-candidate" / "publication.json").read_text(encoding="utf-8"))
        for name in ("births-1790-1859.csv", "us-migration-growth-1790-1860.csv"):
            data = (ROOT / "data" / "derived" / name).read_bytes().replace(b"\n", b"\r\n")
            recorded = manifest["files"][f"data/{name}"]
            self.assertEqual(hashlib.sha256(data).hexdigest(), recorded["sha256"], name)
            self.assertEqual(len(data), recorded["bytes"], name)

    def test_data_package_lists_every_derived_table(self):
        package = json.loads((ROOT / "datapackage.json").read_text(encoding="utf-8"))
        listed = {r["path"] for r in package["resources"]}
        for path in (ROOT / "data").rglob("*"):
            if path.is_file() and path.suffix in {".csv", ".json"}:
                self.assertIn(path.relative_to(ROOT).as_posix(), listed)


if __name__ == "__main__":
    unittest.main()
