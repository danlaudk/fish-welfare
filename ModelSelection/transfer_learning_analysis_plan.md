# Transfer Learning Analysis Plan: Dense Campaign → Sparse Irregular Monitoring

**Date**: 2026-04-24
**Context**: Designing a Hierarchical Bayesian Binomial model to transfer weather→DO knowledge from 17 densely-monitored campaign ponds (source, ~50 days, Nov 2025–Jan 2026) to 235 irregularly-sampled ponds (target, ~460 non-sequential days, Jul 2021–Jan 2026).

---

## Problem Framing

**Source domain**: 17 campaign ponds with 15-min DO/pH/temp sensors, 64 days, regular dense coverage. 25 engineered features (23 weather + 2 calendar). Single Open-Meteo grid for Eluru.

**Target domain**: 235 Eluru ponds , sampled irregularly by field workers at mornings and evenings — biased, non-sequential, varying pond counts per day. Same Open-Meteo weather grid.

**Goal**: Predict Pr(bad_day | weather) for any Eluru day, where "bad_day" means dangerously low dissolved oxygen across the region's ponds.

---

## What Should Be Transfer-Learned

### Recommended: Shared weather slopes (β) via joint hierarchical model

The **transferable knowledge** is the relationship between weather features and the probability that a pond has low DO. Both domains share the same weather grid, so the weather→DO coupling should be the same (up to domain-specific intercepts for prevalence differences).

**Simultaneously transfer-learned:**
1. **Weather regression coefficients (β)**: The slopes relating 7–10 core weather features to logit(p). These are the same physical relationships in both domains.
2. **Seasonal modulation**: Calendar features (doy_cos, month_sin) encode the annual DO cycle. The source only covers winter — the target spans 4+ years. The shared seasonal structure is transferable.
3. **Overdispersion parameter (κ)**: If using Beta-Binomial, the pond-to-pond heterogeneity within a day (captured by κ) is partially transferable.

**NOT transferred (domain-specific):**
- **Intercepts (α_d)**: Absorb the massive prevalence shift (source: ~61% of ponds below 3 mg/L on typical day; target: ~10% of region-days are "bad").
- **Pond-level random effects**: Source has 17 continuously-monitored ponds; target has 235 intermittently-sampled ponds. Pond identities don't transfer.


### Feature partitioning for transfer

| Feature group | # features | Available in source? | Available in target? | Transfer role |
|---|---|---|---|---|
| G1: Overnight weather (0–6AM) | 1 | ✓ | ✓ | Shared β |
| G2: Early morning weather (6–8AM) | 2 | ✓ | ✓ | Shared β |
| G3: Night reaeration (19–06) | 2 | ✓ | ✓ | Shared β |
| G4: Prior daytime weather | 2 | ✓ | ✓ | Shared β |
| G5: 3-day rolling/lag weather | 6 | ✓ | ✓ | Shared β |
| G10: Evening/beam proxy | 2 | ✓ | ✓ | Shared β |
| Calendar (doy_cos, month_sin) | 2 | ✓ | ✓ | Shared β |
| G9: Pond hist trends (>48h) | 6 | ✓ | **✗** | Shared β |
| Pond outcome-adjacent (log_n_ponds) | 1 | ✓ | ✓ | Domain-specific |


---

## Proposed Outcome Variable Definitions

### Count-Based Binomial Outcome

Instead of binary bad_day, model the **count of low-DO ponds** directly:

```
y_dt ~ Binomial(n_dt, p_dt)     [or Beta-Binomial for overdispersion]
logit(p_dt) = α_d + X_t β
```

where:
- y_dt = number of ponds with morning DO < 2.5 mg/Lon day t in domain d
- n_dt = number of ponds sampled on day t
- p_dt = probability that a randomly-sampled pond has DO < 2.4 mg/L

**Advantages of this formulation:**
- **Domain-differentiated**: Both domains model the SAME structure — Pr(pond DO < 2.4 | weather); Pr(pond DO < 3 | weather) . The two different thresholds account for some structural difference.
- **Naturally handles different n_ponds**: Days with 17 ponds contribute more information than days with 3. The Binomial likelihood weights observations by their precision.
- **No percentile computation needed**: No need to decide what "bottom X%" means. The operational decision ("is this a bad day?") is derived from the posterior predictive: compute Pr(fraction_low ≥ 0.6 | weather, posterior) as a derived quantity.
- **Preserves count information**: 12/17 ponds below 3 is much more informative than a binary "bad day = 1".
- **Pseudo-replication solved**: Source days with all 17 ponds contribute Binomial(17, p), not 17 independent Bernoullis.

