#!/usr/bin/env python
"""
Platform-specific utilities for DevWizard
"""
import os
import sys
import platform
import subprocess
import tempfile

def get_platform():
    """Get the current platform: 'windows', 'macos', or 'linux'"""
    system = platform.system().lower()
    if system == 'darwin':
        return 'macos'
    elif system == 'windows':
        return 'windows'
    elif system == 'linux':
        return 'linux'
    else:
        return 'unknown'

def get_tool_path(tool_name, platform_type=None):
    """Get the default path for a tool on the current platform"""
    if platform_type is None:
        platform_type = get_platform()
    
    paths = {
        'windows': {
            'git': 'C:\\Program Files\\Git\\bin\\git.exe',
            'docker': 'C:\\Program Files\\Docker\\Docker\\resources\\bin\\docker.exe',
            'kubectl': os.path.expandvars('%USERPROFILE%\\.kubectl\\kubectl.exe'),
        },
        'macos': {
            'git': '/usr/bin/git',
            'docker': '/usr/local/bin/docker',
            'kubectl': '/usr/local/bin/kubectl',
        },
        'linux': {
            'git': '/usr/bin/git',
            'docker': '/usr/bin/docker',
            'kubectl': '/usr/local/bin/kubectl',
        }
    }
    
    return paths.get(platform_type, {}).get(tool_name.lower(), '')

def create_install_script(path, selected_tools=None, platform_type=None):
    """Create platform-specific installation script"""
    if platform_type is None:
        platform_type = get_platform()
    
    if selected_tools is None:
        selected_tools = ["Git", "Docker", "kubectl"]
    
    if platform_type == 'windows':
        create_windows_install_script(path, selected_tools)
    elif platform_type == 'macos':
        create_macos_install_script(path, selected_tools)
    elif platform_type == 'linux':
        create_linux_install_script(path, selected_tools)
    else:
        raise ValueError(f"Unsupported platform: {platform_type}")

def create_windows_install_script(path, selected_tools):
    """Create Windows PowerShell installation script"""
    script_content = """# DevOps Tools Installer for Windows
# Run this script as Administrator

Write-Host "DevOps Tools Installer for Windows" -ForegroundColor Cyan
Write-Host "===============================" -ForegroundColor Cyan
"""
    
    # Git installation
    if "Git" in selected_tools:
        script_content += """
# Install Git
Write-Host "`nInstalling Git..." -ForegroundColor Yellow
$gitUrl = "https://github.com/git-for-windows/git/releases/download/v2.40.0.windows.1/Git-2.40.0-64-bit.exe"
$gitInstallerPath = "$env:TEMP\\git-installer.exe"
Invoke-WebRequest -Uri $gitUrl -OutFile $gitInstallerPath -UseBasicParsing
Start-Process -FilePath $gitInstallerPath -Wait
"""
    
    # Docker & WSL2 installation
    if "Docker" in selected_tools:
        script_content += """
# Enable WSL2 features
Write-Host "`nEnabling WSL2 features..." -ForegroundColor Yellow
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

# Download and install WSL2 kernel update
Write-Host "`nDownloading WSL2 Linux kernel update package..." -ForegroundColor Yellow
$wslUpdateUrl = "https://wslstorestorage.blob.core.windows.net/wslblob/wsl_update_x64.msi"
$wslUpdateInstallerPath = "$env:TEMP\\wsl_update_x64.msi"
Invoke-WebRequest -Uri $wslUpdateUrl -OutFile $wslUpdateInstallerPath -UseBasicParsing
Start-Process -FilePath "msiexec.exe" -ArgumentList "/i `"$wslUpdateInstallerPath`" /quiet" -Wait

# Set WSL2 as default
Write-Host "`nSetting WSL2 as default version..." -ForegroundColor Yellow
wsl --set-default-version 2

# Install Docker Desktop
Write-Host "`nInstalling Docker Desktop..." -ForegroundColor Yellow
$dockerUrl = "https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe"
$dockerInstallerPath = "$env:TEMP\\DockerDesktopInstaller.exe"
Invoke-WebRequest -Uri $dockerUrl -OutFile $dockerInstallerPath -UseBasicParsing
Start-Process -FilePath $dockerInstallerPath -Wait
"""
    
    # kubectl installation
    if "kubectl" in selected_tools:
        script_content += """
# Install kubectl
Write-Host "`nInstalling kubectl..." -ForegroundColor Yellow
$version = (Invoke-RestMethod "https://storage.googleapis.com/kubernetes-release/release/stable.txt")
$url = "https://storage.googleapis.com/kubernetes-release/release/$version/bin/windows/amd64/kubectl.exe"
$outputPath = "$env:USERPROFILE\\.kubectl\\kubectl.exe"
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\\.kubectl"
Invoke-WebRequest -Uri $url -OutFile $outputPath -UseBasicParsing
$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($currentPath -notlike "*$env:USERPROFILE\\.kubectl*") {
    [Environment]::SetEnvironmentVariable("Path", $currentPath + ";$env:USERPROFILE\\.kubectl", "User")
}
"""
    
    # Add other tools as needed...
    
    # Completion message
    script_content += """
Write-Host "`nInstallation completed!" -ForegroundColor Green
Write-Host "NOTE: You need to restart your computer for all changes to take effect." -ForegroundColor Yellow
Read-Host "Press Enter to exit"
"""
    
    with open(path, 'w') as f:
        f.write(script_content)

