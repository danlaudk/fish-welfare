#!/usr/bin/env python3
"""
FWI ARA Data Processing Script
Processes raw dashboard exports into anonymized public datasets.
"""

import pandas as pd
import hashlib
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent.parent.parent
SOURCE_DIR = BASE_DIR / "data downloaded from dashboard"
OUTPUT_DIR = BASE_DIR / "fwi-farm-data-india" / "data"
PRIVATE_DIR = BASE_DIR / "private"

def generate_anonymous_id(pond_id: str, salt: str = "fwi-ara-2026") -> str:
    """Generate deterministic anonymous pond ID using SHA-256 hash."""
    hash_input = f"{salt}:{pond_id}"
    hash_digest = hashlib.sha256(hash_input.encode()).hexdigest()
    return f"pond_{hash_digest[:8]}"

def extract_region(pond_id: str) -> str:
    """Extract region from pond ID prefix."""
    if pond_id.startswith("WG-"):
        return "West Godavari"
    elif pond_id.startswith("NL-"):
        return "Nellore"
    return "Unknown"

def process_water_quality():
    """Process WQ.csv into water_quality.csv"""
    print("Processing water quality data...")

    df = pd.read_csv(SOURCE_DIR / "WQ.csv")
    print(f"  Source records: {len(df)}")

    # Generate anonymous IDs
    df['pond_id'] = df['Pond ID'].apply(generate_anonymous_id)

    # Select and rename columns
    output = pd.DataFrame({
        'pond_id': df['pond_id'],
        'region': df['Pond ID'].apply(extract_region),
        'date': pd.to_datetime(df['Date of data collection'], format='%m/%d/%Y').dt.strftime('%Y-%m-%d'),
        'measurement_type': df['Type'],
        'time': df['Time of data collection'],
        'group': df['Group'],
        'pond_type': df['Pond status'],
        'staff_member': df['Observer'],
        'equipment': df['Equipment'],
        'is_follow_up': df['Is follow up'].map({'Yes': True, 'No': False}),
        'dissolved_oxygen_mg_l': df['DO (mg/L)'],
        'ph': df['pH'],
        # Ammonia columns - protocol changed in Aug 2025
        # See: https://www.fishwelfareinitiative.org/post/ammonia-change
        'ammonia_tan_mg_l': df['Ammonia—TAN (NH3-N) (mg/L)'],  # Old method (until Aug 2025)
        'ammonia_nh3_mg_l': df['Ammonia—NH3 (mg/L)'],  # New method - unionized ammonia (from Aug 2025)
        'ammonia_tan_as_nh3_mg_l': df['Ammonia—TAN (NH3) (mg/L)'],  # TAN as NH3 (transition tracking)
        'turbidity_cm': df['Turbidity (in cm)'],
        'temperature_c': df['Temp (in °C)'],
        'water_color': df['Water color'],
        'tds_ppt': df['TDS (ppt)'],
        'weather': df['Weather'],
        'is_in_range': df['Is WQ in range?'].map({'Yes': True, 'No': False}),
        'parameters_out_of_range': df['Parameters out of range'],
        'corrective_action_requested': df['Corrective actions requested'],
        'corrective_action_implemented': df['Corrective actions implemented'].map({
            'Yes, all of them': True,
            'Only some': True,  # Partial implementation counts as implemented
            'No, none of them': False
        }),
        'corrective_action_effective': df['Water quality improved after corrective actions'].map({'Yes': True, 'No': False}),
    })

    output.to_csv(OUTPUT_DIR / "water_quality.csv", index=False)
    print(f"  Output records: {len(output)}")
    return df[['Pond ID', 'pond_id']].drop_duplicates()

def process_enrolled_ponds():
    """Process enrolled ponds.csv into enrolled_ponds_2026-02-02.csv"""
    print("Processing enrolled ponds data...")

    df = pd.read_csv(SOURCE_DIR / "enrolled ponds.csv")
    print(f"  Source records: {len(df)}")

    # Generate anonymous IDs
    df['pond_id'] = df['Pond ID'].apply(generate_anonymous_id)

    # Select and rename columns
    output = pd.DataFrame({
        'pond_id': df['pond_id'],
        'region': df['Pond ID'].apply(extract_region),
        'enrollment_date': pd.to_datetime(df['Date of data collection'], format='%m/%d/%Y').dt.strftime('%Y-%m-%d'),
        'pond_type': df['Status'],
        'added_by': df['Added by'],
        'pond_area_acres': df['Pond area in acres'],
        'depth_meters': df['Depth in meters'],
        'equipment': df['Equipment'],
        'feed_type': df['Feed type'],
    })

    output.to_csv(OUTPUT_DIR / "enrolled_ponds_2026-02-02.csv", index=False)
    print(f"  Output records: {len(output)}")
    return df[['Pond ID', 'pond_id']].drop_duplicates()

