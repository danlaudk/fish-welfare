#!/usr/bin/env python3
"""
FWI ARA Data Processing Script
Processes raw dashboard exports into anonymized public datasets.

Columns are kept in the same order as the original files, with minimal exclusions:
- All datasets: Farmer name excluded, Pond ID replaced with anonymized pond_id
- Enrolled ponds: Location (GPS), Village, Fish source excluded
- Stocking/harvest: Financial data (payment, earnings) and verification notes excluded
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
    if pd.isna(pond_id):
        return None
    hash_input = f"{salt}:{pond_id}"
    hash_digest = hashlib.sha256(hash_input.encode()).hexdigest()
    return f"pond_{hash_digest[:8]}"

def extract_region(pond_id: str) -> str:
    """Extract region from pond ID prefix."""
    if pd.isna(pond_id):
        return None
    if str(pond_id).startswith("WG-"):
        return "Eluru"
    elif str(pond_id).startswith("NL-"):
        return "Nellore"
    return "Unknown"

def process_water_quality():
    """Process WQ.csv - keep all columns except Farmer, replace Pond ID with pond_id"""
    print("Processing water quality data...")

    df = pd.read_csv(SOURCE_DIR / "WQ.csv")
    print(f"  Source records: {len(df)}")
    print(f"  Source columns: {len(df.columns)}")

    # Generate anonymous IDs and region
    df['pond_id'] = df['Pond ID'].apply(generate_anonymous_id)
    df['region'] = df['Pond ID'].apply(extract_region)

    # Build output with all columns in original order, excluding Farmer and replacing Pond ID
    output_columns = []
    for col in df.columns:
        if col == 'Pond ID':
            # Replace with pond_id and region
            if 'pond_id' not in output_columns:
                output_columns.append('pond_id')
                output_columns.append('region')
        elif col == 'Farmer':
            # Exclude farmer name
            continue
        elif col in ['pond_id', 'region']:
            # Already added
            continue
        else:
            output_columns.append(col)

    output = df[output_columns].copy()

    output.to_csv(OUTPUT_DIR / "water_quality.csv", index=False)
    print(f"  Output records: {len(output)}")
    print(f"  Output columns: {len(output.columns)}")
    return df[['Pond ID', 'pond_id']].drop_duplicates()

def process_enrolled_ponds():
    """Process enrolled ponds.csv - exclude Farmer, Pond ID, Location, Village, Fish source"""
    print("Processing enrolled ponds data...")

    df = pd.read_csv(SOURCE_DIR / "enrolled ponds.csv")
    print(f"  Source records: {len(df)}")
    print(f"  Source columns: {len(df.columns)}")

    # Generate anonymous IDs and region
    df['pond_id'] = df['Pond ID'].apply(generate_anonymous_id)
    df['region'] = df['Pond ID'].apply(extract_region)

    # Columns to exclude
    exclude_cols = {'Pond ID', 'Farmer', 'Location', 'Village', 'Fish source (e.g. hatchery name)'}

    # Build output with all columns in original order
    output_columns = []
    for col in df.columns:
        if col == 'Pond ID':
            # Replace with pond_id and region
            if 'pond_id' not in output_columns:
                output_columns.append('pond_id')
                output_columns.append('region')
        elif col in exclude_cols:
            continue
        elif col in ['pond_id', 'region']:
            continue
        else:
            output_columns.append(col)

    output = df[output_columns].copy()

    output.to_csv(OUTPUT_DIR / "enrolled_ponds_2026-02-02.csv", index=False)
    print(f"  Output records: {len(output)}")
    print(f"  Output columns: {len(output.columns)}")
    return df[['Pond ID', 'pond_id']].drop_duplicates()

def process_stocking_harvest():
    """Process stocking:harvesting.csv - exclude Farmer, Pond, financial data, verification notes"""
    print("Processing stocking/harvest data...")

    df = pd.read_csv(SOURCE_DIR / "stocking:harvesting.csv")
    print(f"  Source records: {len(df)}")
    print(f"  Source columns: {len(df.columns)}")

    # Parse dates and filter out invalid ones
    df['parsed_date'] = pd.to_datetime(df['Event date'], format='%m/%d/%Y', errors='coerce')

    # Filter out records with invalid years (before 2020 or after 2030)
    valid_mask = (df['parsed_date'].dt.year >= 2020) & (df['parsed_date'].dt.year <= 2030)
    invalid_count = (~valid_mask).sum()
    if invalid_count > 0:
        print(f"  Excluding {invalid_count} records with invalid dates")

    df = df[valid_mask].copy()

    # Generate anonymous IDs and region
    df['pond_id'] = df['Pond'].apply(generate_anonymous_id)
    df['region'] = df['Pond'].apply(extract_region)

    # Columns to exclude (Farmer, Pond, financial data, verification notes)
    exclude_cols = {
        'Pond', 'Farmer',
        'How much did the farmer pay for the stocked fish and shrimp? (in INR)',
        'Earnings from the fish/shrimp sale (in INR)',
        'Data verification notes',
        'parsed_date'  # We keep Event date as-is
    }

    # Build output with all columns in original order
    output_columns = []
    for col in df.columns:
        if col == 'Pond':
            # Replace with pond_id and region
            if 'pond_id' not in output_columns:
                output_columns.append('pond_id')
                output_columns.append('region')
        elif col in exclude_cols:
            continue
        elif col in ['pond_id', 'region']:
            continue
        else:
            output_columns.append(col)

    output = df[output_columns].copy()

    # Convert all float columns to integers (removes .0 artifacts from float conversion)
    # Skip 'Data verified by' which is not a numeric field
    skip_int_conversion = {'Data verified by'}
    for col in output.columns:
        if output[col].dtype == 'float64' and col not in skip_int_conversion:
            output[col] = output[col].round(0).astype('Int64')

    output.to_csv(OUTPUT_DIR / "stocking_harvest.csv", index=False)
    print(f"  Output records: {len(output)}")
    print(f"  Output columns: {len(output.columns)}")
    return df[['Pond', 'pond_id']].rename(columns={'Pond': 'Pond ID'}).drop_duplicates()

def process_dropouts():
    """Process dropouts.csv - exclude Farmer and Pond only"""
    print("Processing dropouts data...")

    df = pd.read_csv(SOURCE_DIR / "dropouts.csv")
    print(f"  Source records: {len(df)}")
    print(f"  Source columns: {len(df.columns)}")

    # Generate anonymous IDs and region
    df['pond_id'] = df['Pond'].apply(generate_anonymous_id)
    df['region'] = df['Pond'].apply(extract_region)

    # Columns to exclude
    exclude_cols = {'Pond', 'Farmer'}

    # Build output with all columns in original order
    output_columns = []
    for col in df.columns:
        if col == 'Pond':
            # Replace with pond_id and region
            if 'pond_id' not in output_columns:
                output_columns.append('pond_id')
                output_columns.append('region')
        elif col in exclude_cols:
            continue
        elif col in ['pond_id', 'region']:
            continue
        else:
            output_columns.append(col)

    output = df[output_columns].copy()

    output.to_csv(OUTPUT_DIR / "dropouts.csv", index=False)
    print(f"  Output records: {len(output)}")
    print(f"  Output columns: {len(output.columns)}")
    return df[['Pond', 'pond_id']].rename(columns={'Pond': 'Pond ID'}).drop_duplicates()

def generate_lookup_table(mappings: list):
    """Generate private lookup table combining all pond ID mappings."""
    print("Generating private lookup table...")

    combined = pd.concat(mappings, ignore_index=True).drop_duplicates()
    combined = combined.rename(columns={'Pond ID': 'internal_pond_id', 'pond_id': 'public_pond_id'})
    combined['region'] = combined['internal_pond_id'].apply(extract_region)
    combined = combined.sort_values('internal_pond_id')

    # Try to add GPS, village, farmer from enrolled ponds if available
    try:
        ponds_src = pd.read_csv(SOURCE_DIR / "enrolled ponds.csv")
        gps_data = ponds_src[['Pond ID', 'Location', 'Village', 'Farmer']].copy()
        gps_data = gps_data.rename(columns={'Pond ID': 'internal_pond_id'})

        combined = combined.merge(gps_data, on='internal_pond_id', how='left')

        # Parse Location into lat/lon
        def parse_location(loc):
            if pd.isna(loc):
                return None, None
            try:
                parts = loc.split(',')
                lat = float(parts[0].strip())
                lon = float(parts[1].strip())
                return lat, lon
            except:
                return None, None

        combined[['latitude', 'longitude']] = combined['Location'].apply(
            lambda x: pd.Series(parse_location(x))
        )
        combined = combined.drop(columns=['Location'])
        combined = combined.rename(columns={'Village': 'village', 'Farmer': 'farmer_name'})

        # Reorder columns
        combined = combined[['internal_pond_id', 'public_pond_id', 'region', 'latitude', 'longitude', 'village', 'farmer_name']]
    except Exception as e:
        print(f"  Warning: Could not add GPS/farmer data: {e}")

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
    print(f"  Eluru: {(lookup['region'] == 'Eluru').sum()}")
    print(f"  Nellore: {(lookup['region'] == 'Nellore').sum()}")

if __name__ == "__main__":
    main()
