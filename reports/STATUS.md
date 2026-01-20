# Dementia Risk Prediction Report - Status

## Summary

A comprehensive Quarto report has been created for predicting dementia risk from PSG data using the SleepFM transformer model. The report is based on the working demo notebook (`notebooks/demo.ipynb`) and includes:

## What's Been Created

### 1. Main Quarto Report (`dementia_risk_prediction.qmd`)
- **Complete end-to-end pipeline** from EDF files to dementia risk predictions
- **Data acquisition guide** for freely accessible PSG datasets (SHHS, MESA)
- **Preprocessing section** for converting EDF to HDF5 format
- **Embedding generation** using the pre-trained SleepFM base model
- **Disease prediction** using the fine-tuned diagnosis model
- **Visualization and interpretation** of results
- **Clinical context** for understanding hazard ratios

### 2. Documentation
- **README.md**: Usage instructions, troubleshooting, customization guide
- **test_dementia_prediction.py**: Test script for validating the setup

### 3. Verified Resources
- ✅ Model checkpoints exist (`model_base`, `model_diagnosis`)
- ✅ Demo PSG data available (`notebooks/demo_data/demo_psg.edf`)
- ✅ Demographics and labels (`demo_age_gender.csv`, `is_event.csv`, `time_to_event.csv`)
- ✅ Label mapping for 1,065 diseases including dementia (`configs/label_mapping.csv`)

## Current Status

### ✅ Completed
1. Report structure and content created
2. Code based on working demo notebook
3. Checkpoints and demo data verified
4. Documentation written
5. Test script created

### ⚠️ Pending
1. **Dependency Installation**: Python packages need to be installed
   ```bash
   pip install -r requirements.txt
   ```

2. **Code Testing**: Once dependencies are installed, run:
   ```bash
   python3 reports/test_dementia_prediction.py
   ```

3. **Quarto Rendering**: Test rendering the report:
   ```bash
   quarto render reports/dementia_risk_prediction.qmd
   ```

## Next Steps

### Immediate (Required for Testing)

1. **Install Dependencies**:
   ```bash
   cd /home/user/sleepfm-clinical
   pip install -r requirements.txt
   ```

   Key packages needed:
   - `torch==2.0.1`
   - `numpy==1.25.2`
   - `pandas==2.1.1`
   - `h5py==3.11.0`
   - `pyedflib==0.1.37`
   - `mne==1.7.0`
   - `matplotlib==3.8.0`
   - `seaborn==0.13.2`

2. **Run Test Script**:
   ```bash
   python3 reports/test_dementia_prediction.py
   ```

   This will verify:
   - All imports work
   - Checkpoints load correctly
   - Models can be initialized
   - Label mapping is accessible

3. **Test Quarto Rendering**:
   ```bash
   cd reports
   quarto render dementia_risk_prediction.qmd
   ```

### Follow-up (Optional Enhancements)

1. **Add Real Data Examples**:
   - Download SHHS data from sleepdata.org
   - Update report paths to use real datasets
   - Validate on external cohorts

2. **Extend Analysis**:
   - Add sleep architecture visualization
   - Include other disease predictions (heart failure, stroke, etc.)
   - Compare multiple patients

3. **Optimize for Different Environments**:
   - Test on CPU-only systems
   - Reduce memory footprint for smaller GPUs
   - Add batch processing for multiple files

## Known Issues

### Dependency Installation
- Initial `pip install` attempts timed out
- Recommendation: Install in stages or use conda environment:
  ```bash
  conda env create -f env.yml
  conda activate sleepfm_env
  ```

### Code Updates Needed
The Quarto report code needs minor adjustments based on test results:
- Model initialization parameters
- Data loading paths
- Device selection (CPU vs GPU)

These can be addressed after dependencies are installed and initial testing is complete.

## Files Created

```
reports/
├── dementia_risk_prediction.qmd       # Main Quarto report
├── dementia_risk_prediction.qmd.backup # Backup copy
├── README.md                           # Usage documentation
├── STATUS.md                           # This file
└── test_dementia_prediction.py        # Test script
```

## Model Performance

From the published Nature Medicine paper (2026):
- **Dementia C-Index**: 0.85 (Bonferroni-corrected p < 0.01)
- **Training Data**: 585,000+ hours of PSG from ~65,000 participants
- **External Validation**: SHHS dataset (transferred successfully)
- **Total Diseases**: 1,065 conditions predicted simultaneously

## Architecture Overview

### SleepFM Base Model (4.44M parameters)
- **Input**: Multi-modal PSG signals (BAS, RESP, EKG, EMG)
- **Tokenizer**: Conv1D-based (640 samples → 128-dim embeddings)
- **Spatial Pooling**: Attention across channels
- **Temporal Processing**: 6-layer Transformer encoder
- **Output**: 128-dim embeddings per 5-minute epoch

### Disease Prediction Model (0.91M parameters)
- **Input**: Embeddings + demographics (age, gender)
- **Architecture**: LSTM + Cox Proportional Hazards
- **Output**: Hazard ratios for 1,065 diseases
- **Loss**: CoxPH (handles time-to-event and censoring)

## Data Format

### Input: EDF Files
- Standard polysomnography format
- Multiple channels (EEG, ECG, EMG, respiratory)
- Variable sampling rates (resampled to 128 Hz)

### Processed: HDF5 Files
- Compressed storage (gzip level 4)
- 5-minute epochs (38,400 samples @ 128 Hz)
- Per-channel z-score normalization
- Grouped by modality (BAS, RESP, EKG, EMG)

### Output: Risk Predictions
- Hazard logits for each disease
- Confidence intervals (if bootstrapped)
- Time-to-event predictions
- Event occurrence probabilities

## References

1. **SleepFM Paper**:
   Thapa, R., et al. (2026). A multimodal sleep foundation model for disease prediction. *Nature Medicine*.
   https://doi.org/10.1038/s41591-025-04133-4

2. **Demo Data**:
   Synthetic PSG generated for demonstration purposes
   Location: `notebooks/demo_data/`

3. **Real Datasets** (freely accessible):
   - SHHS: https://sleepdata.org/datasets/shhs
   - MESA: https://sleepdata.org/datasets/mesa
   - Stanford Sleep Dataset: https://bdsp.io/content/08vg8vqv2wdtwonc1ddy/1.0

## Contact & Support

For issues or questions:
- Check the main README: `/home/user/sleepfm-clinical/README.md`
- Review demo notebook: `notebooks/demo.ipynb`
- GitHub issues: https://github.com/zou-group/sleepfm-clinical/issues

---

**Last Updated**: 2026-01-20
**Status**: Ready for dependency installation and testing
