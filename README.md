# 2026 data consulting
In April, Haven requested contractors / volunteers to take a last stab at the data. 
We were given a brief, and a new pond_locations dataset (NOT PUBLIC) "Shared_ 2026 Github ARA Pond IDs Key.csv". (This is one of the key source data files)

## Summary of findings / hypothesis
Using weather data coupled with the GPS locations brought the result close to a prior attempt.
This [graph](ModelSelection/nb11_test_predictions.png) shows the test predictions. 
The model precision isn't good enough. 

Data is not consistently collected from any single pond, nor from any single village. 
Ponds are observed based on i) remedial action suspected (unobserved variables, and correlated) ii) need to visit all ponds somewhat regularly.  
This introduces bias in sampling.
The between-pond variation is large relative to the sampling frequency, that a mostly-weather model seems unlikely to have enough precision. 

### Procedure
After various methods, I attempted the state-of-the-art in aquaculture water quality prediction (a significant research discipline): transfer learning.
There are not enough samples across the year (campaign data, two months), 
or not dense enough (inconsistent collection on any single pond from 5-year data), 
or monitoring equipment or ponds not similar enough (kaggle data), to capture and transfer month-seasonal patterns. 
This is particularly important in the monsoon area. 

I considered the data quantity insufficient for autogressive models like LSTM.

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
