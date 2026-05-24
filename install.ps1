# Create a short temp dir on D: to avoid Windows 260-char path limit
New-Item -ItemType Directory -Force -Path "D:\tmp" | Out-Null
New-Item -ItemType Directory -Force -Path "D:\pip-cache" | Out-Null

# Override temp for this session only
$env:TEMP = "D:\tmp"
$env:TMP  = "D:\tmp"

# Install with both temp and cache redirected
pip install llama-cpp-python huggingface_hub --cache-dir D:\pip-cache