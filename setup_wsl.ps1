# WSL2 and Docker Setup Helper
# Run this script as Administrator

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "This script needs to be run as Administrator. Please restart PowerShell as Administrator." -ForegroundColor Red
    exit
}

Write-Host "WSL2 and Docker Setup Helper" -ForegroundColor Cyan
Write-Host "============================" -ForegroundColor Cyan

# Step 1: Enable Windows features
Write-Host "`nStep 1: Enabling required Windows features..." -ForegroundColor Yellow
Write-Host "This may require a system restart after completion."

# Enable WSL and Virtual Machine Platform
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

# Step 2: Download and install WSL2 kernel update
Write-Host "`nStep 2: Downloading WSL2 Linux kernel update package..." -ForegroundColor Yellow
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

# Step 3: Set WSL2 as default
Write-Host "`nStep 3: Setting WSL2 as default version..." -ForegroundColor Yellow
wsl --set-default-version 2

# Step 4: Check Docker Desktop installation
Write-Host "`nStep 4: Checking Docker Desktop installation..." -ForegroundColor Yellow
$dockerPath = "C:\Program Files\Docker\Docker\Docker Desktop.exe"
if (Test-Path $dockerPath) {
    Write-Host "Docker Desktop is already installed." -ForegroundColor Green
} else {
    Write-Host "Docker Desktop is not installed." -ForegroundColor Yellow
    $installDocker = Read-Host "Would you like to download Docker Desktop? (y/n)"
    if ($installDocker -eq "y") {
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

# Step 5: Install Git if not already installed
Write-Host "`nStep 5: Checking Git installation..." -ForegroundColor Yellow
try {
    $gitVersion = git --version
    Write-Host "Git is already installed: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "Git is not installed." -ForegroundColor Yellow
    $installGit = Read-Host "Would you like to download Git? (y/n)"
    if ($installGit -eq "y") {
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

# Step 6: Install kubectl if not already installed
Write-Host "`nStep 6: Checking kubectl installation..." -ForegroundColor Yellow
try {
    $kubectlVersion = kubectl version --client
    Write-Host "kubectl is already installed." -ForegroundColor Green
} catch {
    Write-Host "kubectl is not installed." -ForegroundColor Yellow
    $installKubectl = Read-Host "Would you like to download kubectl? (y/n)"
    if ($installKubectl -eq "y") {
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
}

Write-Host "`nSetup completed!" -ForegroundColor Green
Write-Host "NOTE: You may need to restart your computer for all changes to take effect." -ForegroundColor Yellow
Write-Host "After restarting, you should be able to use Docker Desktop with WSL2 backend." -ForegroundColor Yellow

Read-Host "Press Enter to exit"