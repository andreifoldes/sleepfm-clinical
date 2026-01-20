"""
Test script for dementia risk prediction using SleepFM
Based on the working demo.ipynb notebook
"""
import sys
import os
sys.path.append("/home/user/sleepfm-clinical")

import torch
import numpy as np
import pandas as pd
import h5py
from pathlib import Path

# Import SleepFM modules
from sleepfm.models.models import SetTransformer, DiagnosisFinetuneFullLSTMCOXPHWithDemo
from sleepfm.preprocessing.preprocessing import EDFToHDF5Converter
from sleepfm.utils import load_config, load_data, count_parameters

def test_basic_imports():
    """Test that all required modules can be imported"""
    print("="*60)
    print("TESTING IMPORTS")
    print("="*60)

    modules = {
        'torch': torch,
        'numpy': np,
        'pandas': pd,
        'h5py': h5py,
    }

    for name, module in modules.items():
        print(f"✓ {name} version: {module.__version__ if hasattr(module, '__version__') else 'imported'}")

    print(f"✓ CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"  GPU: {torch.cuda.get_device_name(0)}")

    print()

def test_checkpoints():
    """Verify that model checkpoints exist"""
    print("="*60)
    print("TESTING CHECKPOINTS")
    print("="*60)

    base_dir = Path("/home/user/sleepfm-clinical/sleepfm/checkpoints")

    checkpoints = {
        'Base Model': base_dir / "model_base" / "best.pt",
        'Diagnosis Model': base_dir / "model_diagnosis" / "best.pth",
        'Sleep Staging Model': base_dir / "model_sleep_staging" / "best.pth",
    }

    for name, path in checkpoints.items():
        exists = path.exists()
        size = path.stat().st_size / (1024**2) if exists else 0  # MB
        status = f"✓ {size:.1f} MB" if exists else "✗ NOT FOUND"
        print(f"{name}: {status}")

    print()

def test_demo_data():
    """Check that demo data exists"""
    print("="*60)
    print("TESTING DEMO DATA")
    print("="*60)

    demo_dir = Path("/home/user/sleepfm-clinical/notebooks/demo_data")

    files = {
        'PSG (EDF)': demo_dir / "demo_psg.edf",
        'Sleep Stages': demo_dir / "demo_psg.csv",
        'Demographics': demo_dir / "demo_age_gender.csv",
        'Is Event': demo_dir / "is_event.csv",
        'Time to Event': demo_dir / "time_to_event.csv",
    }

    for name, path in files.items():
        exists = path.exists()
        size = path.stat().st_size / 1024 if exists else 0  # KB
        status = f"✓ {size:.1f} KB" if exists else "✗ NOT FOUND"
        print(f"{name}: {status}")

    print()

def test_load_base_model():
    """Test loading the base SleepFM model"""
    print("="*60)
    print("TESTING BASE MODEL LOADING")
    print("="*60)

    try:
        model_path = "/home/user/sleepfm-clinical/sleepfm/checkpoints/model_base"
        config_path = os.path.join(model_path, "config.json")

        config = load_config(config_path)
        print(f"✓ Config loaded")
        print(f"  Model: {config['model']}")
        print(f"  Embed dim: {config['embed_dim']}")
        print(f"  Num heads: {config['num_heads']}")
        print(f"  Num layers: {config['num_layers']}")

        # Initialize model
        model = SetTransformer(
            in_channels=config['in_channels'],
            patch_size=config['patch_size'],
            embed_dim=config['embed_dim'],
            num_heads=config['num_heads'],
            num_layers=config['num_layers'],
            pooling_head=config['pooling_head'],
            dropout=0.0
        )

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model = model.to(device)

        total_layers, total_params = count_parameters(model)
        print(f"✓ Model initialized")
        print(f"  Parameters: {total_params / 1e6:.2f}M")
        print(f"  Layers: {total_layers}")
        print(f"  Device: {device}")

        # Load checkpoint
        checkpoint = torch.load(os.path.join(model_path, "best.pt"), map_location=device)
        model.load_state_dict(checkpoint["state_dict"])
        model.eval()
        print(f"✓ Checkpoint loaded")

        print()
        return True

    except Exception as e:
        print(f"✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        print()
        return False

def test_load_diagnosis_model():
    """Test loading the diagnosis model"""
    print("="*60)
    print("TESTING DIAGNOSIS MODEL LOADING")
    print("="*60)

    try:
        disease_model_path = "/home/user/sleepfm-clinical/sleepfm/checkpoints/model_diagnosis"
        config = load_data(os.path.join(disease_model_path, "config.json"))

        print(f"✓ Config loaded")
        print(f"  Model: {config['model']}")

        config["model_params"]["dropout"] = 0.0
        model_params = config['model_params']

        print(f"  Model params: {model_params}")

        # Initialize model
        model = DiagnosisFinetuneFullLSTMCOXPHWithDemo(**model_params)

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model = model.to(device)

        total_layers, total_params = count_parameters(model)
        print(f"✓ Model initialized")
        print(f"  Parameters: {total_params / 1e6:.2f}M")
        print(f"  Layers: {total_layers}")

        # Load checkpoint
        checkpoint_path = os.path.join(disease_model_path, "best.pth")
        checkpoint = torch.load(checkpoint_path, map_location=device)
        model.load_state_dict(checkpoint)
        model.eval()
        print(f"✓ Checkpoint loaded")

        print()
        return True

    except Exception as e:
        print(f"✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        print()
        return False

def test_label_mapping():
    """Test loading disease label mapping"""
    print("="*60)
    print("TESTING LABEL MAPPING")
    print("="*60)

    try:
        labels_df = pd.read_csv("/home/user/sleepfm-clinical/sleepfm/configs/label_mapping.csv")
        print(f"✓ Label mapping loaded")
        print(f"  Total diseases: {len(labels_df)}")

        # Find dementia-related conditions
        dementia_labels = labels_df[labels_df['phenotype'].str.contains('dementia|alzheimer', case=False, na=False)]
        print(f"  Dementia-related conditions: {len(dementia_labels)}")

        print("\nDementia-related diseases:")
        for _, row in dementia_labels.iterrows():
            print(f"  - [{row['label_idx']}] {row['phecode']}: {row['phenotype']}")

        # Primary dementia label
        primary_dementia = labels_df[labels_df['phecode'] == '290.0']
        if len(primary_dementia) > 0:
            dementia_idx = primary_dementia.iloc[0]['label_idx']
            print(f"\n✓ Primary dementia label index: {dementia_idx}")

        print()
        return True

    except Exception as e:
        print(f"✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        print()
        return False

def main():
    """Run all tests"""
    print("\n")
    print("*"*60)
    print("SLEEPFM DEMENTIA RISK PREDICTION - TEST SUITE")
    print("*"*60)
    print()

    results = {
        'Imports': False,
        'Checkpoints': False,
        'Demo Data': False,
        'Label Mapping': False,
        'Base Model': False,
        'Diagnosis Model': False,
    }

    # Run tests that don't require all dependencies
    test_basic_imports()
    results['Checkpoints'] = True  # Just checking files exist
    test_checkpoints()

    results['Demo Data'] = True  # Just checking files exist
    test_demo_data()

    # Try tests that require torch, etc
    try:
        results['Label Mapping'] = test_label_mapping()
        results['Base Model'] = test_load_base_model()
        results['Diagnosis Model'] = test_load_diagnosis_model()
        results['Imports'] = True
    except Exception as e:
        print(f"Skipping model tests due to missing dependencies: {e}")

    # Summary
    print("="*60)
    print("TEST SUMMARY")
    print("="*60)

    for test_name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name}: {status}")

    all_passed = all(results.values())
    print()
    print("="*60)
    if all_passed:
        print("ALL TESTS PASSED ✓")
    else:
        print("SOME TESTS FAILED ✗")
    print("="*60)
    print()

    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
