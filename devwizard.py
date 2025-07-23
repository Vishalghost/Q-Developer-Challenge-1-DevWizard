#!/usr/bin/env python
"""
DevWizard - A magical CLI for cloud and DevOps engineers
"""
import os
import sys
import json
import shutil
import argparse
import subprocess
import logging
from datetime import datetime
from pathlib import Path

# Constants
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "devwizard_config.json")

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ASCII Art Logo
LOGO = """
 _____              _    _ _                       _ 
|  __ \\            | |  | (_)                     | |
| |  | | _____   __| |  | |_ ______ _ _ __ __ _  | |
| |  | |/ _ \\ \\ / /| |/\\| | |_  / _` | '__/ _` | | |
| |__| |  __/\\ V / \\  /\\  / |/ / (_| | | | (_| | |_|
|_____/ \\___| \\_/   \\/  \\/|_/___\\__,_|_|  \\__,_| (_)
                                                   
        Your Magical DevOps Assistant - v1.0.0
"""

def load_config():
    """Load configuration from config file"""
    if not os.path.exists(CONFIG_FILE):
        return create_default_config()
    
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        return create_default_config()

def create_default_config():
    """Create default configuration"""
    config = {
        "workspace": {
            "cleanup_dirs": [
                "%TEMP%",
                "%USERPROFILE%\\Downloads"
            ],
            "cleanup_extensions": [".tmp", ".log", ".bak"],
            "min_age_days": 7
        },
        "tools": {
            "git_path": "C:\\Program Files\\Git\\bin\\git.exe",
            "docker_path": "C:\\Program Files\\Docker\\Docker\\resources\\bin\\docker.exe",
            "kubectl_path": "%USERPROFILE%\\.kubectl\\kubectl.exe"
        },
        "cloud": {
            "aws_region": "us-east-1",
            "aws_profile": "default",
            "terraform_dir": "%USERPROFILE%\\terraform"
        },
        "apps": [
            {"name": "VS Code", "path": "code"},
            {"name": "Terminal", "path": "wt"}
        ]
    }
    
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)
    
    return config

def expand_path(path):
    """Expand environment variables in path"""
    return os.path.expandvars(path)

def clean_workspace(config):
    """Clean temporary files"""
    print("🧹 Cleaning workspace...")
    
    workspace = config.get("workspace", {})
    dirs = workspace.get("cleanup_dirs", [])
    extensions = workspace.get("cleanup_extensions", [])
    min_age_days = workspace.get("min_age_days", 7)
    
    # Calculate cutoff date
    cutoff_time = datetime.now().timestamp() - (min_age_days * 24 * 60 * 60)
    
    total_cleaned = 0
    files_removed = 0
    
    for directory in dirs:
        dir_path = expand_path(directory)
        if not os.path.exists(dir_path):
            print(f"  Directory not found: {dir_path}")
            continue
            
        print(f"  Cleaning {dir_path}...")
        
        for root, _, files in os.walk(dir_path):
            for file in files:
                file_path = os.path.join(root, file)
                
                # Check if file matches extension criteria
                if any(file.endswith(ext) for ext in extensions) or not extensions:
                    try:
                        # Check file age
                        file_time = os.path.getmtime(file_path)
                        if file_time < cutoff_time:
                            file_size = os.path.getsize(file_path)
                            os.remove(file_path)
                            total_cleaned += file_size
                            files_removed += 1
                    except Exception:
                        # Skip files that can't be accessed
                        pass
    
    mb_cleaned = total_cleaned / (1024*1024)
    print(f"  Removed {files_removed} files ({mb_cleaned:.2f} MB)")
    return files_removed

def check_tools(config):
    """Check if DevOps tools are installed and in PATH"""
    print("🔧 Checking DevOps tools...")
    
    tools = config.get("tools", {})
    git_path = expand_path(tools.get("git_path", ""))
    docker_path = expand_path(tools.get("docker_path", ""))
    kubectl_path = expand_path(tools.get("kubectl_path", ""))
    
    # Check Git
    git_ok = os.path.exists(git_path)
    print(f"  Git: {'✅ Installed' if git_ok else '❌ Not found'}")
    
    # Check Docker
    docker_ok = os.path.exists(docker_path)
    print(f"  Docker: {'✅ Installed' if docker_ok else '❌ Not found'}")
    
    # Check kubectl
    kubectl_ok = os.path.exists(kubectl_path)
    print(f"  kubectl: {'✅ Installed' if kubectl_ok else '❌ Not found'}")
    
    if not (git_ok and docker_ok and kubectl_ok):
        print("\nSome tools are missing. Would you like to install them?")
        choice = input("Install missing tools? (y/n): ")
        if choice.lower() == 'y':
            install_tools()
    
    return git_ok and docker_ok and kubectl_ok

