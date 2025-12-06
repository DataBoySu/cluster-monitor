"""Update mechanism for cluster health monitor."""

import requests
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import Optional, Dict

GITHUB_API = "https://api.github.com/repos/DataBoySu/cluster-monitor/releases/latest"
CURRENT_VERSION = "1.0.0"

def get_latest_version() -> Optional[Dict]:
    """
    Check GitHub for latest release.
    
    Returns:
        dict with 'version' and 'download_url', or None if error
    """
    try:
        response = requests.get(GITHUB_API, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        version = data.get('tag_name', '').lstrip('v')
        assets = data.get('assets', [])
        
        # Find ZIP asset
        download_url = None
        for asset in assets:
            if asset['name'].endswith('.zip'):
                download_url = asset['browser_download_url']
                break
        
        if not download_url:
            return None
        
        return {
            'version': version,
            'download_url': download_url,
            'name': data.get('name', ''),
            'body': data.get('body', '')
        }
    except Exception:
        return None

def compare_versions(v1: str, v2: str) -> int:
    """
    Compare two version strings.
    
    Returns:
        -1 if v1 < v2, 0 if equal, 1 if v1 > v2
    """
    def parse_version(v):
        return [int(x) for x in v.split('.')]
    
    try:
        parts1 = parse_version(v1)
        parts2 = parse_version(v2)
        
        for p1, p2 in zip(parts1, parts2):
            if p1 < p2:
                return -1
            elif p1 > p2:
                return 1
        
        if len(parts1) < len(parts2):
            return -1
        elif len(parts1) > len(parts2):
            return 1
        
        return 0
    except Exception:
        return 0

def download_update(url: str, dest: Path) -> bool:
    """Download update ZIP file."""
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        with open(dest, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return True
    except Exception:
        return False

def apply_update(zip_path: Path) -> bool:
    """
    Extract update ZIP and replace files.
    """
    try:
        # Extract to temp directory
        temp_dir = Path("update_temp")
        temp_dir.mkdir(exist_ok=True)
        
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(temp_dir)
        
        # Find extracted directory
        extracted = list(temp_dir.glob("cluster-health-monitor*"))
        if not extracted:
            return False
        
        src = extracted[0]
        
        # Copy files (excluding venv, cache, data)
        import shutil
        exclude = {'venv', '__pycache__', '.features_cache', '*.db', 'config.yaml'}
        
        for item in src.rglob('*'):
            if item.is_file():
                rel = item.relative_to(src)
                
                # Skip excluded patterns
                skip = False
                for ex in exclude:
                    if ex in str(rel):
                        skip = True
                        break
                
                if not skip:
                    dest = Path(rel)
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, dest)
        
        # Cleanup
        shutil.rmtree(temp_dir)
        zip_path.unlink()
        
        return True
    except Exception:
        return False

def check_for_updates() -> Dict:
    """
    Check for updates and return status.
    
    Returns:
        dict with 'available', 'current', 'latest', 'info'
    """
    latest = get_latest_version()
    
    if not latest:
        return {
            'available': False,
            'current': CURRENT_VERSION,
            'latest': None,
            'error': 'Could not check for updates'
        }
    
    latest_version = latest['version']
    is_newer = compare_versions(latest_version, CURRENT_VERSION) > 0
    
    return {
        'available': is_newer,
        'current': CURRENT_VERSION,
        'latest': latest_version,
        'info': latest
    }

def perform_update() -> bool:
    """
    Download and apply update.
    
    Returns:
        True if successful
    """
    latest = get_latest_version()
    if not latest:
        return False
    
    # Download
    zip_path = Path("update.zip")
    if not download_update(latest['download_url'], zip_path):
        return False
    
    # Apply
    return apply_update(zip_path)