**Operational "bad day" definition** (derived, not modeled):
- Compute posterior predictive P(fraction_low ≥ threshold | weather_t) for any desired threshold
- Threshold can be chosen operationally (e.g., ≥50% of ponds, or ≥60%) without retraining

---

## Planned Analyses (10 Notebooks)

### Phase 1: Data Alignment & Feature Availability (parallel)

#### NB01: `01_source_target_data_alignment.ipynb`
**Question**: How well do the source and target feature spaces overlap, and which features are computable in both domains?

**Analyses**:
- Load source (data_campaign_flat_clean.csv) and target (water_quality.csv, Eluru morning non-follow-up) datasets
- For each of the 25 features: can it be computed from target data? Classify as {shared, source-only, target-only}
- For shared weather features: compare distributional overlap between source period (Nov–Jan) and full target period (Jul 2021–Jan 2026) using KS tests, KL divergence
- Quantify covariate shift: are weather conditions during source period representative of full annual cycle?
- Visualise: side-by-side density plots for each shared feature in source vs target period

**Output**: Feature availability matrix, covariate shift magnitude per feature, seasonal coverage gaps

---

#### NB02: `02_outcome_variable_comparison.ipynb`
**Question**: How do different outcome formulations compare for transfer feasibility? Is the Binomial count formulation better than binary percentile?

**Analyses**:
- Compute 6 candidate outcomes for both domains:
  1. Binary: bad_day at 10th percentile of mean DO (current target definition)
  2. Binary: bad_day at 20th percentile (current source definition)
  3. Binary: bad_day at fixed threshold (mean_do < 2.5 mg/L)
  3. Binary: bad_day at fixed threshold (mean_do < 3.1 mg/L)
  4. Count: n_low / n_ponds (fraction of ponds with DO < 3)
  5. Count: n_low / n_ponds (fraction with DO < 2.5)
  6. Continuous: region-day mean morning DO
- For each: compute prevalence, distributional properties, sensitivity to n_ponds cutoff
- Cross-domain concordance: for days that exist in both domains (source campaign days also have target-domain WQ measurements from some of the 235 ponds), do outcomes agree?
- Information content: effective sample size under each formulation
- Simulate: how much does the Binomial formulation improve power over binary for detecting weather effects?

**Output**: Recommended outcome variable with justification; concordance analysis

---

#### NB03: `03_sampling_bias_characterisation.ipynb`
**Question**: Is target-domain sampling biased in ways that affect the weather→DO relationship?

**Analyses**:
- Compare weather distributions on sampled vs non-sampled days (using full Open-Meteo hourly data)
- Are field workers more likely to visit on certain weather conditions? (logistic regression: sampled_day ~ weather)
- Temporal bias: are certain months/seasons over-represented? (histogram of sampling dates vs calendar)
- Pond selection bias: are certain ponds visited more frequently? Do frequently-visited ponds have different DO distributions?
- Morning timing bias: does measurement hour vary systematically with weather or DO level?
- Propose: inverse probability weighting (IPW) or post-stratification corrections if bias is substantial

**Output**: Bias magnitude for each weather feature; IPW weights if needed; recommended correction strategy

---

### Phase 2: Feature Engineering for Transfer (depends on NB01)

#### NB04: `04_transferable_feature_engineering.ipynb`
**Question**: What is the optimal shared feature set that works in both domains?

**Analyses**:
- Start from the 25 selected features, re-assess correlations with the Binomial count outcome (not the binary bad_day)
- Feature selection specifically for the count-based outcome: Spearman correlation of each weather feature with y/n (fraction low) instead of binary
- Test whether the 7-feature "core" from the transfer_learning_methods_review.md is sufficient, or whether additional features help
- Multicollinearity check: VIF analysis on the shared feature set
- Compute all shared features for the full target period (460+ days) and verify no missing values

