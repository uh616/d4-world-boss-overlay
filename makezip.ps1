$files = "overlay.py", "start_overlay.bat", "install.bat", "requirements.txt", "logo.png", "README.md"
$zip = "D4-Overlay-v1.0.0.zip"
if (Test-Path $zip) { Remove-Item $zip }
Add-Type -Assembly System.IO.Compression.FileSystem
$zipPath = [System.IO.Path]::GetFullPath($zip)
$zipArchive = [System.IO.Compression.ZipFile]::Open($zipPath, 'Create')
foreach ($f in $files) {
    if (Test-Path $f) {
        [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($zipArchive, $f, $f)
    }
}
$zipArchive.Dispose()
Write-Host "Created $zip"