def install_tools():
    """Install missing DevOps tools"""
    print("🔄 Installing DevOps tools...")
    
    # Path to the installation script
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "install_tools.ps1")
    
    # Check if the script exists
    if not os.path.exists(script_path):
        print("  Installation script not found. Creating it...")
        create_install_script(script_path)
    
    # Run the installation script with admin privileges
    print("  Launching installer with admin privileges...")
    subprocess.Popen([
        "powershell", 
        "-ExecutionPolicy", "Bypass", 
        "-Command", 
        f"Start-Process powershell -ArgumentList '-ExecutionPolicy Bypass -File \"{script_path}\"' -Verb RunAs"
    ], shell=True)
    
    print("  Installation started in a new window.")
    input("  Press Enter when installation is complete...")

def create_install_script(path):
    """Create the PowerShell installation script"""
    with open(path, 'w') as f:
        f.write("""# DevOps Tools Installer
# Run this script as Administrator

Write-Host "DevOps Tools Installer" -ForegroundColor Cyan
Write-Host "====================" -ForegroundColor Cyan

# Install Git
Write-Host "`nInstalling Git..." -ForegroundColor Yellow
$gitUrl = "https://github.com/git-for-windows/git/releases/download/v2.40.0.windows.1/Git-2.40.0-64-bit.exe"
$gitInstallerPath = "$env:TEMP\\git-installer.exe"
Invoke-WebRequest -Uri $gitUrl -OutFile $gitInstallerPath -UseBasicParsing
Start-Process -FilePath $gitInstallerPath -Wait

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

Write-Host "`nInstallation completed!" -ForegroundColor Green
Write-Host "NOTE: You need to restart your computer for all changes to take effect." -ForegroundColor Yellow
Read-Host "Press Enter to exit"
""")

def monitor_system():
    """Monitor system resources"""
    print("📊 System Monitor")
    
    # Simple CPU usage
    try:
        ps_cmd = "powershell -Command ""Get-Counter '\\Processor(_Total)\\% Processor Time' | Select-Object -ExpandProperty CounterSamples | Select-Object -ExpandProperty CookedValue"""
        cpu_result = subprocess.run(ps_cmd, capture_output=True, text=True, shell=True)
        cpu_usage = float(cpu_result.stdout.strip())
        print(f"  CPU Usage: {cpu_usage:.1f}%")
    except:
        print("  CPU Usage: Unable to retrieve")
    
    # Simple memory usage
    try:
        ps_cmd = "powershell -Command ""$CompObject = Get-WmiObject -Class WIN32_OperatingSystem; "
        ps_cmd += "$TotalMemory = [math]::round($CompObject.TotalVisibleMemorySize / 1024, 0); "
        ps_cmd += "$FreeMemory = [math]::round($CompObject.FreePhysicalMemory / 1024, 0); "
        ps_cmd += "$UsedMemory = $TotalMemory - $FreeMemory; "
        ps_cmd += "$MemoryUsage = [math]::round(($UsedMemory / $TotalMemory) * 100, 2); "
        ps_cmd += "Write-Output \"$MemoryUsage,$UsedMemory,$TotalMemory\""""
        
        mem_result = subprocess.run(ps_cmd, capture_output=True, text=True, shell=True)
        mem_values = mem_result.stdout.strip().split(',')
        
        mem_percent = float(mem_values[0])
        used_mem = float(mem_values[1])
        total_mem = float(mem_values[2])
        print(f"  Memory Usage: {mem_percent:.1f}% ({used_mem:.0f} MB / {total_mem:.0f} MB)")
    except:
        print("  Memory Usage: Unable to retrieve")
    
    # Simple disk usage
    try:
        ps_cmd = "powershell -Command ""Get-PSDrive -PSProvider FileSystem | ForEach-Object {$_.Name + ',' + [math]::Round(($_.Used/($_.Used+$_.Free))*100,1) + ',' + [math]::Round($_.Used/1GB,1) + ',' + [math]::Round(($_.Used+$_.Free)/1GB,1)}"""
        disk_result = subprocess.run(ps_cmd, capture_output=True, text=True, shell=True)
        disk_lines = disk_result.stdout.strip().split('\n')
        
        print("  Disk Usage:")
        for line in disk_lines:
            parts = line.split(',')
            if len(parts) == 4:
                drive = parts[0] + ":"
                usage_percent = float(parts[1])
                used_space = float(parts[2])
                total_space = float(parts[3])
                print(f"    {drive}: {usage_percent:.1f}% used ({used_space:.1f} GB / {total_space:.1f} GB)")
    except:
        print("  Disk Usage: Unable to retrieve")
    
    # Simple process count
    try:
        ps_cmd = "powershell -Command ""(Get-Process).Count"""
        process_count = subprocess.run(ps_cmd, capture_output=True, text=True, shell=True).stdout.strip()
        print(f"  Processes: {process_count} running")
    except:
        print("  Processes: Unable to retrieve")


