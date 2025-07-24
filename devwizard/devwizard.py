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
import platform
from datetime import datetime
from pathlib import Path

# Import platform utilities
from .platform_utils import get_platform, get_tool_path, create_install_script, run_install_script, open_file_with_default_app

# Import system monitoring
from .system_monitor import monitor_system

# Constants
CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".devwizard", "config.json")

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ASCII Art Logo
LOGO = """
      *    .  *       .             *
   .    *           .    .            
        .     *  🧙‍♂️   .        *     .
     .            *         .           
  *        .  *         .        *      

 ____              __        ___                  _ 
|  _ \  _____   __ \ \      / (_)______ _ _ __ __| | 
| | | |/ _ \ \ / /  \ \ /\ / /| |_  / _` | '__/ _` | 
| |_| |  __/\ V /    \ V  V / | |/ / (_| | | | (_| |
|____/ \___| \_/      \_/\_/  |_/___\__,_|_|  \__,_|

    ⚡ Your Magical DevOps Assistant - v1.0.0 ⚡
      🔮 Cast spells on your infrastructure! 🔮
"""

def load_config():
    """Load configuration from config file"""
    # Ensure config directory exists
    config_dir = os.path.dirname(CONFIG_FILE)
    if not os.path.exists(config_dir):
        os.makedirs(config_dir, exist_ok=True)
        
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
    current_platform = get_platform()
    
    # Platform-specific defaults
    if current_platform == "windows":
        cleanup_dirs = ["%TEMP%", "%USERPROFILE%\\Downloads"]
        git_path = "C:\\Program Files\\Git\\bin\\git.exe"
        docker_path = "C:\\Program Files\\Docker\\Docker\\resources\\bin\\docker.exe"
        kubectl_path = "%USERPROFILE%\\.kubectl\\kubectl.exe"
        terraform_dir = "%USERPROFILE%\\terraform"
        terminal_path = "wt"
    elif current_platform == "macos":
        cleanup_dirs = ["/tmp", "~/Downloads"]
        git_path = "/usr/bin/git"
        docker_path = "/usr/local/bin/docker"
        kubectl_path = "/usr/local/bin/kubectl"
        terraform_dir = "~/terraform"
        terminal_path = "open -a Terminal"
    else:  # linux
        cleanup_dirs = ["/tmp", "~/Downloads"]
        git_path = "/usr/bin/git"
        docker_path = "/usr/bin/docker"
        kubectl_path = "/usr/local/bin/kubectl"
        terraform_dir = "~/terraform"
        terminal_path = "x-terminal-emulator"
    
    config = {
        "workspace": {
            "cleanup_dirs": cleanup_dirs,
            "cleanup_extensions": [".tmp", ".log", ".bak"],
            "min_age_days": 7
        },
        "tools": {
            "git_path": git_path,
            "docker_path": docker_path,
            "kubectl_path": kubectl_path
        },
        "cloud": {
            "aws_region": "us-east-1",
            "aws_profile": "default",
            "terraform_dir": terraform_dir
        },
        "apps": [
            {
                "name": "VS Code", 
                "path": "code",
                "platform_paths": {
                    "windows": "code",
                    "macos": "/Applications/Visual Studio Code.app",
                    "linux": "code"
                }
            },
            {
                "name": "Terminal", 
                "path": terminal_path
            }
        ]
    }
    
    # Ensure config directory exists
    config_dir = os.path.dirname(CONFIG_FILE)
    if not os.path.exists(config_dir):
        os.makedirs(config_dir, exist_ok=True)
    
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
    current_platform = get_platform()
    
    # Define tools to check with their paths or commands
    tools_to_check = {
        "Git": {
            "path": expand_path(tools.get("git_path", get_tool_path("git", current_platform))),
            "command": "git --version"
        },
        "Docker": {
            "path": expand_path(tools.get("docker_path", get_tool_path("docker", current_platform))),
            "command": "docker --version"
        },
        "kubectl": {
            "path": expand_path(tools.get("kubectl_path", get_tool_path("kubectl", current_platform))),
            "command": "kubectl version --client"
        },
        "Terraform": {
            "path": "",
            "command": "terraform --version"
        },
        "AWS CLI": {
            "path": "",
            "command": "aws --version"
        },
        "Azure CLI": {
            "path": "",
            "command": "az --version"
        },
        "Google Cloud SDK": {
            "path": "",
            "command": "gcloud --version"
        },
        "Ansible": {
            "path": "",
            "command": "ansible --version"
        },
        "Jenkins CLI": {
            "path": "",
            "command": "jenkins-cli -v"
        },
        "Helm": {
            "path": "",
            "command": "helm version --short"
        },
        "Vagrant": {
            "path": "",
            "command": "vagrant --version"
        },
        "Packer": {
            "path": "",
            "command": "packer --version"
        },
        "Maven": {
            "path": "",
            "command": "mvn --version"
        },
        "Gradle": {
            "path": "",
            "command": "gradle --version"
        },
        "Node.js": {
            "path": "",
            "command": "node --version"
        },
        "npm": {
            "path": "",
            "command": "npm --version"
        },
        "Python": {
            "path": "",
            "command": "python --version"
        }
    }
    
    # Track which tools are installed
    installed_tools = []
    missing_tools = []
    
    print("\n  Checking core tools:")
    # Check Git, Docker, and kubectl first (core tools)
    for tool_name in ["Git", "Docker", "kubectl"]:
        tool_info = tools_to_check[tool_name]
        tool_path = tool_info["path"]
        tool_cmd = tool_info["command"]
        
        # First check if the path exists
        if tool_path and os.path.exists(tool_path):
            print(f"  {tool_name}: ✅ Installed")
            installed_tools.append(tool_name)
        else:
            # Try running the command
            try:
                result = subprocess.run(tool_cmd, shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"  {tool_name}: ✅ Installed")
                    installed_tools.append(tool_name)
                else:
                    print(f"  {tool_name}: ❌ Not found")
                    missing_tools.append(tool_name)
            except:
                print(f"  {tool_name}: ❌ Not found")
                missing_tools.append(tool_name)
    
    print("\n  Checking additional DevOps tools:")
    # Check other tools
    for tool_name, tool_info in tools_to_check.items():
        if tool_name in ["Git", "Docker", "kubectl"]:
            continue  # Skip core tools already checked
            
        tool_cmd = tool_info["command"]
        
        # Try running the command
        try:
            result = subprocess.run(tool_cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"  {tool_name}: ✅ Installed")
                installed_tools.append(tool_name)
            else:
                print(f"  {tool_name}: ❌ Not found")
                missing_tools.append(tool_name)
        except:
            print(f"  {tool_name}: ❌ Not found")
            missing_tools.append(tool_name)
    
    print(f"\n  Found {len(installed_tools)} of {len(tools_to_check)} tools installed")
    
    # Check if core tools are missing
    core_missing = any(tool in missing_tools for tool in ["Git", "Docker", "kubectl"])
    if core_missing:
        print("\nSome core tools are missing. Would you like to install them?")
        choice = input("Install missing core tools? (y/n): ")
        if choice.lower() == 'y':
            install_tools()
    
    return len(missing_tools) == 0

