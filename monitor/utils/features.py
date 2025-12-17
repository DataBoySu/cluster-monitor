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

def _cupy_info():
    """Return CuPy presence and whether it is built for CUDA 12.x.

    Returns: (present: bool, cuda_ok: bool)
    """
    try:
        import cupy as cp
    except Exception:
        return (False, False)

    # Try to detect CuPy's compiled CUDA runtime version. Several accessors exist.
    cuda_version = None
    try:
        v = getattr(cp, 'cuda', None)
        if v is not None and hasattr(v, 'runtime') and hasattr(v.runtime, 'get_runtime_version'):
            rv = v.runtime.get_runtime_version()
            cuda_version = str(rv)
    except Exception:
        cuda_version = None

    if cuda_version is None:
        try:
            if hasattr(cp, 'cuda') and hasattr(cp.cuda, 'runtime') and hasattr(cp.cuda.runtime, 'runtimeGetVersion'):
                rv = cp.cuda.runtime.runtimeGetVersion()
                cuda_version = str(rv)
        except Exception:
            cuda_version = None

    if cuda_version is None:
        try:
            if hasattr(cp.cuda, 'get_runtime_version'):
                rv = cp.cuda.get_runtime_version()
                cuda_version = str(rv)
        except Exception:
            cuda_version = None

    cuda_major = None
    try:
        if cuda_version:
            s = str(cuda_version)
            if s.startswith('12'):
                cuda_major = 12
            else:
                if '.' in s and s.split('.')[0] == '12':
                    cuda_major = 12
    except Exception:
        cuda_major = None

    # Validate device access
    try:
        cp.cuda.Device(0).compute_capability
    except Exception:
        # present but cannot access device
        return (True, False)

    return (True, cuda_major == 12)

def _torch_info():
    """Return (present: bool, cuda_ok: bool) for PyTorch.

    We enforce CUDA 12.x only.
    """
    try:
        import torch
    except Exception:
        return (False, False)

    cuda_report = getattr(torch.version, 'cuda', None)
    if cuda_report is None:
        return (True, False)
    try:
        major = str(cuda_report).split('.')[0]
        cuda_ok = (major == '12') and torch.cuda.is_available()
    except Exception:
        cuda_ok = False
    return (True, cuda_ok)

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
    cupy_present, cupy_ok = _cupy_info()
    torch_present, torch_ok = _torch_info()

    features = {
        'nvidia_smi': _detect_nvidia_smi(),
        # `cupy` indicates CuPy is installed and compiled for CUDA 12.x
        'cupy': cupy_present and cupy_ok,
        'cupy_present': cupy_present,
        'cupy_cuda_ok': cupy_ok,
        # `torch` indicates PyTorch is installed and compiled for CUDA 12.x
        'torch': torch_present and torch_ok,
        'torch_present': torch_present,
        'torch_cuda_ok': torch_ok,
    }

    # GPU benchmark available if cupy or torch available (with CUDA 12.x)
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
