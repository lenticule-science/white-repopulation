# Reproducing the paper

## Numbers (no dependencies beyond Python 3.11+)

    python -m analysis.reproduce     # writes data/derived/, checks every stated number
    python -m unittest discover -s tests -t .

`data/derived/claims.json` lists each claim, the value the manuscript states,
the value derived from the records, and the arithmetic used.

## Figures

    python -m pip install -r requirements.txt
    python -m analysis.figures

SVG output is byte-reproducible: it uses a fixed hash salt and no timestamps.

## Manuscript

    make paper        # PDF, HTML, DOCX and JATS into build/

The pinned toolchain is the one CI uses (`.github/workflows/build.yml`). Each
build writes `build/build-receipt.json`, which records the toolchain versions,
the exact arguments and the SHA-256 of every input and output. The receipt is
projected into `provenance/prov.ttl` (W3C PROV-O).

HTML, DOCX and JATS outputs are byte-reproducible under `SOURCE_DATE_EPOCH`.
PDF output from LaTeX is reproducible only to the limits documented by the
renderer service. Each release lists its PDF digest, and a reader should
compare against that digest rather than expect an identical rebuild on a
different TeX installation.

## Provenance of the v0.1.0 bundle

The unreleased v0.1.0 candidate bundle recorded SHA-256 digests for its CSV
tables. Those digests were computed over CRLF line endings. The test
`test_tables_match_the_v0_1_0_release_bundle` regenerates both tables from the
records and reproduces those exact digests.