def install_tools():
    """Install missing DevOps tools"""
    print("🔄 Installing DevOps tools...")
    
    # Define available tools for installation
    available_tools = {
        "1": {"name": "Git", "selected": True},
        "2": {"name": "Docker & WSL2", "selected": True},
        "3": {"name": "kubectl", "selected": True},
        "4": {"name": "Terraform", "selected": False},
        "5": {"name": "AWS CLI", "selected": False},
        "6": {"name": "Azure CLI", "selected": False},
        "7": {"name": "Google Cloud SDK", "selected": False},
        "8": {"name": "Ansible", "selected": False},
        "9": {"name": "Helm", "selected": False},
        "10": {"name": "Node.js & npm", "selected": False},
        "11": {"name": "Python", "selected": False}
    }
    
    # Let user select tools to install
    print("\nSelect tools to install (core tools are selected by default):")
    for key, tool in available_tools.items():
        status = "[X]" if tool["selected"] else "[ ]"
        print(f"  {status} {key}. {tool['name']}")
    
    print("\nEnter tool numbers to toggle selection (e.g., '4 5 7' to select/deselect those tools)")
    print("Or press Enter to continue with current selection")
    
    selection = input("> ").strip()
    if selection:
        for num in selection.split():
            if num in available_tools:
                available_tools[num]["selected"] = not available_tools[num]["selected"]
    
    # Show final selection
    print("\nSelected tools to install:")
    selected_tools = [tool["name"] for tool in available_tools.values() if tool["selected"]]
    for tool in selected_tools:
        print(f"  - {tool}")
    
    confirm = input("\nProceed with installation? (y/n): ").lower()
    if confirm != 'y':
        print("Installation cancelled.")
        return
    
    # Get current platform
    current_platform = get_platform()
    
    # Path to the installation script
    script_ext = ".ps1" if current_platform == "windows" else ".sh"
    config_dir = os.path.join(os.path.expanduser("~"), ".devwizard")
    if not os.path.exists(config_dir):
        os.makedirs(config_dir, exist_ok=True)
    script_path = os.path.join(config_dir, f"install_tools{script_ext}")
    
    # Create the installation script with selected tools
    create_install_script(script_path, selected_tools, current_platform)
    
    # Run the installation script with appropriate privileges
    print(f"  Launching installer for {current_platform}...")
    run_install_script(script_path, current_platform)
    
    print("  Installation started in a new window.")
    input("  Press Enter when installation is complete...")