**Output**: Final shared feature matrix (n_days × p_features) for both domains; recommended feature set (7–15 features)

---

#### NB05: `05_seasonal_transferability.ipynb`
**Question**: Does the weather→DO relationship hold across seasons, or is it winter-specific?

**Analyses**:
- The source covers only Nov–Jan (winter). Target spans Jul 2021–Jan 2026.
- Split target data by season (monsoon: Jun–Sep, post-monsoon: Oct–Nov, winter: Dec–Feb, pre-monsoon: Mar–May)
- For each season: compute weather→DO correlations and compare to source-period correlations
- Test for interaction: weather × season effects on DO
- If relationships are season-specific: propose season-gated priors (tighter priors on β in winter when source data supports them, wider in monsoon)
- Quantify: what fraction of target observations fall outside the source's weather support?

**Output**: Season-specific correlation matrices; evidence for/against season-invariant β; prior width recommendations by season

---

### Phase 3: Model Design Analysis (depends on NB02, NB04)

#### NB06: `06_overdispersion_and_correlation_structure.ipynb`
**Question**: Is the Binomial model adequate, or do we need Beta-Binomial? Is there temporal autocorrelation?

**Analyses**:
- Fit simple Binomial GLM (logit link) to target domain: y_t ~ Binomial(n_t, logistic(α + X_t β))
- Check overdispersion: compare observed variance of y/n to Binomial-expected variance; Pearson chi-squared test
- If overdispersed: fit Beta-Binomial; estimate concentration parameter κ
- Temporal autocorrelation: ACF/PACF of Pearson residuals from the Binomial fit
- If autocorrelated: propose AR(1) structure on the latent logit-scale, or just use temporal blocking for cross-validation
- Examine: are residuals heteroscedastic by season? By n_ponds?

**Output**: Overdispersion test result; recommended likelihood (Binomial vs Beta-Binomial); temporal correlation structure

---

#### NB07: `07_prior_sensitivity_and_power_analysis.ipynb`
**Question**: How informative should the source-derived priors be? How much does the source actually help?

**Analyses**:
- Fit source-only Bayesian Binomial regression using the shared feature set (PyMC or numpyro)
- Extract posterior distributions of β from the source fit → these become informative priors for the target
- Power prior approach: vary the discount factor a₀ ∈ {0, 0.1, 0.3, 0.5, 0.7, 1.0} to control how much source information transfers
- For each a₀: fit the target model; compare ELPD (expected log predictive density) via LOO-CV
- Simulation study: generate synthetic target data with known β; measure how quickly the target posterior recovers the true β with vs without source prior
- Determine: is the source posterior informative enough to beat a weakly informative prior? (given the very weak signal, ρ < 0.1)

**Output**: Optimal discount factor a₀; evidence for whether source prior helps or hurts; recommended prior specification

---

### Phase 4: Validation Strategy (depends on Phase 3)

#### NB08: `08_cross_validation_design.ipynb`
**Question**: How should we evaluate the transfer model given non-sequential, irregularly-sampled target data?

**Analyses**:
- Temporal blocking: define CV folds that respect temporal order (no leakage from future)
- Block sizes: test 30-day, 60-day, and 90-day blocks; assess stability of held-out metrics
- Stratified assessment: does performance vary by season? By n_ponds? By year?
- Proper scoring: use Brier score and log-loss (proper scoring rules for calibration) rather than AUC alone
- Calibration analysis: reliability diagrams for predicted Pr(bad_day) vs observed fraction
- Compare evaluation metrics: AUC vs Brier score vs ELPD for model selection
- Design the final train/test protocol: chronological split with the most recent 20% as held-out test set

**Output**: Recommended CV scheme; baseline performance metrics; evaluation protocol specification

---

#### NB09: `09_baseline_models.ipynb`
**Question**: What are the baselines the hierarchical Bayesian model must beat?

**Analyses**:
- **Baseline 1: Marginal rate** — predict Pr(bad_day) = overall prevalence (no weather info)
- **Baseline 2: Seasonal rate** — predict Pr(bad_day) = month-specific prevalence
- **Baseline 3: Target-only Binomial GLM** — fit β from target data alone (no transfer)
- **Baseline 4: Pooled Binomial GLM** — pool source + target with domain intercept (simple pooling, no hierarchical structure)
- **Baseline 5: Persistence** — use yesterday's y/n as tomorrow's predicted probability
- For each baseline: compute Brier score, log-loss, AUC, calibration on the held-out test set
- This establishes the performance floor. If the hierarchical Bayesian model can't beat Baseline 2 (seasonal rate), weather features are not useful.

