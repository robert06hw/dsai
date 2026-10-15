# Reproduction and artifact integrity

## Two kinds of reproduction

1. **Audit the reported experiment** with `verify`, `summarize`, `generate-data`, `extract`, `rebuild-bank`, `replay` and `evaluate --compare-archived`. These commands read frozen observations and reproduce the stated transformations or evaluations. They never change the historical result tables.
2. **Run GP again** with `run`. This makes new candidate attempts in a distinct output directory under the same locked choices. It is optional and is not done by the default test suite. Reproduction outputs are never merged into the reported 120 runs.

## Why adapters are necessary

The selected original scripts expect sibling archive directories and Windows source paths. Those scripts are preserved byte-for-byte in `archives/` and `src/dsai/frozen/`, but their original `prepare` commands are not the repository entry points. The portable layer redirects ROOT locations, supplies the shipped frozen inputs and invokes the unchanged operator, selection, packing, extraction-worker and matched-bank functions. It creates required output directories before invoking workers. Frozen sources are never rewritten in place.

The three original methods use the original historical `run_one` and library loader. The random method uses its own original `run_one` and random loader. Their worker function ASTs are equal; the worker copy is used only for isolated evaluation, never method selection. The 112-step schedule is not shortened by a smoke run, construction failure or duplicate. A shared initial result is a recorded budget slot even when physical evaluation is reused.

The `replay` command regenerates every candidate from archived parents and RNG channels, checks execution/internal keys, expressions, operators, receiver/donor identities, fragment choices and construction errors, then injects its saved fitness and checks both elite transitions and final best identity. This verifies 13,440 actual constructions in all 120 runs without adding a search observation or packing evaluation. Original checkpoint timing and worker-result metadata remain historical.

## Outputs and preservation

Use a fresh `--out` for each command. Adapters reject outputs under immutable asset/evidence/source directories. `run --resume` requires identical seeds, methods, workers and package-manifest identity and reuses the original per-attempt files/checkpoints. No command deletes source directories or automatically overwrites a nonempty result directory. A valid duplicate still receives full packing in a new search.

`evaluate --compare-archived` matches bins, chosen-bin trace hash and chosen-capacity hash for all 3,690 shipped B records. New runtime values are expected to differ; they are not compared with archived wall clocks. `--save-traces` optionally saves the complete newly evaluated index/capacity arrays in ignored execution outputs. Original bulky NPZ packing traces are not necessary to recompute reported statistics: archived hashes and the exact evaluator, programs and item sequences are supplied. Complete population checkpoints and child expressions are included for source reconstruction.

`extract` reconstructs all 1,166 supported full trees and checks their execution keys against the registry, then reconstructs both 1,947-entry fragment key sets. It retains all input-resolved subexpressions and does not use Worst-fit or probe-ranking pruning. Source occurrence metadata in this portable reconstruction is rederived; the frozen libraries and original coverage/score checks remain authoritative. `verify-conversion` reruns the full original score and packing equivalence procedure in resource-limited subprocesses. The complete 1,166-program verification is more expensive than a five-program check.

`rebuild-bank` calls the original bank builder with only its source/output roots redirected and requires the resulting list of all entries to equal the frozen bank. All random syntax probes are interface checks; no B/dev quality chooses a bank member.

## Hashes and provenance

- `REPRODUCIBILITY_MANIFEST.json` hashes every published project file except itself and ignored Git/execution files. `python -m dsai verify` checks this manifest.
- `provenance/source_files.json` records the original relative source and hash of selected byte-preserved copies. Original Windows source paths within archival records are provenance only; portable commands do not resolve them.
- `archives/*/manifest.json` and original lock JSONs are historical archive records. They include original archive inventories, some of whose bulky traces are not distributed. They are not manifests of this repository. Use the package manifest to validate the distributed set.
- `assets/program_manifest.json` pins all 120 selected programs and three fixed references.
- Git attributes disable newline conversion for byte-preserved assets, evidence, reports and frozen source files so a clone does not invalidate their hashes.

The code makes no new model calls. Historical prompt/response records and their generation options are evidence of prior work. No credentials, model weights, virtual environments or user application caches belong in this repository.