def launch_apps(config):
    """Launch configured applications"""
    print("🚀 Launching applications...")
    
    current_platform = get_platform()
    apps = config.get("apps", [])
    launched = 0
    
    for app in apps:
        name = app.get("name", "")
        path = app.get("path", "")
        platform_paths = app.get("platform_paths", {})
        
        # Use platform-specific path if available
        if current_platform in platform_paths:
            path = platform_paths[current_platform]
        
        if path:
            try:
                print(f"  Starting {name}...")
                if current_platform == "windows":
                    subprocess.Popen(path, shell=True)
                elif current_platform == "macos":
                    subprocess.Popen(["open", path])
                elif current_platform == "linux":
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

def docker_helper():
    """Docker helper function"""
    print("🚀 Docker Helper")
    print("\n1. List containers")
    print("2. List images")
    print("3. Run container")
    print("4. Stop container")
    print("5. Remove container")
    print("6. Pull image")
    print("7. Docker Compose up")
    print("8. Docker Compose down")
    print("9. Return to main menu")
    
    choice = input("\nEnter your choice (1-9): ")
    
    if choice == "1":
        print("\nListing containers...")
        subprocess.run("docker ps -a", shell=True)
    elif choice == "2":
        print("\nListing images...")
        subprocess.run("docker images", shell=True)
    elif choice == "3":
        image = input("Enter image name: ")
        name = input("Enter container name (or press Enter for random name): ").strip()
        ports = input("Enter port mapping (e.g., 8080:80) or press Enter to skip: ").strip()
        cmd = f"docker run -d"
        if name:
            cmd += f" --name {name}"
        if ports:
            cmd += f" -p {ports}"
        cmd += f" {image}"
        print(f"\nRunning container: {cmd}")
        subprocess.run(cmd, shell=True)
    elif choice == "4":
        container = input("Enter container ID or name: ")
        print(f"\nStopping container {container}...")
        subprocess.run(f"docker stop {container}", shell=True)
    elif choice == "5":
        container = input("Enter container ID or name: ")
        force = input("Force removal? (y/n): ").lower() == 'y'
        cmd = f"docker rm {container}"
        if force:
            cmd += " -f"
        print(f"\nRemoving container {container}...")
        subprocess.run(cmd, shell=True)
    elif choice == "6":
        image = input("Enter image name: ")
        print(f"\nPulling image {image}...")
        subprocess.run(f"docker pull {image}", shell=True)
    elif choice == "7":
        path = input("Enter docker-compose.yml directory (or press Enter for current directory): ").strip() or "."
        print(f"\nRunning docker-compose up in {path}...")
        subprocess.run(f"cd {path} && docker-compose up -d", shell=True)
    elif choice == "8":
        path = input("Enter docker-compose.yml directory (or press Enter for current directory): ").strip() or "."
        print(f"\nRunning docker-compose down in {path}...")
        subprocess.run(f"cd {path} && docker-compose down", shell=True)
    elif choice == "9":
        return
    else:
        print("Invalid choice.")

def kubernetes_helper():
    """Kubernetes helper function"""
    print("☸️ Kubernetes Helper")
    print("\n1. Get pods")
    print("2. Get services")
    print("3. Get deployments")
    print("4. Describe resource")
    print("5. Apply YAML file")
    print("6. Delete resource")
    print("7. Get logs")
    print("8. Switch context")
    print("9. Return to main menu")
    
    choice = input("\nEnter your choice (1-9): ")
    
    if choice == "1":
        namespace = input("Enter namespace (or press Enter for all namespaces): ").strip()
        cmd = "kubectl get pods"
        if namespace:
            cmd += f" -n {namespace}"
        else:
            cmd += " --all-namespaces"
        print("\nGetting pods...")
        subprocess.run(cmd, shell=True)
    elif choice == "2":
        namespace = input("Enter namespace (or press Enter for all namespaces): ").strip()
        cmd = "kubectl get services"
        if namespace:
            cmd += f" -n {namespace}"
        else:
            cmd += " --all-namespaces"
        print("\nGetting services...")
        subprocess.run(cmd, shell=True)
    elif choice == "3":
        namespace = input("Enter namespace (or press Enter for all namespaces): ").strip()
        cmd = "kubectl get deployments"
        if namespace:
            cmd += f" -n {namespace}"
        else:
            cmd += " --all-namespaces"
        print("\nGetting deployments...")
        subprocess.run(cmd, shell=True)
    elif choice == "4":
        resource_type = input("Enter resource type (pod, service, deployment, etc.): ")
        resource_name = input("Enter resource name: ")
        namespace = input("Enter namespace: ")
        print(f"\nDescribing {resource_type} {resource_name} in namespace {namespace}...")
        subprocess.run(f"kubectl describe {resource_type} {resource_name} -n {namespace}", shell=True)
    elif choice == "5":
        yaml_file = input("Enter path to YAML file: ")
        print(f"\nApplying {yaml_file}...")
        subprocess.run(f"kubectl apply -f {yaml_file}", shell=True)
    elif choice == "6":
        resource_type = input("Enter resource type (pod, service, deployment, etc.): ")
        resource_name = input("Enter resource name: ")
        namespace = input("Enter namespace: ")
        print(f"\nDeleting {resource_type} {resource_name} in namespace {namespace}...")
        subprocess.run(f"kubectl delete {resource_type} {resource_name} -n {namespace}", shell=True)
    elif choice == "7":
        pod_name = input("Enter pod name: ")
        namespace = input("Enter namespace: ")
        print(f"\nGetting logs for pod {pod_name} in namespace {namespace}...")
        subprocess.run(f"kubectl logs {pod_name} -n {namespace}", shell=True)
    elif choice == "8":
        print("\nAvailable contexts:")
        subprocess.run("kubectl config get-contexts", shell=True)
        context = input("\nEnter context name to switch to: ")
        print(f"\nSwitching to context {context}...")
        subprocess.run(f"kubectl config use-context {context}", shell=True)
    elif choice == "9":
        return
    else:
        print("Invalid choice.")

