# Data Dictionary

This document describes all columns in each dataset.

## water_quality.csv

Water quality measurements collected during farm visits.

| Column | Type | Description |
|--------|------|-------------|
| `pond_id` | string | Anonymized pond identifier |
| `region` | string | Geographic region (West Godavari or Nellore) |
| `date` | date | Date of measurement (YYYY-MM-DD) |
| `measurement_type` | string | Time of day (Morning or Evening) |
| `time` | time | Exact time of measurement |
| `group` | string | Farmer group (e.g., "Regular ara pond", "Focus group 3") |
| `pond_type` | string | Treatment or Control |
| `staff_member` | string | FWI staff member who recorded the measurement |
| `equipment` | string | Measurement equipment used |
| `is_follow_up` | boolean | Whether this is a follow-up measurement |
| `dissolved_oxygen_mg_l` | float | Dissolved oxygen in mg/L |
| `ph` | float | pH level |
| `ammonia_tan_mg_l` | float | Total Ammonia Nitrogen in mg/L (old method, until Aug 2025) |
| `ammonia_nh3_mg_l` | float | Unionized ammonia (NH₃) in mg/L (new method, from Aug 2025) |
| `ammonia_tan_as_nh3_mg_l` | float | TAN expressed as NH₃ in mg/L (transition tracking, from Aug 2025) |
| `turbidity_cm` | float | Turbidity measured by Secchi disk in cm |
| `temperature_c` | float | Water temperature in Celsius |
| `water_color` | string | Visual water color description |
| `tds_ppt` | float | Total dissolved solids in ppt |
| `weather` | string | Weather conditions during measurement |
| `is_in_range` | boolean | Whether all parameters are in acceptable range |
| `parameters_out_of_range` | string | List of parameters outside acceptable range |
| `corrective_action_requested` | string | Corrective actions recommended to farmer |
| `corrective_action_implemented` | boolean | Whether farmer implemented the actions |
| `corrective_action_effective` | boolean | Whether water quality improved after actions |

### Acceptable Ranges (Welfare Standard v2)

| Parameter | Acceptable Range |
|-----------|------------------|
| Dissolved Oxygen | > 4 mg/L (morning), > 5 mg/L (evening) |
| pH | 7.0 - 9.0 |
| Ammonia (TAN) | < 0.5 mg/L (old threshold, until Aug 2025) |
| Ammonia (NH₃) | < 0.05 mg/L (new threshold, from Aug 2025) |
| Temperature | Species-dependent |

### Ammonia Measurement Protocol Change (August 2025)

In August 2025, FWI changed how ammonia is measured. For details, see: [Changes in our Ammonia Measurement Protocols](https://www.fishwelfareinitiative.org/post/ammonia-change)

**Why the change?** Unionized ammonia (NH₃) is the form that is directly toxic to fish. The proportion of toxic NH₃ in total ammonia increases with pH and temperature, so measuring only Total Ammonia Nitrogen (TAN) gives an incomplete picture of ammonia toxicity.

**The three ammonia columns:**

| Column | Period | Description |
|--------|--------|-------------|
| `ammonia_tan_mg_l` | Jun 2021 - Aug 2025 | Total Ammonia Nitrogen (TAN as NH₃-N). Old measurement method. |
| `ammonia_nh3_mg_l` | Aug 2025 onwards | Unionized ammonia (NH₃). New primary metric - the directly toxic form. |
| `ammonia_tan_as_nh3_mg_l` | Aug 2025 onwards | TAN expressed as NH₃. Used during transition period for comparison. |

**Note:** During the transition period (Aug 2025 onwards), both old and new metrics are tracked. Earlier records will only have `ammonia_tan_mg_l` populated.

---

## enrolled_ponds_2026-02-02.csv

Snapshot of ponds enrolled in the ARA program as of February 2, 2026.

**Note:** "Enrolled" means the pond is participating in the ARA program. This is distinct from "active" ponds, which at FWI refers specifically to ponds that currently have fish stocked. An enrolled pond may be between production cycles (empty) but still part of the program.

| Column | Type | Description |
|--------|------|-------------|
| `pond_id` | string | Anonymized pond identifier |
| `region` | string | Geographic region (West Godavari or Nellore) |
| `enrollment_date` | date | Date pond enrolled in program (YYYY-MM-DD) |
| `pond_type` | string | Treatment or Control |
| `added_by` | string | FWI staff member who added the pond |
| `pond_area_acres` | float | Pond surface area in acres |
| `depth_meters` | float | Pond depth in meters |
| `equipment` | string | Farm equipment (aerators, pumps, etc.) |
| `feed_type` | string | Type of feed used |

---

## stocking_harvest.csv

Stocking and harvest events for tracked ponds.

| Column | Type | Description |
|--------|------|-------------|
| `pond_id` | string | Anonymized pond identifier |
| `region` | string | Geographic region (West Godavari or Nellore) |
| `event_date` | date | Date of event (YYYY-MM-DD) |
| `event_type` | string | Type: Stocking, Harvest, Partial stocking, Partial harvest |
| `logged_by` | string | FWI staff member who logged the event |
| `lifecycle_stage` | string | Production stage: Breed-out, Grow-out, Rearing |
| `species` | string | Fish species stocked/harvested |
| `species_ratio` | string | Ratio of species (e.g., "9:1") |
| `target_weight_grams` | float | Target harvest weight in grams |
| `average_weight_grams` | float | Average fish weight at event time in grams |
| `intended_stocking_density_per_acre` | float | Planned stocking density |
| `actual_stocking_density_per_acre` | float | Actual stocking density |
| `fish_harvested_kg` | float | Total fish harvested in kg (harvest events) |
| `fish_remaining_individuals` | float | Fish remaining in pond (partial harvest) |
| `harvest_reason` | string | Reason for harvest (e.g., "Planned harvest") |
| `pond_preparation_done` | boolean | Whether farmer did pond preparation |

### Lifecycle Stages

- **Breed-out**: Fingerling/juvenile production phase
- **Grow-out**: Main growth phase to market size
- **Rearing**: Early rearing of fry/fingerlings

---

## dropouts.csv

Ponds that have left the program.

| Column | Type | Description |
|--------|------|-------------|
| `pond_id` | string | Anonymized pond identifier |
| `region` | string | Geographic region (West Godavari or Nellore) |
| `dropout_date` | date | Date of dropout (YYYY-MM-DD) |
| `added_by` | string | FWI staff member who recorded the dropout |
| `reason_category` | string | Standardized dropout reason |
| `tenancy_type` | string | Owned or Leased |
| `total_measurements` | integer | Number of WQ measurements before dropout |

### Dropout Reason Categories

| Category | Description |
|----------|-------------|
| Changed to shrimp | Farmer switched to crustacean farming |
| Changed to other finfish | Farmer switched to different fish species |
| Stopped farming | Farmer stopped aquaculture entirely |
| Other | Other reasons (farmer unreachable, sold farm, etc.) |

---

## Notes on Missing Values

Empty cells or `NaN` values may indicate:
- Data not collected for that measurement type (e.g., turbidity only measured in morning)
- Parameter not applicable (e.g., harvest fields on stocking events)
- Data deliberately not collected as part of methodology refinement

This is not missing data, but rather intentional data collection decisions. See the [ARA Data blog post](https://www.fishwelfareinitiative.org/post/ara-data-24) for more context.
