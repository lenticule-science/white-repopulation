"""Recompute every quantitative claim in White Repopulation from its source records.

The paper states its numbers in prose; this module derives each one from
`data/records/` so that a reader can check the arithmetic, change an
assumption, and see which sentences move. It uses only the Python standard
library so the computation has no supply chain beyond the interpreter.

Run `python -m analysis.reproduce` from the repository root. It writes
`data/derived/*.csv` and `data/derived/claims.json` and exits non-zero if a
derived value disagrees with the value the manuscript states.
"""

from __future__ import annotations

import csv
import io
import json
import sys
from dataclasses import dataclass
from decimal import ROUND_HALF_EVEN, Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RECORDS = ROOT / "data" / "records"
DERIVED = ROOT / "data" / "derived"

BIRTH_SERIES = RECORDS / "2026-10-17-captive-birth-shares-source-series.json"
MIGRATION_SERIES = RECORDS / "us-net-migration-share-of-growth-1790-1860.json"
STERILIZATION_RECORD = RECORDS / "white-increase-eugenic-selection-measurements-2026-10-17.json"
CASE_REGISTER = RECORDS / "2026-10-17-antebellum-property-law-case-register.json"
VIRGINIA_SEQUENCE = RECORDS / "2026-10-17-virginia-racial-integrity-legislative-sequence.json"

DECADES = [(1790 + 10 * i, 1799 + 10 * i) for i in range(7)]
SENSITIVITY_RATES = (45, 50, 55, 60, 65)


