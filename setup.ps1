# Cluster Health Monitor - Setup Script
# Automated setup for Windows with CUDA detection

$ErrorActionPreference = "Stop"

Write-Host "`n=== Cluster Health Monitor Setup ===" -ForegroundColor Cyan
Write-Host "Version 1.0.0`n" -ForegroundColor Cyan

# Check Python
Write-Host "Checking Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[OK] $pythonVersion" -ForegroundColor Green
    
    # Check version >= 3.8
    $versionMatch = $pythonVersion -match "Python (\d+)\.(\d+)"
    if ($versionMatch) {
        $major = [int]$matches[1]
        $minor = [int]$matches[2]
        if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 8)) {
            Write-Host "[ERROR] Python 3.8+ required" -ForegroundColor Red
            exit 1
        }
    }
} catch {
    Write-Host "[ERROR] Python not found. Install from https://www.python.org/downloads/" -ForegroundColor Red
    exit 1
}

# Check NVIDIA drivers
Write-Host "`nChecking NVIDIA drivers..." -ForegroundColor Yellow
$nvidiaFound = $false
try {
    $nvidiaSmi = nvidia-smi --version 2>&1 | Out-String
    Write-Host "[OK] nvidia-smi found" -ForegroundColor Green
    $nvidiaFound = $true
    
    # Parse driver version
    if ($nvidiaSmi -match "Driver Version: ([\d\.]+)") {
        Write-Host "Driver Version: $($matches[1])" -ForegroundColor Cyan
    }
} catch {
    Write-Host "[WARNING] nvidia-smi not found" -ForegroundColor Yellow
    Write-Host "Install NVIDIA drivers: https://www.nvidia.com/download/index.aspx" -ForegroundColor Yellow
}

# Check CUDA
Write-Host "`nChecking CUDA Toolkit..." -ForegroundColor Yellow
$cudaFound = $false
$cudaVersion = ""

try {
    $nvccVersion = nvcc --version 2>&1 | Out-String
    if ($nvccVersion -match "release (\d+\.\d+)") {
        $cudaVersion = $matches[1]
        $cudaFound = $true
        Write-Host "[OK] CUDA $cudaVersion detected" -ForegroundColor Green
    }
} catch {
    Write-Host "[WARNING] CUDA Toolkit not found" -ForegroundColor Yellow
    Write-Host "GPU benchmarking requires CUDA. Download from:" -ForegroundColor Yellow
    Write-Host "https://developer.nvidia.com/cuda-downloads" -ForegroundColor Cyan
}

# Summary and user choice
Write-Host "`n=== Setup Options ===" -ForegroundColor Cyan
Write-Host "This will:" -ForegroundColor White
Write-Host "  1. Create Python virtual environment" -ForegroundColor White
Write-Host "  2. Install core dependencies (FastAPI, uvicorn, etc.)" -ForegroundColor White

if ($cudaFound) {
    Write-Host "  3. Optionally install GPU libraries (CuPy or PyTorch)" -ForegroundColor White
} else {
    Write-Host "  3. Run in monitoring-only mode (no GPU benchmarking)" -ForegroundColor Yellow
}

Write-Host ""
$continue = Read-Host "Continue with setup? [Y/n]"
if ($continue -eq "n" -or $continue -eq "N") {
    Write-Host "`nSetup cancelled." -ForegroundColor Yellow
    exit 0
}

# Create virtual environment
Write-Host "`nCreating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "[OK] Virtual environment already exists" -ForegroundColor Green
} else {
    python -m venv venv
    Write-Host "[OK] Virtual environment created" -ForegroundColor Green
}

# Activate venv
Write-Host "`nActivating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Upgrade pip
Write-Host "`nUpgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet

# Install core dependencies
Write-Host "`nInstalling core dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet
Write-Host "[OK] Core dependencies installed" -ForegroundColor Green

# GPU benchmark libraries
if ($cudaFound) {
    Write-Host "`n=== GPU Benchmark Libraries ===" -ForegroundColor Cyan
    Write-Host "CUDA $cudaVersion detected. Install GPU libraries for benchmarking?" -ForegroundColor Yellow
    Write-Host "  1) CuPy (recommended for CUDA 12.x)" -ForegroundColor White
    Write-Host "  2) PyTorch (alternative)" -ForegroundColor White
    Write-Host "  3) Skip (passive monitoring only)" -ForegroundColor White
    
    $choice = Read-Host "`nChoice [1-3]"
    
    switch ($choice) {
        "1" {
            Write-Host "`nInstalling CuPy..." -ForegroundColor Yellow
            if ($cudaVersion -match "^12") {
                pip install cupy-cuda12x --quiet
            } elseif ($cudaVersion -match "^11") {
                pip install cupy-cuda11x --quiet
            } else {
                Write-Host "[WARNING] Unsupported CUDA version, trying cuda12x" -ForegroundColor Yellow
                pip install cupy-cuda12x --quiet
            }
            Write-Host "[OK] CuPy installed" -ForegroundColor Green
        }
        "2" {
            Write-Host "`nInstalling PyTorch..." -ForegroundColor Yellow
            if ($cudaVersion -match "^12") {
                pip install torch --index-url https://download.pytorch.org/whl/cu121 --quiet
            } elseif ($cudaVersion -match "^11") {
                pip install torch --index-url https://download.pytorch.org/whl/cu118 --quiet
            }
            Write-Host "[OK] PyTorch installed" -ForegroundColor Green
        }
        "3" {
            Write-Host "[OK] Skipping GPU libraries" -ForegroundColor Yellow
        }
        default {
            Write-Host "[OK] Skipping GPU libraries" -ForegroundColor Yellow
        }
    }
}

# Detect features and cache
Write-Host "`nDetecting available features..." -ForegroundColor Yellow
python -c "from monitor.utils import detect_features; detect_features(force=True)"
Write-Host "[OK] Features cached" -ForegroundColor Green

# Verify installation
Write-Host "`nVerifying installation..." -ForegroundColor Yellow
try {
    python health_monitor.py --help > $null 2>&1
    Write-Host "[OK] Installation verified" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Installation verification failed" -ForegroundColor Red
    exit 1
}

# Complete
Write-Host "`n=== Setup Complete ===" -ForegroundColor Green
Write-Host "`nTo get started:" -ForegroundColor Cyan
Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "  python health_monitor.py" -ForegroundColor White
Write-Host "`nAccess web dashboard at: http://localhost:8090" -ForegroundColor Cyan
Write-Host "Change port: python health_monitor.py --port 3000" -ForegroundColor DarkGray
Write-Host "`nOther commands:" -ForegroundColor Cyan
Write-Host "  python health_monitor.py cli       - Terminal dashboard" -ForegroundColor White
Write-Host "  python health_monitor.py benchmark - GPU benchmark" -ForegroundColor White
Write-Host "  python health_monitor.py --update  - Check for updates`n" -ForegroundColor White