def aws_helper():
    """AWS helper function"""
    print("☁️ AWS Helper")
    print("\n1. List EC2 instances")
    print("2. List S3 buckets")
    print("3. List Lambda functions")
    print("4. Describe EC2 instance")
    print("5. Start EC2 instance")
    print("6. Stop EC2 instance")
    print("7. Switch AWS profile")
    print("8. Check AWS service status")
    print("9. Return to main menu")
    
    choice = input("\nEnter your choice (1-9): ")
    
    if choice == "1":
        print("\nListing EC2 instances...")
        subprocess.run("aws ec2 describe-instances --query 'Reservations[*].Instances[*].[InstanceId,State.Name,InstanceType,PublicIpAddress]' --output table", shell=True)
    elif choice == "2":
        print("\nListing S3 buckets...")
        subprocess.run("aws s3 ls", shell=True)
    elif choice == "3":
        print("\nListing Lambda functions...")
        subprocess.run("aws lambda list-functions --query 'Functions[*].[FunctionName,Runtime,Timeout,MemorySize]' --output table", shell=True)
    elif choice == "4":
        instance_id = input("Enter EC2 instance ID: ")
        print(f"\nDescribing EC2 instance {instance_id}...")
        subprocess.run(f"aws ec2 describe-instances --instance-ids {instance_id}", shell=True)
    elif choice == "5":
        instance_id = input("Enter EC2 instance ID: ")
        print(f"\nStarting EC2 instance {instance_id}...")
        subprocess.run(f"aws ec2 start-instances --instance-ids {instance_id}", shell=True)
    elif choice == "6":
        instance_id = input("Enter EC2 instance ID: ")
        print(f"\nStopping EC2 instance {instance_id}...")
        subprocess.run(f"aws ec2 stop-instances --instance-ids {instance_id}", shell=True)
    elif choice == "7":
        print("\nAvailable AWS profiles:")
        subprocess.run("aws configure list-profiles", shell=True)
        profile = input("\nEnter profile name to switch to: ")
        print(f"\nSwitching to profile {profile}...")
        os.environ["AWS_PROFILE"] = profile
        print(f"AWS_PROFILE environment variable set to {profile}")
        print("Note: This only affects the current session")
    elif choice == "8":
        print("\nChecking AWS service status...")
        subprocess.run("aws health describe-events --filter eventTypeCategories=issue --region us-east-1", shell=True)
    elif choice == "9":
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
        if get_platform() == "windows":
            os.system(f"notepad {config_path}")
        elif get_platform() == "macos":
            os.system(f"open -e {config_path}")
        else:
            os.system(f"xdg-open {config_path}")
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
            print("7. Docker Helper")
            print("8. Kubernetes Helper")
            print("9. AWS Helper")
            print("10. Edit configuration")
            print("11. Exit")
            
            choice = input("\nEnter your choice (1-11): ")
            
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
                docker_helper()
            elif choice == "8":
                kubernetes_helper()
            elif choice == "9":
                aws_helper()
            elif choice == "10":
                config_path = os.path.abspath(CONFIG_FILE)
                print(f"Opening configuration file: {config_path}")
                if get_platform() == "windows":
                    os.system(f"notepad {config_path}")
                elif get_platform() == "macos":
                    os.system(f"open -e {config_path}")
                else:
                    os.system(f"xdg-open {config_path}")
            elif choice == "11":
                print("\nThank you for using DevWizard! ✨")
                break
            else:
                print("Invalid choice. Please try again.")
            
            input("\nPress Enter to continue...")