def load(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def percent(numerator: int, denominator: int, places: int = 2) -> Decimal:
    """Exact share as a percentage, rounded half-even to `places` decimals."""
    quantum = Decimal(1).scaleb(-places)
    return (Decimal(numerator) * 100 / Decimal(denominator)).quantize(quantum, ROUND_HALF_EVEN)


@dataclass(frozen=True)
class BirthReconstruction:
    captive_by_decade: tuple[int, ...]
    all_by_decade: tuple[int, ...]
    births_1790s_assumed: int
    mean_population_1790s: int
    assumed_cbr_1790s: int

    @classmethod
    def from_record(cls, record: dict) -> "BirthReconstruction":
        source = record["source"]
        captive = tuple(source["captive_births_1790_1859_by_decade"])
        annual = {row["year"]: row["births_thousands"] for row in source["births_all_1800_1859_thousands"]}
        if sorted(annual) != list(range(1800, 1860)):
            raise ValueError("annual birth series must cover 1800-1859 exactly")
        rate = record["assumed_cbr_1790s_per_thousand"]
        population = source["mean_population_1790s"]
        births_1790s = cls.assumed_1790s_births(population, rate)
        observed = tuple(1000 * sum(annual[y] for y in range(start, end + 1)) for start, end in DECADES[1:])
        return cls(captive, (births_1790s, *observed), births_1790s, population, rate)

    @staticmethod
    def assumed_1790s_births(mean_population: int, rate_per_thousand: int) -> int:
        # Ten years at a constant crude birth rate on the mid-decade population.
        return mean_population * rate_per_thousand * 10 // 1000

    def share(self, first: int, last: int, births_1790s: int | None = None) -> tuple[int, int]:
        """Captive and all births for decades indexed [first, last]."""
        denominators = list(self.all_by_decade)
        if births_1790s is not None:
            denominators[0] = births_1790s
        return sum(self.captive_by_decade[first : last + 1]), sum(denominators[first : last + 1])


def decade_rows(births: BirthReconstruction) -> list[list[str]]:
    rows = [["start_year", "end_year", "modeled_births_into_slavery", "estimated_all_us_births", "denominator_type", "share_pct"]]
    for index, (start, end) in enumerate(DECADES):
        captive, total = births.captive_by_decade[index], births.all_by_decade[index]
        rows.append([str(start), str(end), str(captive), str(total), "assumed" if index == 0 else "modeled", str(percent(captive, total, 4).normalize())])
    return rows


def migration_rows(record: dict) -> list[list[str]]:
    rows = [["start_year", "end_year", "net_migration_share_total_growth_pct", "source"]]
    for row in record["intervals"]:
        rows.append([str(row["start_year"]), str(row["end_year"]), f'{row["net_migration_share_total_growth_pct"]:.1f}', record["source_label"]])
    return rows


def write_csv(path: Path, rows: list[list[str]]) -> bytes:
    buffer = io.StringIO()
    csv.writer(buffer, lineterminator="\n").writerows(rows)
    data = buffer.getvalue().encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return data


def claims() -> list[dict]:
    """Every number the manuscript states, with the value derived from records."""
    births = BirthReconstruction.from_record(load(BIRTH_SERIES))
    found: list[dict] = []

    def claim(identifier: str, where: str, stated, derived, basis: str) -> None:
        found.append({"id": identifier, "manuscript": where, "stated": stated, "derived": derived, "agrees": str(stated) == str(derived), "basis": basis})

    for identifier, (first, last), stated_pct, stated_num, stated_den in (
        ("captive-share-1800-1849", (1, 5), "17.20", 5_167_522, 30_038_000),
        ("captive-share-1790-1849", (0, 5), "17.13", 5_571_170, 32_524_000),
        ("captive-share-1790-1859", (0, 6), "16.82", 7_437_068, 44_218_000),
    ):
        numerator, denominator = births.share(first, last)
        claim(f"{identifier}-numerator", "03-birth-into-captivity", stated_num, numerator, "sum of Hacker 2020 Table 1 col. 7 decades")
        claim(f"{identifier}-denominator", "03-birth-into-captivity", stated_den, denominator, "Haines-Sutch annual births; 1790s assumed")
        claim(f"{identifier}-pct", "03-birth-into-captivity", stated_pct, str(percent(numerator, denominator)), "numerator / denominator")

    claim("births-1790s-assumed", "03-birth-into-captivity", 2_486_000, births.births_1790s_assumed,
          f"{births.assumed_cbr_1790s}/1000 x {births.mean_population_1790s:,} x 10 years")

    record = load(BIRTH_SERIES)
    for row in record["sensitivities"]:
        rate = row["rate"]
        births_1790s = BirthReconstruction.assumed_1790s_births(births.mean_population_1790s, rate)
        for key, last in (("share_1790_1849_pct", 5), ("share_1790_1859_pct", 6)):
            numerator, denominator = births.share(0, last, births_1790s)
            claim(f"sensitivity-cbr{rate}-{key}", "03-birth-into-captivity", f"{row[key]:.2f}", str(percent(numerator, denominator)),
                  f"1790s births at {rate}/1000")

    migration = load(MIGRATION_SERIES)
    by_start = {row["start_year"]: row["net_migration_share_total_growth_pct"] for row in migration["intervals"]}
    claim("migration-share-1790-1800", "01-introduction; 05-transatlantic", "11.9", f"{by_start[1790]:.1f}", "Haines 2006 Table Aa15-Aa21 as reported")
    claim("migration-share-1850-1860", "01-introduction; 05-transatlantic", "32.3", f"{by_start[1850]:.1f}", "Haines 2006 Table Aa15-Aa21 as reported")

    register = load(CASE_REGISTER)
    claim("case-register-records", "04-whose-future-increase", 7, len(register["records"]), "documents in the purposive register")
    claim("case-register-observations", "04-whose-future-increase", 21,
          sum(len(r.get("observations", [])) for r in register["records"]), "observations across documents")

    virginia = load(VIRGINIA_SEQUENCE)
    claim("virginia-events", "02-the-future-white", 4, len(virginia["events"]), "legal-state events 1924-1930")
    claim("virginia-1926-not-enacted", "02-the-future-white", True,
          any(e["id"].startswith("VA-1926") and e["state"] != "enacted" for e in virginia["events"]), "1926 House amendment state")
    return found


def appendix_tables(births: BirthReconstruction, results: list[dict]) -> str:
    """Appendix A as Pandoc Markdown, so the printed tables are the computed ones."""
    out = ["# Appendix A. Reproduced tables {#appendix-a}", "",
           "Generated by `analysis/reproduce.py` from `data/records/`. Do not edit by hand.", "",
           "Table: Births into slavery and estimated U.S. births by decade. The 1790s denominator is assumed. {#tbl:decades}", "",
           "| Decade | Births into slavery | Estimated U.S. births | Denominator | Share (%) |",
           "|---|--:|--:|---|--:|"]
    for row in decade_rows(births)[1:]:
        out.append(f"| {row[0]}–{row[1][2:]} | {int(row[2]):,} | {int(row[3]):,} | {row[4]} | {percent(int(row[2]), int(row[3]))} |")
    out += ["", "Table: Sensitivity of the period shares to the assumed 1790s crude birth rate. {#tbl:sensitivity}", "",
            "| 1790s births per 1,000 | 1790s births | Share 1790–1849 (%) | Share 1790–1859 (%) |", "|--:|--:|--:|--:|"]
    for rate in SENSITIVITY_RATES:
        assumed = BirthReconstruction.assumed_1790s_births(births.mean_population_1790s, rate)
        out.append(f"| {rate} | {assumed:,} | {percent(*births.share(0, 5, assumed))} | {percent(*births.share(0, 6, assumed))} |")
    out += ["", f"Table: Every quantitative claim in the paper and its derivation ({sum(c['agrees'] for c in results)} of {len(results)} reproduced). {{#tbl:claims}}", "",
            "| Claim | Stated | Derived | Basis |", "|---|--:|--:|---|"]
    for c in results:
        out.append(f"| `{c['id']}` | {c['stated']} | {c['derived']} | {c['basis']} |")
    return "\n".join(out) + "\n"


def main() -> int:
    births = BirthReconstruction.from_record(load(BIRTH_SERIES))
    outputs = {
        "births-1790-1859.csv": write_csv(DERIVED / "births-1790-1859.csv", decade_rows(births)),
        "us-migration-growth-1790-1860.csv": write_csv(DERIVED / "us-migration-growth-1790-1860.csv", migration_rows(load(MIGRATION_SERIES))),
    }
    results = claims()
    (DERIVED / "claims.json").write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (ROOT / "manuscript" / "90-appendix-a-tables.md").write_text(appendix_tables(births, results), encoding="utf-8")
    failures = [c for c in results if not c["agrees"]]
    for c in failures:
        print(f"DISAGREES {c['id']}: stated {c['stated']} derived {c['derived']}", file=sys.stderr)
    print(f"{len(results) - len(failures)}/{len(results)} manuscript claims reproduced; wrote {', '.join(outputs)}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