def launch_apps(config):
    """Launch configured applications"""
    print("🚀 Launching applications...")
    
    apps = config.get("apps", [])
    launched = 0
    
    for app in apps:
        name = app.get("name", "")
        path = app.get("path", "")
        
        if path:
            try:
                print(f"  Starting {name}...")
                subprocess.Popen(path, shell=True)
                launched += 1
            except Exception as e:
                print(f"  Error launching {name}: {e}")
    
    print(f"  Launched {launched} applications")
    return launched

def git_helper():
    """Git helper function"""
    print("🔄 Git Helper")
    print("\n1. Initialize repository")
    print("2. Clone repository")
    print("3. Check status")
    print("4. Add files")
    print("5. Commit changes")
    print("6. Push changes")
    print("7. Pull changes")
    print("8. Return to main menu")
    
    choice = input("\nEnter your choice (1-8): ")
    
    if choice == "1":
        path = input("Enter directory path (or press Enter for current directory): ").strip() or "."
        cmd = f"git -C {path} init"
        subprocess.run(cmd, shell=True)
    elif choice == "2":
        repo_url = input("Enter repository URL: ")
        path = input("Enter target directory (or press Enter for default): ").strip()
        cmd = f"git clone {repo_url}" + (f" {path}" if path else "")
        subprocess.run(cmd, shell=True)
    elif choice == "3":
        path = input("Enter repository path (or press Enter for current directory): ").strip() or "."
        cmd = f"git -C {path} status"
        subprocess.run(cmd, shell=True)
    elif choice == "4":
        path = input("Enter repository path (or press Enter for current directory): ").strip() or "."
        files = input("Enter files to add (or . for all): ").strip() or "."
        cmd = f"git -C {path} add {files}"
        subprocess.run(cmd, shell=True)
    elif choice == "5":
        path = input("Enter repository path (or press Enter for current directory): ").strip() or "."
        message = input("Enter commit message: ")
        cmd = f"git -C {path} commit -m \"{message}\""
        subprocess.run(cmd, shell=True)
    elif choice == "6":
        path = input("Enter repository path (or press Enter for current directory): ").strip() or "."
        remote = input("Enter remote name (or press Enter for origin): ").strip() or "origin"
        branch = input("Enter branch name (or press Enter for main): ").strip() or "main"
        cmd = f"git -C {path} push {remote} {branch}"
        subprocess.run(cmd, shell=True)
    elif choice == "7":
        path = input("Enter repository path (or press Enter for current directory): ").strip() or "."
        remote = input("Enter remote name (or press Enter for origin): ").strip() or "origin"
        branch = input("Enter branch name (or press Enter for main): ").strip() or "main"
        cmd = f"git -C {path} pull {remote} {branch}"
        subprocess.run(cmd, shell=True)
    elif choice == "8":
        return
    else:
        print("Invalid choice.")

def main():
    print(LOGO)
    
    parser = argparse.ArgumentParser(description="DevWizard - A magical CLI for cloud and DevOps engineers")
    parser.add_argument("--clean", action="store_true", help="Clean workspace")
    parser.add_argument("--check", action="store_true", help="Check DevOps tools")
    parser.add_argument("--monitor", action="store_true", help="Monitor system resources")
    parser.add_argument("--launch", action="store_true", help="Launch applications")
    parser.add_argument("--install", action="store_true", help="Install DevOps tools")
    parser.add_argument("--config", action="store_true", help="Edit configuration")
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config()
    
    # If no arguments provided, show interactive menu
    run_menu = not (args.clean or args.check or args.monitor or args.launch or 
                    args.install or args.config)
    
    # Edit configuration if requested
    if args.config:
        config_path = os.path.abspath(CONFIG_FILE)
        print(f"Opening configuration file: {config_path}")
        os.system(f"notepad {config_path}")
        return
    
    # Run specific actions if requested
    if args.clean:
        clean_workspace(config)
    
    if args.check:
        check_tools(config)
    
    if args.monitor:
        monitor_system()
    
    if args.launch:
        launch_apps(config)
    
    if args.install:
        install_tools()
    
    # Interactive menu
    if run_menu:
        while True:
            print("\n" + "=" * 60)
            print("DevWizard - Your Magical DevOps Assistant")
            print("=" * 60)
            print("1. Clean workspace")
            print("2. Check DevOps tools")
            print("3. Monitor system resources")
            print("4. Launch applications")
            print("5. Install DevOps tools")
            print("6. Git Helper")
            print("7. Edit configuration")
            print("8. Exit")
            
            choice = input("\nEnter your choice (1-8): ")
            
            if choice == "1":
                clean_workspace(config)
            elif choice == "2":
                check_tools(config)
            elif choice == "3":
                monitor_system()
            elif choice == "4":
                launch_apps(config)
            elif choice == "5":
                install_tools()
            elif choice == "6":
                git_helper()
            elif choice == "7":
                config_path = os.path.abspath(CONFIG_FILE)
                print(f"Opening configuration file: {config_path}")
                os.system(f"notepad {config_path}")
            elif choice == "8":
                print("\nThank you for using DevWizard! ✨")
                break
            else:
                print("Invalid choice. Please try again.")
            
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()