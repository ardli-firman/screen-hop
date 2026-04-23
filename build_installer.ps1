param(
    [string]$PythonCmd = "python",
    [string]$IsccPath = "",
    [switch]$SkipDependencyInstall
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$installerScript = Join-Path $projectRoot "installer\browser_move_win7.iss"
$distDir = Join-Path $projectRoot "dist\browser_move"

function Get-PythonVersionString {
    param([string]$PythonExecutable)

    & $PythonExecutable -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')"
}

function Get-AppVersion {
    param([string]$PythonExecutable, [string]$RootPath)

    $version = & $PythonExecutable -c "import pathlib,re; p=pathlib.Path(r'$RootPath')/'src'/'browser_move'/'__init__.py'; t=p.read_text(encoding='utf-8'); m=re.search(r""__version__\s*=\s*['""]([^'""]+)['""]"", t); print(m.group(1) if m else '1.0.0')"
    if (-not $version) {
        return "1.0.0"
    }
    return $version.Trim()
}

function Resolve-IsccPath {
    param([string]$ExplicitPath)

    if ($ExplicitPath -and (Test-Path $ExplicitPath)) {
        return (Resolve-Path $ExplicitPath).Path
    }

    if ($env:ISCC_PATH -and (Test-Path $env:ISCC_PATH)) {
        return (Resolve-Path $env:ISCC_PATH).Path
    }

    $candidates = @(
        "C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        "C:\Program Files\Inno Setup 6\ISCC.exe",
        "C:\Program Files (x86)\Inno Setup 7\ISCC.exe",
        "C:\Program Files\Inno Setup 7\ISCC.exe"
    )

    foreach ($candidate in $candidates) {
        if (Test-Path $candidate) {
            return (Resolve-Path $candidate).Path
        }
    }

    throw "ISCC.exe not found. Install Inno Setup or pass -IsccPath."
}

if (-not (Test-Path $installerScript)) {
    throw "Installer script not found: $installerScript"
}

$pythonVersion = Get-PythonVersionString -PythonExecutable $PythonCmd
if (-not $pythonVersion.StartsWith("3.8.")) {
    throw "Windows 7 build must use Python 3.8.x. Current: $pythonVersion"
}

Write-Host "Using Python $pythonVersion"

if (-not $SkipDependencyInstall) {
    Write-Host "Installing dependencies from requirements.txt..."
    & $PythonCmd -m pip install --upgrade pip
    & $PythonCmd -m pip install -r (Join-Path $projectRoot "requirements.txt")
}

Write-Host "Building PyInstaller bundle..."
& $PythonCmd -m PyInstaller --noconfirm --clean (Join-Path $projectRoot "browser_move.spec")

if (-not (Test-Path (Join-Path $distDir "browser_move.exe"))) {
    throw "Build failed: browser_move.exe not found at $distDir"
}

$appVersion = Get-AppVersion -PythonExecutable $PythonCmd -RootPath $projectRoot
$iscc = Resolve-IsccPath -ExplicitPath $IsccPath

Write-Host "Compiling installer with ISCC: $iscc"
& $iscc "/DAppVersion=$appVersion" "/DDistDir=$distDir" "$installerScript"

Write-Host "Done. Installer output is in dist\installer\"
