# Package Cluster Health Monitor for distribution
# Creates portable ZIP for users to download

$ErrorActionPreference = "Stop"

$VERSION = "1.0.0"
$OUTPUT_NAME = "cluster-health-monitor-v$VERSION"
$OUTPUT_ZIP = "$OUTPUT_NAME.zip"

Write-Host "`n=== Packaging Cluster Health Monitor v$VERSION ===" -ForegroundColor Cyan

# Clean previous build
if (Test-Path $OUTPUT_NAME) {
    Write-Host "Removing old build directory..." -ForegroundColor Yellow
    Remove-Item $OUTPUT_NAME -Recurse -Force
}

if (Test-Path $OUTPUT_ZIP) {
    Write-Host "Removing old ZIP..." -ForegroundColor Yellow
    Remove-Item $OUTPUT_ZIP -Force
}

# Create build directory
Write-Host "Creating build directory..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path $OUTPUT_NAME | Out-Null

# Copy project files
Write-Host "Copying project files..." -ForegroundColor Yellow

$include = @(
    "monitor",
    "health_monitor.py",
    "config.yaml",
    "requirements.txt",
    "setup.ps1",
    "README.md",
    "LICENSE"
)

foreach ($item in $include) {
    if (Test-Path $item) {
        Write-Host "  - $item"
        Copy-Item $item -Destination $OUTPUT_NAME -Recurse
    }
}

# Remove unwanted files
Write-Host "Cleaning build directory..." -ForegroundColor Yellow

$cleanup = @(
    "__pycache__",
    "*.pyc",
    "*.pyo",
    ".features_cache",
    "*.db",
    ".pytest_cache",
    ".vscode"
)

Get-ChildItem $OUTPUT_NAME -Recurse -Force | Where-Object {
    $file = $_
    $cleanup | Where-Object { $file.Name -like $_ } | Select-Object -First 1
} | Remove-Item -Force -Recurse

# Create ZIP
Write-Host "`nCreating ZIP archive..." -ForegroundColor Yellow
Compress-Archive -Path $OUTPUT_NAME -DestinationPath $OUTPUT_ZIP -Force

# Calculate size
$size = (Get-Item $OUTPUT_ZIP).Length / 1MB

Write-Host "`n=== Package Complete ===" -ForegroundColor Green
Write-Host "Output: $OUTPUT_ZIP" -ForegroundColor Cyan
Write-Host "Size: $([math]::Round($size, 2)) MB" -ForegroundColor Cyan
Write-Host "`nUpload to GitHub Releases:" -ForegroundColor Yellow
Write-Host "https://github.com/DataBoySu/cluster-monitor/releases/new`n" -ForegroundColor Cyan

# Cleanup build directory
if (Test-Path $OUTPUT_NAME) {
    Remove-Item $OUTPUT_NAME -Recurse -Force
}