**Output**: Baseline performance table; performance floor for the hierarchical model

---

### Phase 5: Model Prototyping (depends on all above)

#### NB10: `10_hierarchical_bayesian_prototype.ipynb`
**Question**: Does the full hierarchical Bayesian Binomial/Beta-Binomial model improve on baselines?

**Analyses**:
- Implement the recommended model in PyMC/numpyro:
  ```
  y_dt ~ BetaBinomial(n_dt, μ_dt * κ, (1 - μ_dt) * κ)   [or Binomial]
  logit(μ_dt) = α_d + X_t β
  β ~ N(β_source_posterior * a₀, σ²_adjusted)
  α_source ~ N(0, 5)
  α_target ~ N(0, 5)
  ```
- MCMC diagnostics: R̂, ESS, trace plots, divergences
- Posterior analysis: which weather features have non-zero coefficients? (examine 95% credible intervals)
- Posterior predictive checks: does the model reproduce the observed y/n distribution?
- Held-out evaluation: Brier score, log-loss, AUC, calibration on test set
- Compare against all baselines from NB09
- Sensitivity analysis: how does performance change if we drop the source prior entirely?
- Operational output: for each test-set day, produce Pr(fraction_low ≥ 0.5 | weather) with 90% credible interval

**Output**: Full model specification; posterior summaries; comparative performance table; go/no-go recommendation for deployment

---

## Dependency Graph

```
NB01 ─┬──→ NB04 ──→ NB06 ──→ NB07 ──→ NB10
      │              ↑                   ↑
NB02 ─┤              │                   │
      │              │                   │
NB03 ─┘        NB05 ─┘             NB08 ─┤
                                         │
                                   NB09 ─┘
```

**Phase 1** (NB01–NB03): Parallel, no dependencies
**Phase 2** (NB04–NB05): Depend on NB01; can run in parallel
**Phase 3** (NB06–NB07): Depend on NB02 + NB04; sequential
**Phase 4** (NB08–NB09): Depend on NB04 + NB06; can run in parallel
**Phase 5** (NB10): Depends on NB07 + NB08 + NB09

---

## Key Design Decisions Summary

| Decision | Choice | Rationale |
|---|---|---|
| What to transfer | Weather slopes (β) via shared priors | Same weather grid; physical relationship is domain-invariant |
| Transfer mechanism | Power prior / informative Bayesian prior from source posterior | Principled; allows controlling transfer strength via a₀ |
| Outcome variable | Binomial count (n_low, n_total) not binary | Preserves information; handles varying n_ponds; aligns domains |
| Low-DO threshold |  3 mg/L (and 2.5mg/L in source) | Biologically meaningful;  no percentile ambiguity |
| Likelihood | Beta-Binomial (pending overdispersion test in NB06) | Handles correlated pond outcomes within a day |
| Feature set | ~23 shared weather features (weather-only) and pond-history features; computable in both domains despite some observations will have imputed values if recent history is unavailable |
| Seasonal handling | Season-gated prior widths on β | Source covers winter only; transfer should be weaker in monsoon |
| Evaluation | Brier score + calibration on chronological held-out set | Proper scoring rules for probabilistic predictions |

---

## Data Files Referenced

| File | Role |
|---|---|
| `data/data_campaign_flat_clean.csv` | Source domain: 17 campaign ponds, 15-min resolution |
| `data/water_quality.csv` | Target domain: 235 Eluru ponds, irregular sampling |
| `data/open_meteo_24.csv` | Hourly weather for Eluru (shared across domains) |
| `data/weather_features.csv` | Pre-engineered weather+DO features |
| `data/enrolled_ponds_2026-02-02.csv` | Pond metadata (area, depth, stocking) |
| `data/feature_matrix.csv` | Source domain feature matrix from feature_engineering.ipynb |
| `data/feature_correlations.csv` | Feature correlation results |