def process_stocking_harvest():
    """Process stocking:harvesting.csv into stocking_harvest.csv"""
    print("Processing stocking/harvest data...")

    df = pd.read_csv(SOURCE_DIR / "stocking:harvesting.csv")
    print(f"  Source records: {len(df)}")

    # Parse dates and filter out invalid ones
    df['parsed_date'] = pd.to_datetime(df['Event date'], format='%m/%d/%Y', errors='coerce')

    # Filter out records with invalid years (before 2020 or after 2030)
    valid_mask = (df['parsed_date'].dt.year >= 2020) & (df['parsed_date'].dt.year <= 2030)
    invalid_count = (~valid_mask).sum()
    if invalid_count > 0:
        print(f"  Excluding {invalid_count} records with invalid dates")
        invalid_dates = df[~valid_mask][['Event date', 'Pond']].head(5)
        print(f"  Sample invalid dates: {invalid_dates.to_dict('records')}")

    df = df[valid_mask]

    # Generate anonymous IDs
    df['pond_id'] = df['Pond'].apply(generate_anonymous_id)

    # Select and rename columns
    output = pd.DataFrame({
        'pond_id': df['pond_id'],
        'region': df['Pond'].apply(extract_region),
        'event_date': df['parsed_date'].dt.strftime('%Y-%m-%d'),
        'event_type': df['Type'],
        'logged_by': df['Logged by'],
        'lifecycle_stage': df['Lifecycle'],
        'species': df['Species'],
        'species_ratio': df['Species ratio'],
        'target_weight_grams': df['Reported target weight in grams'],
        'average_weight_grams': df['Average fish weight (in grams)'],
        'intended_stocking_density_per_acre': df['Intended fish stocking density (per acre)'],
        'actual_stocking_density_per_acre': df['Actual fish stocking density (per acre)'],
        'fish_harvested_kg': df['Fish harvested (total, in kg)'],
        'fish_remaining_individuals': df['Fish left in the pond (total, in individuals)'],
        'harvest_reason': df['Harvest reason'],
        'pond_preparation_done': df['Did the farmer do pond preparation?'].map({1: True, 0: False, '1': True, '0': False}),
    })

    output.to_csv(OUTPUT_DIR / "stocking_harvest.csv", index=False)
    print(f"  Output records: {len(output)}")
    return df[['Pond', 'pond_id']].rename(columns={'Pond': 'Pond ID'}).drop_duplicates()

def process_dropouts():
    """Process dropouts.csv into dropouts.csv"""
    print("Processing dropouts data...")

    df = pd.read_csv(SOURCE_DIR / "dropouts.csv")
    print(f"  Source records: {len(df)}")

    # Generate anonymous IDs
    df['pond_id'] = df['Pond'].apply(generate_anonymous_id)

    # Standardize reason categories
    reason_map = {
        'Changed to farming crustaceans (e.g. shrimp)': 'Changed to shrimp',
        'Changed to farming another species of finfish': 'Changed to other finfish',
        'Stopped farming fish': 'Stopped farming',
        'Other (mention below)': 'Other',
    }
    df['reason_standardized'] = df['Reason'].map(reason_map).fillna('Other')

    # Select and rename columns
    output = pd.DataFrame({
        'pond_id': df['pond_id'],
        'region': df['Pond'].apply(extract_region),
        'dropout_date': pd.to_datetime(df['Date of drop out'], format='%m/%d/%Y').dt.strftime('%Y-%m-%d'),
        'added_by': df['Added by'],
        'reason_category': df['reason_standardized'],
        'tenancy_type': df['Tenancy type'],
        'total_measurements': df['Pond measurements'],
    })

    output.to_csv(OUTPUT_DIR / "dropouts.csv", index=False)
    print(f"  Output records: {len(output)}")
    return df[['Pond', 'pond_id']].rename(columns={'Pond': 'Pond ID'}).drop_duplicates()

def generate_lookup_table(mappings: list):
    """Generate private lookup table combining all pond ID mappings."""
    print("Generating private lookup table...")

    combined = pd.concat(mappings, ignore_index=True).drop_duplicates()
    combined = combined.rename(columns={'Pond ID': 'internal_pond_id', 'pond_id': 'public_pond_id'})
    combined['region'] = combined['internal_pond_id'].apply(extract_region)
    combined = combined.sort_values('internal_pond_id')

    combined.to_csv(PRIVATE_DIR / "pond_id_mapping.csv", index=False)
    print(f"  Total unique ponds: {len(combined)}")

    return combined

def main():
    print("=" * 60)
    print("FWI ARA Data Processing")
    print("=" * 60)

    # Process each dataset and collect pond ID mappings
    mappings = []

    mappings.append(process_water_quality())
    print()

    mappings.append(process_enrolled_ponds())
    print()

    mappings.append(process_stocking_harvest())
    print()

    mappings.append(process_dropouts())
    print()

    # Generate private lookup table
    lookup = generate_lookup_table(mappings)

    print()
    print("=" * 60)
    print("Processing complete!")
    print("=" * 60)
    print(f"\nPublic data saved to: {OUTPUT_DIR}")
    print(f"Private lookup saved to: {PRIVATE_DIR / 'pond_id_mapping.csv'}")

    # Summary stats
    print("\n" + "=" * 60)
    print("Summary Statistics")
    print("=" * 60)
    print(f"Total unique ponds across all datasets: {len(lookup)}")
    print(f"  West Godavari: {(lookup['region'] == 'West Godavari').sum()}")
    print(f"  Nellore: {(lookup['region'] == 'Nellore').sum()}")

if __name__ == "__main__":
    main()
