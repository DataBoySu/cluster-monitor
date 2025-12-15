"""Feature detection and caching system."""
"""Feature detection utilities for optional dependencies.

Maintenance:
- Purpose: centralize detection of optional libraries (CuPy, PyTorch, NVML).
- Debug: use these helpers from startup to conditionally enable features.
"""

import json
import os
from pathlib import Path
from typing import Dict

CACHE_FILE = '.features_cache'

def _detect_nvidia_smi() -> bool:
    """Check if nvidia-smi is available."""
    try:
        import subprocess
        result = subprocess.run(['nvidia-smi', '--version'], 
                              capture_output=True, timeout=5)
        return result.returncode == 0
    except Exception:
        return False

def _detect_cupy() -> bool:
    """Check if cupy is available."""
    try:
        import cupy as cp
        cp.cuda.Device(0).compute_capability
        return True
    except Exception:
        return False

def _detect_torch() -> bool:
    """Check if torch with CUDA is available."""
    try:
        import torch
        return torch.cuda.is_available()
    except Exception:
        return False

def detect_features(force: bool = False) -> Dict[str, bool]:
    """
    Detect available features. Uses cache unless force=True.
    
    Returns:
        dict: {'nvidia_smi': bool, 'cupy': bool, 'torch': bool, 'gpu_benchmark': bool}
    """
    cache_path = Path(CACHE_FILE)
    
    # Check cache
    if not force and cache_path.exists():
        try:
            with open(cache_path, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    
    # Detect features
    features = {
        'nvidia_smi': _detect_nvidia_smi(),
        'cupy': _detect_cupy(),
        'torch': _detect_torch(),
    }
    
    # GPU benchmark available if cupy or torch available
    features['gpu_benchmark'] = features['cupy'] or features['torch']
    
    # Cache results
    try:
        with open(cache_path, 'w') as f:
            json.dump(features, f, indent=2)
    except Exception:
        pass
    
    return features

def get_features() -> Dict[str, bool]:
    """Get cached features or detect them."""
    return detect_features(force=False)

def refresh_features() -> Dict[str, bool]:
    """Force feature re-detection."""
    return detect_features(force=True)
