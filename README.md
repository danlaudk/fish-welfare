# FWI Farm Data - India (up to Jan 31, 2026)

Public dataset from the **Alliance for Responsible Aquaculture (ARA)** program operated by [Fish Welfare Initiative](https://www.fishwelfareinitiative.org/) in India.

## About the Program

The ARA program works with fish farmers in India to improve fish welfare through water quality monitoring and management. Field staff conduct regular visits to measure water quality parameters and provide corrective action recommendations when measurements fall outside acceptable ranges.

**Regions covered:** Eluru and Nellore districts, Andhra Pradesh, India

**Program period:** June 2021 - January 2026 (ongoing)

## Datasets

| File | Records | Description |
|------|---------|-------------|
| [`water_quality.csv`](data/water_quality.csv) | 11,433 | Water quality measurements collected during farm visits |
| [`enrolled_ponds_2026-02-02.csv`](data/enrolled_ponds_2026-02-02.csv) | 210 | Ponds enrolled in the program as of Feb 2, 2026 |
| [`stocking_harvest.csv`](data/stocking_harvest.csv) | 1,461 | Stocking and harvest events |
| [`dropouts.csv`](data/dropouts.csv) | 94 | Ponds that left the program |

**Note:** "Enrolled ponds" refers to ponds participating in the ARA program, regardless of whether they currently have fish stocked. This differs from "active ponds" which would only include ponds with fish currently in them.

See [`docs/data_dictionary.md`](docs/data_dictionary.md) for detailed column definitions.

## Privacy

All data has been anonymized to protect farmer privacy:
- Pond IDs are anonymized using deterministic hashing
- Farmer names, village names, and GPS coordinates are excluded
- Financial data (earnings, costs) are excluded

## License

This data is released under [CC-BY-4.0](LICENSE). You are free to share and adapt this data for any purpose, provided you give appropriate credit.

## Citation

If you use this data in research or publications, please cite:

```
Fish Welfare Initiative. (2026). FWI Farm Data - India (up to Jan 31, 2026).
https://github.com/fish-welfare-initiative/fwi-farm-data-india
```

## Contact

For questions about this data, please contact: [fwi.fish/contact](https://fwi.fish/contact)

## Related Links

- [Fish Welfare Initiative](https://www.fishwelfareinitiative.org/)
- [ARA Program Overview](https://www.fishwelfareinitiative.org/ara)
- [ARA Data Dashboard](https://data.fishwelfareinitiative.org/ara)
