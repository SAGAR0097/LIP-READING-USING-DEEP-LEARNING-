# Run this script as administrator
$ErrorActionPreference = "Stop"

Write-Host "Starting FFmpeg installation..."

# Create directories
Write-Host "Creating directories..."
$ffmpegDir = "C:\ffmpeg"
New-Item -ItemType Directory -Force -Path $ffmpegDir | Out-Null

# Download FFmpeg
Write-Host "Downloading FFmpeg..."
$url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
$output = "C:\ffmpeg\ffmpeg.zip"

# Using .NET WebClient to download
$webClient = New-Object System.Net.WebClient
$webClient.DownloadFile($url, $output)

# Extract the ZIP file
Write-Host "Extracting FFmpeg..."
Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::ExtractToDirectory($output, $ffmpegDir)

# Move files from nested directory to main ffmpeg directory
Write-Host "Setting up FFmpeg..."
$extractedDir = Get-ChildItem -Path $ffmpegDir -Filter "ffmpeg-master-*" -Directory | Select-Object -First 1
Move-Item -Path "$($extractedDir.FullName)\bin\*" -Destination $ffmpegDir -Force

# Add to PATH
Write-Host "Adding FFmpeg to System PATH..."
$path = [Environment]::GetEnvironmentVariable("Path", "Machine")
if (-not $path.Contains($ffmpegDir)) {
    [Environment]::SetEnvironmentVariable("Path", $path + ";$ffmpegDir", "Machine")
}

# Clean up
Write-Host "Cleaning up..."
Remove-Item -Path $output -Force
Remove-Item -Path $extractedDir.FullName -Recurse -Force

Write-Host "FFmpeg installation complete!"
Write-Host "Please restart your PowerShell/Command Prompt and type 'ffmpeg -version' to verify installation"