def create_macos_install_script(path, selected_tools):
    """Create macOS bash installation script"""
    script_content = """#!/bin/bash
# DevOps Tools Installer for macOS

echo "DevOps Tools Installer for macOS"
echo "==============================="

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi
"""
    
    # Git installation
    if "Git" in selected_tools:
        script_content += """
# Install Git
echo "Installing Git..."
brew install git
"""
    
    # Docker installation
    if "Docker" in selected_tools:
        script_content += """
# Install Docker
echo "Installing Docker..."
brew install --cask docker
"""
    
    # kubectl installation
    if "kubectl" in selected_tools:
        script_content += """
# Install kubectl
echo "Installing kubectl..."
brew install kubectl
"""
    
    # Add other tools as needed...
    
    # Completion message
    script_content += """
echo "Installation completed!"
echo "Press Enter to exit"
read
"""
    
    with open(path, 'w') as f:
        f.write(script_content)
    
    # Make the script executable
    os.chmod(path, 0o755)

def create_linux_install_script(path, selected_tools):
    """Create Linux bash installation script"""
    script_content = """#!/bin/bash
# DevOps Tools Installer for Linux

echo "DevOps Tools Installer for Linux"
echo "=============================="

# Detect package manager
if command -v apt &> /dev/null; then
    PKG_MANAGER="apt"
    PKG_UPDATE="apt update"
    PKG_INSTALL="apt install -y"
elif command -v dnf &> /dev/null; then
    PKG_MANAGER="dnf"
    PKG_UPDATE="dnf check-update"
    PKG_INSTALL="dnf install -y"
elif command -v yum &> /dev/null; then
    PKG_MANAGER="yum"
    PKG_UPDATE="yum check-update"
    PKG_INSTALL="yum install -y"
else
    echo "Unsupported package manager. Please install tools manually."
    exit 1
fi

# Update package lists
echo "Updating package lists..."
sudo $PKG_UPDATE
"""
    
    # Git installation
    if "Git" in selected_tools:
        script_content += """
# Install Git
echo "Installing Git..."
sudo $PKG_INSTALL git
"""
    
    # Docker installation
    if "Docker" in selected_tools:
        script_content += """
# Install Docker
echo "Installing Docker..."
if [ "$PKG_MANAGER" = "apt" ]; then
    sudo $PKG_INSTALL apt-transport-https ca-certificates curl gnupg lsb-release
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo $PKG_UPDATE
    sudo $PKG_INSTALL docker-ce docker-ce-cli containerd.io
elif [ "$PKG_MANAGER" = "dnf" ] || [ "$PKG_MANAGER" = "yum" ]; then
    sudo $PKG_INSTALL dnf-plugins-core
    sudo dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo
    sudo $PKG_INSTALL docker-ce docker-ce-cli containerd.io
fi
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker $USER
"""
    
    # kubectl installation
    if "kubectl" in selected_tools:
        script_content += """
# Install kubectl
echo "Installing kubectl..."
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
"""
    
    # Add other tools as needed...
    
    # Completion message
    script_content += """
echo "Installation completed!"
echo "NOTE: You may need to log out and log back in for some changes to take effect."
echo "Press Enter to exit"
read
"""
    
    with open(path, 'w') as f:
        f.write(script_content)
    
    # Make the script executable
    os.chmod(path, 0o755)

def run_install_script(script_path, platform_type=None):
    """Run the installation script with appropriate privileges"""
    if platform_type is None:
        platform_type = get_platform()
    
    if platform_type == 'windows':
        # Run PowerShell script with admin privileges
        subprocess.Popen([
            "powershell", 
            "-ExecutionPolicy", "Bypass", 
            "-Command", 
            f"Start-Process powershell -ArgumentList '-ExecutionPolicy Bypass -File \"{script_path}\"' -Verb RunAs"
        ], shell=True)
    elif platform_type == 'macos' or platform_type == 'linux':
        # Run bash script with sudo
        subprocess.Popen([
            "sudo",
            "bash",
            script_path
        ])
    else:
        raise ValueError(f"Unsupported platform: {platform_type}")

def open_file_with_default_app(file_path, platform_type=None):
    """Open a file with the default application"""
    if platform_type is None:
        platform_type = get_platform()
    
    if platform_type == 'windows':
        os.startfile(os.path.abspath(file_path))
    elif platform_type == 'macos':
        subprocess.run(['open', file_path])
    elif platform_type == 'linux':
        subprocess.run(['xdg-open', file_path])
    else:
        raise ValueError(f"Unsupported platform: {platform_type}")