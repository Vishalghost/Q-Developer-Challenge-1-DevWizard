# DevOps Tools Installer
# Run this script as Administrator

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "This script needs to be run as Administrator. Please restart PowerShell as Administrator." -ForegroundColor Red
    exit
}

Write-Host "DevOps Tools Installer" -ForegroundColor Cyan
Write-Host "====================" -ForegroundColor Cyan

# Function to check if a command exists
function Test-CommandExists {
    param ($command)
    $exists = $false
    try {
        if (Get-Command $command -ErrorAction Stop) {
            $exists = $true
        }
    } catch {}
    return $exists
}

# Check if winget is available
$useWinget = Test-CommandExists "winget"
if (-not $useWinget) {
    Write-Host "Winget is not available. Will use direct downloads instead." -ForegroundColor Yellow
}

# Install Git
Write-Host "`nInstalling Git..." -ForegroundColor Yellow
if (Test-CommandExists "git") {
    $gitVersion = & git --version
    Write-Host "Git is already installed: $gitVersion" -ForegroundColor Green
} else {
    if ($useWinget) {
        Write-Host "Installing Git using winget..."
        winget install --id Git.Git -e --source winget
    } else {
        $gitUrl = "https://github.com/git-for-windows/git/releases/download/v2.40.0.windows.1/Git-2.40.0-64-bit.exe"
        $gitInstallerPath = "$env:TEMP\git-installer.exe"
        
        try {
            Write-Host "Downloading Git installer..."
            Invoke-WebRequest -Uri $gitUrl -OutFile $gitInstallerPath -UseBasicParsing
            Write-Host "Starting Git installer..."
            Start-Process -FilePath $gitInstallerPath -Wait
            Write-Host "Git installation completed." -ForegroundColor Green
        } catch {
            Write-Host "Failed to download or install Git: $_" -ForegroundColor Red
        }
    }
}

# Enable WSL2 features
Write-Host "`nEnabling WSL2 features..." -ForegroundColor Yellow
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

# Download and install WSL2 kernel update
Write-Host "`nDownloading WSL2 Linux kernel update package..." -ForegroundColor Yellow
$wslUpdateUrl = "https://wslstorestorage.blob.core.windows.net/wslblob/wsl_update_x64.msi"
$wslUpdateInstallerPath = "$env:TEMP\wsl_update_x64.msi"

try {
    Invoke-WebRequest -Uri $wslUpdateUrl -OutFile $wslUpdateInstallerPath -UseBasicParsing
    Write-Host "Installing WSL2 Linux kernel update package..."
    Start-Process -FilePath "msiexec.exe" -ArgumentList "/i `"$wslUpdateInstallerPath`" /quiet" -Wait
    Write-Host "WSL2 Linux kernel update package installed successfully." -ForegroundColor Green
} catch {
    Write-Host "Failed to download or install WSL2 Linux kernel update package: $_" -ForegroundColor Red
}

# Set WSL2 as default
Write-Host "`nSetting WSL2 as default version..." -ForegroundColor Yellow
wsl --set-default-version 2

# Install Docker Desktop
Write-Host "`nInstalling Docker Desktop..." -ForegroundColor Yellow
$dockerPath = "C:\Program Files\Docker\Docker\Docker Desktop.exe"
if (Test-Path $dockerPath) {
    Write-Host "Docker Desktop is already installed." -ForegroundColor Green
} else {
    if ($useWinget) {
        Write-Host "Installing Docker Desktop using winget..."
        winget install Docker.DockerDesktop
    } else {
        $dockerUrl = "https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe"
        $dockerInstallerPath = "$env:TEMP\DockerDesktopInstaller.exe"
        
        try {
            Write-Host "Downloading Docker Desktop installer..."
            Invoke-WebRequest -Uri $dockerUrl -OutFile $dockerInstallerPath -UseBasicParsing
            Write-Host "Starting Docker Desktop installer..."
            Start-Process -FilePath $dockerInstallerPath -Wait
            Write-Host "Docker Desktop installation completed." -ForegroundColor Green
        } catch {
            Write-Host "Failed to download or install Docker Desktop: $_" -ForegroundColor Red
        }
    }
}

# Install kubectl
Write-Host "`nInstalling kubectl..." -ForegroundColor Yellow
if (Test-CommandExists "kubectl") {
    Write-Host "kubectl is already installed." -ForegroundColor Green
} else {
    try {
        $version = (Invoke-RestMethod "https://storage.googleapis.com/kubernetes-release/release/stable.txt")
        $url = "https://storage.googleapis.com/kubernetes-release/release/$version/bin/windows/amd64/kubectl.exe"
        $outputPath = "$env:USERPROFILE\.kubectl\kubectl.exe"
        
        # Create directory if it doesn't exist
        New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.kubectl"
        
        # Download kubectl
        Write-Host "Downloading kubectl..."
        Invoke-WebRequest -Uri $url -OutFile $outputPath -UseBasicParsing
        
        # Add to PATH
        $currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
        if ($currentPath -notlike "*$env:USERPROFILE\.kubectl*") {
            [Environment]::SetEnvironmentVariable("Path", $currentPath + ";$env:USERPROFILE\.kubectl", "User")
            Write-Host "Added kubectl to PATH." -ForegroundColor Green
        }
        
        Write-Host "kubectl installation completed." -ForegroundColor Green
    } catch {
        Write-Host "Failed to download or install kubectl: $_" -ForegroundColor Red
    }
}

Write-Host "`nInstallation completed!" -ForegroundColor Green
Write-Host "NOTE: You need to restart your computer for all changes to take effect." -ForegroundColor Yellow
Write-Host "After restarting, you should be able to use Git, Docker with WSL2 backend, and kubectl." -ForegroundColor Yellow

Read-Host "Press Enter to exit"