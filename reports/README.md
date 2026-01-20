# SleepFM Clinical Reports

This directory contains Quarto reports for analyzing PSG data and predicting disease risk using the SleepFM transformer model.

## Available Reports

### 1. Dementia Risk Prediction (`dementia_risk_prediction.qmd`)

A comprehensive report demonstrating how to:
- Download freely accessible PSG data from PhysioNet/NSRR
- Preprocess EDF files to HDF5 format
- Generate embeddings using the pre-trained SleepFM base model
- Predict dementia risk using the fine-tuned disease prediction model
- Visualize and interpret results

**Key Features:**
- Uses freely available data from Sleep Heart Health Study (SHHS)
- Complete end-to-end pipeline
- Clinical interpretation of hazard ratios
- Reproducible analysis with embedded code

## Prerequisites

### Software Requirements

1. **Python 3.10+** with packages:
   ```bash
   pip install pandas numpy matplotlib seaborn torch h5py mne pyedflib
   ```

2. **Quarto** (for rendering reports):
   ```bash
   # Install Quarto from https://quarto.org/docs/get-started/
   # Or use conda:
   conda install -c conda-forge quarto
   ```

3. **NSRR Downloader** (optional, for downloading data):
   ```bash
   pip install nsrr
   ```

### Data Requirements

**Option 1: Use Demo Data (Recommended for Quick Start)**
- The repository includes demo data in `data/mesa/`
- No additional downloads needed
- Modify the report to point to demo files

**Option 2: Download SHHS Data**
1. Register at https://sleepdata.org (free for research use)
2. Get your API token from your account settings
3. Download PSG files using the NSRR downloader:
   ```bash
   nsrr download shhs/polysomnography/edfs/shhs1/ -t YOUR_TOKEN
   ```

## Usage

### Rendering the Report

**Generate HTML output:**
```bash
cd /home/user/sleepfm-clinical/reports
quarto render dementia_risk_prediction.qmd
```

**Generate PDF output:**
```bash
quarto render dementia_risk_prediction.qmd --to pdf
```

**Live preview with auto-reload:**
```bash
quarto preview dementia_risk_prediction.qmd
```

### Customization

#### Using Your Own Data

1. Modify the data paths in the report:
   ```python
   DATA_DIR = Path("/path/to/your/data")
   ```

2. Ensure your data structure follows:
   ```
   data/
   └── your_dataset/
       ├── edfs/           # Raw EDF files
       ├── processed/      # Converted HDF5 files
       └── embeddings/     # Generated embeddings
   ```

#### Changing Patient Demographics

Modify the demographics in the prediction section:
```python
patient_demographics = {
    'age': 70,      # years
    'gender': 0     # 0=female, 1=male
}
```

#### Analyzing Different Diseases

The model predicts 1,065 diseases. To focus on a different condition:

1. Check `sleepfm/configs/label_mapping.csv` for available diseases
2. Find the phecode or phenotype name
3. Update the analysis:
   ```python
   # Example: Analyze heart failure instead
   hf_labels = labels_df[labels_df['phenotype'].str.contains('heart failure', case=False)]
   HF_IDX = hf_labels.iloc[0]['label_idx']
   hf_hazard = hazard_logits[HF_IDX]
   ```

## Output Files

After rendering, you'll get:

- `dementia_risk_prediction.html` - Interactive HTML report with embedded plots
- `dementia_risk_prediction.pdf` - PDF version (if rendered)
- `dementia_risk_prediction_files/` - Supporting files (plots, data)

## Troubleshooting

### Common Issues

**1. CUDA out of memory**
- Reduce batch size in model configuration
- Process fewer epochs at once
- Use CPU instead: `device = torch.device('cpu')`

**2. Missing channels in PSG data**
- Check `channel_groups.json` for expected channel names
- Modify channel mapping in preprocessing script
- Some channels are optional (model handles missing modalities)

**3. Checkpoint not found**
- Ensure model checkpoints are downloaded:
  ```bash
  ls sleepfm/checkpoints/model_base/
  ls sleepfm/checkpoints/model_diagnosis/
  ```
- Download from the SleepFM repository if missing

**4. Quarto rendering errors**
- Check Python kernel: `quarto check`
- Verify all dependencies are installed
- Try rendering without executing code: `quarto render --execute-daemon=false`

## Performance Notes

**Typical processing times (on NVIDIA A40 GPU):**
- EDF to HDF5 conversion: ~2-3 minutes per recording
- Embedding generation: ~30 seconds per recording
- Disease prediction: <1 second per recording

**Memory requirements:**
- Minimum: 16 GB RAM
- Recommended: 32 GB RAM for parallel processing
- GPU: 8 GB VRAM minimum (16 GB recommended)

## Citation

If you use this report or the SleepFM model in your research, please cite:

```bibtex
@article{thapa2026multimodal,
  title={A multimodal sleep foundation model for disease prediction},
  author={Thapa, Rahul and Kjaer, Magnus Ruud and He, Bryan and Covert, Ian and Moore IV, Hyatt and Hanif, Umaer and Ganjoo, Gauri and Westover, M Brandon and Jennum, Poul and Brink-Kjaer, Andreas and others},
  journal={Nature Medicine},
  pages={1--11},
  year={2026},
  publisher={Nature Publishing Group US New York}
}
```

## Additional Resources

- **SleepFM Repository**: https://github.com/zou-group/sleepfm-clinical
- **Paper**: https://doi.org/10.1038/s41591-025-04133-4
- **NSRR Data Portal**: https://sleepdata.org
- **Quarto Documentation**: https://quarto.org/docs/guide/

## Support

For questions or issues:
1. Check the main repository README
2. Review the demo notebook: `notebooks/demo.ipynb`
3. Open an issue on GitHub: https://github.com/zou-group/sleepfm-clinical/issues

## License

This report follows the same MIT License as the SleepFM repository.
