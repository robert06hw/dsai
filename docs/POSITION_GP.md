# Position GP data and reproduction

The repository contains two studies. The historical fragment study has four methods and 30 paired seeds. The position study has three methods and 30 paired seeds, formed from the initial 10 seeds and the first 20-seed extension.

## Find the files

| Directory | Contents |
| --- | --- |
| `results/aggregate/` | Historical study: 120 run summaries and 3,690 B instance results |
| `fragment_position_gp_equal_time_01/` | Position study: initial 10 seeds, 30 runs, source, configuration, outputs, and results |
| `fragment_position_gp_equal_time_20seed_extension_01/` | Position study: first 20-seed extension, 60 runs, source, configuration, outputs, and results |
| `fragment_position_gp_equal_time_20seed_extension_01/aggregate/` | Position study: combined 30 seeds, 90 run summaries, and 2,790 B instance results |
| `fragment_gp_limited_01/` | Shared typed GP implementation, historical fragment library, and historical tree index |

The historical study is already at the repository root. There is no nested copy of the repository.

The main position tables are `all30_threemethod_run_summary.csv`, `all30_threemethod_B_instance_results.csv`, `all30_threemethod_method_summary.csv`, and `all30_threemethod_comparisons.json`. They are in the combined results directory above. Each position cohort also contains `final_candidates/`, `frozen/`, `test_data/`, `config.json`, and `REPORT.md`.

The historical study and position study use separate B instance collections. Use the saved instance identifiers to join results within each study.

## Verify the package

Install the dependencies from the repository root:

```powershell
python -m pip install -e .
python -m dsai verify
python tools/position_gp.py verify
```

The position verifier checks the copied file hashes, archive hashes and member lists, distinct seed count, run count, shared position test data, and combined result row count. To read and hash every archived member, run:

```powershell
python tools/position_gp.py verify --deep
```

`distribution_manifest.json` records the files supplied in each added directory. `trace_archive_index.json` lists the original relative path and SHA-256 of every compressed file. The package retains the original execution locks as records of the original runs. The current repository manifest verifies the distributed files, including the later documentation edits.

## Restore the complete traces

The full search traces and the shared core's large intermediate directories are stored as `trace_archive_*.zip`. The remaining files are directly browsable. Restore all archived members into a new directory:

```powershell
python tools/position_gp.py restore --out runs/restored_position
```

The restore command copies the directly browsable files, extracts the archived paths, and checks every restored member against its recorded hash. Existing output directories are rejected.

## Check the saved final programs

Run a small check of the first paired seed in each position cohort. This checks all three methods on the first saved B instance:

```powershell
python tools/position_gp.py smoke --out runs/position_smoke
```

Re-evaluate every position output and the fixed references on the saved position B instances:

```powershell
python tools/position_gp.py evaluate --out runs/position_B_recheck
```

Both commands compare bin counts and complete decision hashes with the archived instance results. They write to a new directory and make no search or LLM requests. Identical program bytes share evaluation results.

## Reproduce the search on Windows

The position methods are `uniform_position_gp`, `structure_position_gp`, and `behavior_A_position_gp`. Each run has a 120-second budget and at most 16 retained parents. The frozen initialization plans, ranking models, and state collection are supplied.

Prepare a new reproduction without starting it:

```powershell
python tools/position_gp.py reproduce --cohort original10 --out runs/position_original10 --prepare-only
```

Start a fresh reproduction of either cohort:

```powershell
python tools/position_gp.py reproduce --cohort original10 --out runs/position_original10_search
python tools/position_gp.py reproduce --cohort extension20 --out runs/position_extension20_search
```

The launcher creates new execution locks for the copied runner and its dependencies. It changes the repository and asset paths for the new checkout. The proposal, ranking, selection, and timing code comes from the supplied runner. The archived runs remain in their original directories. Windows is required for the original Job Object process and memory controls.
