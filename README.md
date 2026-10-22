# Historical Fragment Priors for Genetic Programming

DSAI6707 Advanced Computational Intelligence, Project 1: Evolutionary Computation for Emerging AI.

This project studies whether reusable expressions from earlier small language model outputs help a bounded CPU genetic programming search find better online bin packing rules. The main comparison contains **four methods and 30 paired search seeds**, with Best-fit and public EoH rules as fixed quality references. The repository also includes an insertion-position study with three methods and 30 paired seeds. The GP stage makes **zero new LLM calls**; its historical corpus was produced by earlier model requests.

## Main findings

| Method | Mean B bins | SD across 30 run means | Runs improving development initialization |
| --- | ---: | ---: | ---: |
| Basic GP | 2092.312 | 1.029 | 1/30 |
| Historical fragment GP | 2089.514 | 5.021 | 12/30 |
| Fixed parent fragment sampling | 2090.507 | 3.829 | 10/30 |
| Matched random fragment GP | 2092.453 | 0.310 | 2/30 |

Historical fragment GP uses 2.939 fewer B bins than the matched random fragment control on average, with a descriptive crossed-bootstrap 95% interval of [1.242, 4.846]. The mean difference relative to fixed parent sampling is 0.992 bins, interval [-1.021, 3.172].



## Setup

The archived reference environment is Windows 11, Python 3.12.14 and NumPy 2.3.5. Use a fresh virtual environment. No Ollama service, model weights, API credential or GPU is required.

```powershell
git clone https://github.com/robert06hw/dsai.git
cd dsai
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
python -m dsai verify
python -m unittest discover -s tests -v
```

On Linux/macOS, use `python3.12 -m venv .venv` and `source .venv/bin/activate`. Pure audits and packing evaluation are portable. The preserved worker code enforces the archived 512 MiB memory limit through **Windows Job Objects**; on other operating systems it explicitly reports that this memory cap is not enforced. Subprocess timeouts still apply. Use Windows for the original resource envelope.

## Reproduce without new search

Every command below writes only into its own fresh output directory. It does not change the published input assets or archived results.

```powershell
# Verify hashes of the packaged inputs, sources and evidence.
python -m dsai verify

# Recompute all four means, SDs and paired bootstrap intervals from 3,690 rows.
python -m dsai summarize --out runs/summary

# Recreate the saved development, validation and B instances with recorded seeds.
python -m dsai generate-data --out runs/rebuilt_data

# Reconstruct both historical fragment key sets from the saved source programs.
python -m dsai extract --out runs/rebuilt_libraries

# Recreate the matched random bank and compare every entry to its frozen version.
python -m dsai rebuild-bank --out runs/rebuilt_bank

# Replay all 13,440 archived offspring constructions and population transitions.
# Saved fitness is replayed; no new search or packing evaluation occurs.
python -m dsai replay

# Re-evaluate all 120 final outputs and three references on B.
# Compare bins and complete decision hashes against every archived row.
python -m dsai evaluate --out runs/B_recheck --compare-archived
```

The generated data in `generate-data` are a reproduction of already viewed sequences, not a new holdout. All 30 B instances are included once and shared across the search seeds.

For a smaller conversion check before the full 1,166-program verification:

```powershell
python -m dsai verify-conversion --limit 5 --out runs/conversion_smoke
python -m dsai verify-conversion --out runs/conversion_full
```

This compares original, expanded and conservatively normalized scores on the saved probes and every pilot_dev packing state, then checks complete packing decisions.

## Run the bounded search again

This is optional. It creates a **new reproduction run** and never appends observations to the archived study.

```powershell
# Four methods, one of the frozen paired seeds, 128 nominal slots per method.
python -m dsai run --seeds 303 --out runs/search_303

# The complete four-method, 30-seed configuration.
python -m dsai run --out runs/search_all

# Evaluate the outputs only after search and development-based selection finish.
python -m dsai evaluate --programs runs/search_all/final_candidates --out runs/search_all_B
```

Initialization programs, scores and schedules are reused from the frozen common initialization. Each search still charges 16 initial slots plus 112 new candidate slots. New initial LLM calls or new random initialization draws are not made. For interrupted runs use the exact same options and add `--resume`; the configuration and package manifest must match. At most four workers are allowed. B never selects the final candidate; pilot_val is diagnostic only.

## Repository layout

The insertion-position study uses the initial 10 seeds and the first 20-seed extension. Its combined results are in [`fragment_position_gp_equal_time_20seed_extension_01/aggregate/`](fragment_position_gp_equal_time_20seed_extension_01/aggregate/). The source cohorts are [`fragment_position_gp_equal_time_01/`](fragment_position_gp_equal_time_01/) and [`fragment_position_gp_equal_time_20seed_extension_01/`](fragment_position_gp_equal_time_20seed_extension_01/). The shared core is [`fragment_gp_limited_01/`](fragment_gp_limited_01/). See [position GP data and reproduction](docs/POSITION_GP.md) for verification, trace restoration, output evaluation, and search commands.

| Location | Contents |
| --- | --- |
| `src/dsai/` | Portable CLI, auditing, aggregation and orchestration |
| `src/dsai/frozen/` | Byte-preserved original evaluator, typed trees, search operators and extraction worker |
| `configs/study.json` | Four methods, 30 seeds, budgets, operators and resource settings |
| `assets/data/` | Saved pilot_dev, pilot_val and B ordered item sequences |
| `assets/source_programs/` | 1,242 historical valid programs |
| `assets/libraries/` | Frozen raw/clean historical libraries and matched random library |
| `assets/initialization/` | The 480 shared initial slots and their saved evaluations |
| `assets/final_candidates/` | All 120 frozen final programs |
| `assets/program_manifest.json` | Final program and reference hashes |
| `results/aggregate/` | 120-run summaries, 3,690 B instance rows and paired comparisons |
| `results/search/` | Attempts, parent reproduction, curves and complete checkpoints |
| `results/candidate_ledger.jsonl` | Every archived child expression and construction identity |
| `results/lineage/` | First improvements, ancestor operations and fragment provenance |
| `provenance/` | Data manifests, old LLM prompts/options/responses, matching and cost evidence |
| `archives/` | Selected original implementation and lock records; not the portable execution entry points |
| `third_party/eoh/` | Pinned official instance generator, source revision and retained MIT license |
| `docs/` | Reproduction details, experimental protocol and coursework mapping |

## Coursework deliverables

The source code, setup instructions, data preparation, execution, evaluation and supporting raw/processed evidence are supplied here. `docs/DELIVERABLES.md` maps them to the assignment. A complete research report and its required recent-literature review are separate submission items; this repository does not claim to provide them. Word documents are not included.

See [the experimental protocol](docs/EXPERIMENT.md), [reproduction details](docs/REPRODUCIBILITY.md) and [third-party attribution](THIRD_PARTY_NOTICES.md). Project-specific code is supplied for course assessment; no blanket open-source license is asserted for all contents. The included EoH-derived material retains its own license and attribution.
