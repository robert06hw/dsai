# Experimental protocol

## Question and comparison

Does a historical expression prior improve bounded GP from Best-fit plus basic random initialization? Can the benefit be separated from having a type/size/depth-matched random library, and from fixed-parent fragment sampling?

The four archive identifiers are `basic_gp`, `raw_fragment_gp`, `fixed_parent_random` and `matched_random_fragment_gp`. The original 30 seeds are 303, 404, 505, and multiples of 101 from 606 through 3232. They form 120 paired method-seed runs.

## Shared search

- 16 nominal initialization slots per seed: Best-fit plus 15 basic random expressions. All methods reuse the exact programs and evaluations. There are 480 physical initial candidates, all valid. Exact structural deduplication leaves 8–15 initial parents. The maximum retained population is 16.
- Every initial best has pilot_dev mean 2066.4 bins. The historical best is a fixed reference outside initialization.
- Each run adds 112 child slots: a shuffled exact quota of 56 crossover, 39 subtree replacement and 17 constant mutation attempts.
- Uniform parent sampling with replacement. Typed crossover samples a receiver expression location and a compatible donor subtree. The fragment methods draw a bank fragment for half of replacements; otherwise they use the basic random grammar. Basic GP always generates a basic replacement.
- Constant mutation adds Normal(0, 5) to a uniformly selected numeric literal. Construction failures do not receive retries or repair.
- The emitted full numeric vector expression is limited to 64 expression nodes and depth 8. Negative literal serialization is included in counting.
- Every valid child completes all five pilot_dev instances. A duplicate still consumes a slot and receives a fresh full evaluation. Invalid and oversized constructions consume slots.
- GP retains exact-AST-unique elites ordered by mean bins, emitted nodes and execution key, with at most 16 parents. Fixed-parent sampling retains its initial parent pool while saving its best discovered candidate.
- Outputs are chosen by pilot_dev alone. The diagnostic pilot_val is read after all searches. B is evaluated after outputs are frozen.

This yields 15,360 nominal slots and 13,920 physical attempts: 480 common initial candidates plus 13,440 children. The matched random method adds 3,360 physical attempts and reuses 480 initial slots.

## Historical prior and random matching

Five historical model experiments made 2,496 requests using Qwen2.5-Coder 3B Instruct Q4_K_M through Ollama 0.35.1. The archived digest and exact request records are under `provenance/historical_llm/`. Generation used temperature 0.7, top_p 0.9, top_k 40, num_predict 512 and num_ctx 2048. Those are prior costs. There is no model client in the current portable experiment.

The selected corpus contains 1,242 valid unique programs and 2,315 origin records. Local variables are expanded without reassociation. Numeric scalars, numeric vectors and scalar/vector masks are checked conservatively. Unsupported operations are excluded with reasons. There is no source quality threshold or finite-behavior pruning.

Of 1,242 programs, 1,166 convert and pass archived full-pilot equivalence checks (93.88%). Their raw and cleaned libraries each contain 1,947 structural entries. Complete supported historical scoring roots are blocked under conservative normalization: 707 entries are blocked and 1,240 are eligible. The eligible types are 1,024 V, 117 S and 99 BV. Sampling is uniform by entry within type, not occurrence-weighted.

The random bank independently generates one unique legal expression for each eligible slot, exactly matching type, emitted node count and depth. Bank seed 918273645 is split by slot with SeedSequence channel 901. Construction uses no packing-quality selection. It takes 1,283 attempts with 43 structural duplicate rejections to make 1,240 entries, with two recorded natural AST overlaps. Thirty oversized/overdeep bank slots are retained in both views and may consume rejected candidate attempts. Complete historical scoring roots are excluded from random insertion too.



## Data and evaluator

Capacity is 100, with 5,000 items per instance and saved arrival order. The underlying Weibull has shape 3 and scale 45, clipped to [1,100]. pilot_dev uses seeds 6001–6005 and pilot_val 6101–6105; these apply floor. B uses 30 seeds 800001–800030 with the pinned official generator's NumPy round (ties to even). Every instance has its own PCG64 generator. Floor versus round is preserved explicitly.

The official EoH repository commit is `472545785c936dcfc863d2bc0d6109cf23c7ce62`. Its generator SHA-256 is `02556b60c67e769aa8f012783244eb81861f8a1d59f0e90756466ab8c6315c52`. These are same-setting new item sequences, not the original paper's five item lists. The saved historical nonoverlap audit compares B with 447 unique ordered sequences from 37 files and records zero overlap. A new generation audit also checks the packaged splits against one another.

Only opened feasible bins are scored. No feasible bin means open one new bin. Otherwise the function receives read-only feasible float64 capacities and returns a same-length finite numeric ndarray. The evaluator applies argmax and chooses the earliest original bin on ties. It does not sort items or accept a scalar/index in place of scores.

Fixed reference means on pilot_dev / pilot_val / B are:

| Rule | pilot_dev | pilot_val diagnostic | B |
| --- | ---: | ---: | ---: |
| Best-fit | 2066.4 | 2070.2 | 2092.500 |
| EoH | 2059.4 | 2063.8 | 2085.900 |
| Historical best | 2044.8 | 2049.2 | 2069.833 |

## Statistical and cost interpretation

The primary reported quality is mean bins over B for each development-selected output. Methods weight all 30 search seeds equally; SD is across 30 run means. Paired differences are control bins minus historical fragment GP bins, with positive values favoring history. Win/tie/loss counts compare seed means on the same instances.

Intervals use 10,000 crossed bootstrap draws with PCG64(900002), independently resampling 30 seeds and 30 instances and averaging the crossed matrix. All methods use identical draws. The random control was added after earlier results were examined and B was already viewed.

The archived environment is Python3.12.14, NumPy2.3.5 and Windows11 build26200, four workers, 120 seconds per worker and 512 MiB per Windows Job Object, with one BLAS thread per worker. Batch wall times, summed evaluation times, shared initialization accounting, historical preparation and B evaluation are separate quantities. Different batches/background loads prevent reading timing differences as controlled hardware speedups. See the original cost records and `results/aggregate/additional_cost_accounting.json` for scope and exclusions.
