#!/usr/bin/env python
"""
Dev Assistant - A CLI automation tool for cloud and DevOps engineers
"""
import os
import sys
import json
import shutil
import argparse
import subprocess
import logging
import re
import configparser
import time
import socket
from datetime import datetime
from pathlib import Path

# Try to import AWS SDK
try:
    import boto3
    import botocore
    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

def load_config():
    """Load configuration from config.json file"""
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
        "cleanup": {
            "temp_directories": [
                "%TEMP%",
                "%USERPROFILE%\\Downloads"
            ],
            "file_extensions_to_clean": [".tmp", ".log", ".bak"],
            "min_age_days": 7,
            "exclude_patterns": ["important", "keep"]
        },
        "organize": {
            "target_directory": "%USERPROFILE%\\Desktop",
            "rules": [
                {"extensions": [".pdf", ".doc", ".docx", ".txt"], "folder": "Documents"},
                {"extensions": [".jpg", ".png", ".gif", ".jpeg"], "folder": "Images"},
                {"extensions": [".mp3", ".wav"], "folder": "Audio"},
                {"extensions": [".mp4", ".avi", ".mov"], "folder": "Videos"},
                {"extensions": [".zip", ".rar", ".7z"], "folder": "Archives"},
                {"extensions": [".exe", ".msi"], "folder": "Installers"}
            ]
        },
        "applications": [
            {"name": "VS Code", "path": "code"},
            {"name": "Chrome", "path": "start chrome"},
            {"name": "Windows Terminal", "path": "wt"}
        ],
        "aws": {
            "default_region": "us-east-1",
            "credentials_path": "%USERPROFILE%\\.aws\\credentials",
            "config_path": "%USERPROFILE%\\.aws\\config",
            "terraform_path": "%USERPROFILE%\\terraform",
            "cloudformation_path": "%USERPROFILE%\\cloudformation",
            "monitor_services": ["ec2", "s3", "lambda", "rds"],
            "cost_alert_threshold": 100
        },
        "devops": {
            "docker_compose_files": ["%USERPROFILE%\\docker-compose.yml"],
            "git_repos": ["%USERPROFILE%\\projects"],
            "terraform_files": ["%USERPROFILE%\\terraform"],
            "kubernetes_config": "%USERPROFILE%\\.kube\\config"
        }
    }
    
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)
    
    print(f"Created default configuration at {CONFIG_FILE}")
    return config

def expand_path(path):
    """Expand environment variables in path"""
    return os.path.expandvars(path)

def clean_disk_space(config):
    """Clean temporary files based on configuration"""
    print("Cleaning disk space...")
    logging.info("Starting disk cleanup")
    
    cleanup_config = config.get("cleanup", {})
    temp_dirs = cleanup_config.get("temp_directories", [])
    extensions = cleanup_config.get("file_extensions_to_clean", [])
    min_age_days = cleanup_config.get("min_age_days", 7)
    exclude_patterns = cleanup_config.get("exclude_patterns", [])
    
    # Calculate cutoff date
    cutoff_time = datetime.now().timestamp() - (min_age_days * 24 * 60 * 60)
    
    total_cleaned = 0
    files_removed = 0
    
    for directory in temp_dirs:
        dir_path = expand_path(directory)
        if not os.path.exists(dir_path):
            logging.warning(f"Directory not found: {dir_path}")
            print(f"  Directory not found: {dir_path}")
            continue
            
        print(f"  Cleaning {dir_path}...")
        
        for root, _, files in os.walk(dir_path):
            for file in files:
                file_path = os.path.join(root, file)
                
                # Skip files matching exclude patterns
                if any(pattern.lower() in file.lower() for pattern in exclude_patterns):
                    continue
                
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
                            logging.debug(f"Removed: {file_path} ({file_size / 1024:.1f} KB)")
                    except PermissionError:
                        logging.debug(f"Permission denied: {file_path}")
                    except Exception as e:
                        # Skip files that can't be accessed
                        logging.debug(f"Error processing {file_path}: {e}")
    
    mb_cleaned = total_cleaned / (1024*1024)
    print(f"  Removed {files_removed} files ({mb_cleaned:.2f} MB)")
    logging.info(f"Disk cleanup complete: {files_removed} files removed ({mb_cleaned:.2f} MB)")
    return total_cleaned

def organize_files(config):
    """Organize files based on configuration rules"""
    print("Organizing files...")
    logging.info("Starting file organization")
    
    organize_config = config.get("organize", {})
    target_dir = expand_path(organize_config.get("target_directory", ""))
    rules = organize_config.get("rules", [])
    
    if not target_dir or not os.path.exists(target_dir):
        logging.warning(f"Target directory not found: {target_dir}")
        print(f"  Target directory not found: {target_dir}")
        return 0
    
    files_organized = 0
    
    for item in os.listdir(target_dir):
        item_path = os.path.join(target_dir, item)
        
        # Skip directories and non-files
        if not os.path.isfile(item_path):
            continue
        
        # Find matching rule
        moved = False
        for rule in rules:
            extensions = rule.get("extensions", [])
            folder = rule.get("folder", "")
            
            if any(item.lower().endswith(ext.lower()) for ext in extensions):
                # Determine destination folder
                dest_folder = os.path.join(target_dir, folder)
                

                
                # Create destination folder if it doesn't exist
                if not os.path.exists(dest_folder):
                    os.makedirs(dest_folder)
                
                # Move the file
                dest_path = os.path.join(dest_folder, item)
                try:
                    shutil.move(item_path, dest_path)
                    files_organized += 1
                    moved = True
                    print(f"  Moved: {item} → {os.path.relpath(dest_folder, target_dir)}/")
                    logging.info(f"Organized file: {item} → {os.path.relpath(dest_folder, target_dir)}/")
                except Exception as e:
                    print(f"  Error moving {item}: {e}")
                    logging.error(f"Error moving {item}: {e}")
                
                break
    
    print(f"  Organized {files_organized} files")
    logging.info(f"File organization complete: {files_organized} files organized")
    return files_organized

def launch_applications(config):
    """Launch configured applications"""
    print("Launching applications...")
    logging.info("Starting application launcher")
    
    apps = config.get("applications", [])
    launched = 0
    
    for app in apps:
        name = app.get("name", "")
        path = app.get("path", "")
        
        if path:
            try:
                print(f"  Starting {name}...")
                subprocess.Popen(path, shell=True)
                launched += 1
                logging.info(f"Launched application: {name}")
            except Exception as e:
                print(f"  Error launching {name}: {e}")
                logging.error(f"Error launching {name}: {e}")
    
    print(f"  Launched {launched} applications")
    logging.info(f"Application launcher complete: {launched} applications started")
    return launched


def manage_aws_resources(config):
    """Manage AWS resources and provide status information"""
    if not AWS_AVAILABLE:
        print("AWS SDK (boto3) not installed. Run: pip install boto3")
        return False
    
    print("AWS Resource Manager")
    print("=" * 50)
    
    aws_config = config.get("aws", {})
    default_region = aws_config.get("default_region", "us-east-1")
    
    # Get current AWS profile
    session = boto3.Session()
    current_profile = session.profile_name
    current_region = session.region_name or default_region
    
    print(f"Current profile: {current_profile or 'default'} | Region: {current_region}")
    print("-" * 50)
    
    # Show menu
    print("Select an option:")
    print("1. List EC2 instances")
    print("2. List S3 buckets")
    print("3. Check service health")
    print("4. Deploy CloudFormation stack")
    print("5. Run Terraform plan")
    print("6. Estimate AWS costs")
    print("7. Switch AWS profile")
    print("8. Return to main menu")
    
    choice = input("Enter your choice (1-8): ")
    
    try:
        if choice == "1":
            # List EC2 instances
            ec2 = boto3.resource('ec2', region_name=current_region)
            instances = list(ec2.instances.all())
            
            if not instances:
                print("No EC2 instances found in this region.")
            else:
                print(f"\nFound {len(instances)} EC2 instances:")
                print("{:<20} {:<15} {:<15} {:<15}".format("Instance ID", "State", "Type", "Public IP"))
                print("-" * 70)
                
                for instance in instances:
                    print("{:<20} {:<15} {:<15} {:<15}".format(
                        instance.id,
                        instance.state['Name'],
                        instance.instance_type,
                        instance.public_ip_address or 'None'
                    ))
        
        elif choice == "2":
            # List S3 buckets
            s3 = boto3.client('s3', region_name=current_region)
            response = s3.list_buckets()
            buckets = response['Buckets']
            
            if not buckets:
                print("No S3 buckets found.")
            else:
                print(f"\nFound {len(buckets)} S3 buckets:")
                print("{:<30} {:<20}".format("Bucket Name", "Creation Date"))
                print("-" * 50)
                
                for bucket in buckets:
                    print("{:<30} {:<20}".format(
                        bucket['Name'],
                        bucket['CreationDate'].strftime('%Y-%m-%d')
                    ))
        
        elif choice == "3":
            # Check service health
            services_to_check = aws_config.get("monitor_services", ["ec2", "s3", "lambda", "rds"])
            
            print("\nChecking AWS service health...")
            print("{:<15} {:<10}".format("Service", "Status"))
            print("-" * 25)
            
            for service in services_to_check:
                try:
                    # Try to create a client for the service
                    client = boto3.client(service, region_name=current_region)
                    # If we can list something, the service is working
                    if service == 'ec2':
                        client.describe_instances(MaxResults=5)
                    elif service == 's3':
                        client.list_buckets()
                    elif service == 'lambda':
                        client.list_functions(MaxItems=1)
                    elif service == 'rds':
                        client.describe_db_instances(MaxRecords=5)
                    else:
                        # Generic approach for other services
                        pass
                    
                    print("{:<15} {:<10}".format(service.upper(), "OK"))
                except botocore.exceptions.ClientError as e:
                    print("{:<15} {:<10}".format(service.upper(), "ERROR"))
                    print(f"  {str(e)}")
                except Exception as e:
                    print("{:<15} {:<10}".format(service.upper(), "UNKNOWN"))
                    print(f"  {str(e)}")
        
        elif choice == "4":
            # Deploy CloudFormation stack
            cf_path = expand_path(aws_config.get("cloudformation_path", "%USERPROFILE%\\cloudformation"))
            
            if not os.path.exists(cf_path):
                print(f"CloudFormation directory not found: {cf_path}")
                return
            
            # List available templates
            templates = [f for f in os.listdir(cf_path) if f.endswith('.yaml') or f.endswith('.json')]
            
            if not templates:
                print("No CloudFormation templates found.")
                return
            
            print("\nAvailable CloudFormation templates:")
            for i, template in enumerate(templates):
                print(f"{i+1}. {template}")
            
            template_idx = int(input("\nSelect template number: ")) - 1
            if template_idx < 0 or template_idx >= len(templates):
                print("Invalid selection.")
                return
            
            template_path = os.path.join(cf_path, templates[template_idx])
            stack_name = input("Enter stack name: ")
            
            if not stack_name:
                print("Stack name cannot be empty.")
                return
            
            # Deploy the stack
            cf = boto3.client('cloudformation', region_name=current_region)
            
            with open(template_path, 'r') as f:
                template_body = f.read()
            
            print(f"\nDeploying stack '{stack_name}'...")
            try:
                response = cf.create_stack(
                    StackName=stack_name,
                    TemplateBody=template_body,
                    Capabilities=['CAPABILITY_IAM', 'CAPABILITY_NAMED_IAM']
                )
                print(f"Stack creation initiated. Stack ID: {response['StackId']}")
            except Exception as e:
                print(f"Error deploying stack: {e}")
        
        elif choice == "5":
            # Run Terraform plan
            tf_path = expand_path(aws_config.get("terraform_path", "%USERPROFILE%\\terraform"))
            
            if not os.path.exists(tf_path):
                print(f"Terraform directory not found: {tf_path}")
                return
            
            # List available Terraform directories
            tf_dirs = [d for d in os.listdir(tf_path) if os.path.isdir(os.path.join(tf_path, d))]
            
            if not tf_dirs:
                print("No Terraform directories found.")
                return
            
            print("\nAvailable Terraform projects:")
            for i, tf_dir in enumerate(tf_dirs):
                print(f"{i+1}. {tf_dir}")
            
            dir_idx = int(input("\nSelect project number: ")) - 1
            if dir_idx < 0 or dir_idx >= len(tf_dirs):
                print("Invalid selection.")
                return
            
            project_dir = os.path.join(tf_path, tf_dirs[dir_idx])
            
            # Run Terraform commands
            print(f"\nRunning Terraform in {project_dir}...")
            
            # Initialize Terraform
            print("\nInitializing Terraform...")
            subprocess.run(["terraform", "init"], cwd=project_dir, shell=True)
            
            # Run Terraform plan
            print("\nRunning Terraform plan...")
            subprocess.run(["terraform", "plan"], cwd=project_dir, shell=True)
            
            # Ask if user wants to apply
            apply = input("\nDo you want to apply this plan? (y/n): ").lower()
            if apply == 'y':
                print("\nApplying Terraform plan...")
                subprocess.run(["terraform", "apply", "-auto-approve"], cwd=project_dir, shell=True)
                print("Terraform apply completed.")
        
        elif choice == "6":
            # Estimate AWS costs
            print("\nFetching AWS cost data...")
            
            try:
                ce = boto3.client('ce', region_name=current_region)
                
                # Get cost for current month
                start_date = datetime.now().replace(day=1).strftime('%Y-%m-%d')
                end_date = datetime.now().strftime('%Y-%m-%d')
                
                response = ce.get_cost_and_usage(
                    TimePeriod={
                        'Start': start_date,
                        'End': end_date
                    },
                    Granularity='MONTHLY',
                    Metrics=['UnblendedCost']
                )
                
                if response['ResultsByTime']:
                    cost = float(response['ResultsByTime'][0]['Total']['UnblendedCost']['Amount'])
                    currency = response['ResultsByTime'][0]['Total']['UnblendedCost']['Unit']
                    
                    print(f"\nCurrent month costs: {cost:.2f} {currency}")
                    
                    # Check against threshold
                    threshold = aws_config.get("cost_alert_threshold", 100)
                    if cost > threshold:
                        print(f"WARNING: Current costs exceed threshold of {threshold} {currency}!")
                else:
                    print("No cost data available.")
                    
                # Get cost by service
                response = ce.get_cost_and_usage(
                    TimePeriod={
                        'Start': start_date,
                        'End': end_date
                    },
                    Granularity='MONTHLY',
                    Metrics=['UnblendedCost'],
                    GroupBy=[{
                        'Type': 'DIMENSION',
                        'Key': 'SERVICE'
                    }]
                )
                
                if response['ResultsByTime'] and response['ResultsByTime'][0]['Groups']:
                    print("\nCosts by service:")
                    print("{:<30} {:<15}".format("Service", "Cost"))
                    print("-" * 45)
                    
                    for group in response['ResultsByTime'][0]['Groups']:
                        service = group['Keys'][0]
                        amount = float(group['Metrics']['UnblendedCost']['Amount'])
                        
                        if amount > 0.1:  # Only show services with significant cost
                            print("{:<30} {:<15.2f} {}".format(
                                service,
                                amount,
                                currency
                            ))
            except Exception as e:
                print(f"Error fetching cost data: {e}")
        
        elif choice == "7":
            # Switch AWS profile
            credentials_path = expand_path(aws_config.get("credentials_path", "%USERPROFILE%\\.aws\\credentials"))
            
            if not os.path.exists(credentials_path):
                print(f"AWS credentials file not found: {credentials_path}")
                return
            
            # Read credentials file
            config_parser = configparser.ConfigParser()
            config_parser.read(credentials_path)
            
            profiles = config_parser.sections()
            if "default" not in profiles and config_parser.has_section("default"):
                profiles.insert(0, "default")
            
            if not profiles:
                print("No AWS profiles found.")
                return
            
            print("\nAvailable AWS profiles:")
            for i, profile in enumerate(profiles):
                if profile == current_profile:
                    print(f"{i+1}. {profile} (current)")
                else:
                    print(f"{i+1}. {profile}")
            
            profile_idx = int(input("\nSelect profile number: ")) - 1
            if profile_idx < 0 or profile_idx >= len(profiles):
                print("Invalid selection.")
                return
            
            selected_profile = profiles[profile_idx]
            
            # Set environment variables
            os.environ["AWS_PROFILE"] = selected_profile
            
            # Create a batch file to set environment variables
            batch_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "set_aws_profile.bat")
            with open(batch_path, 'w') as f:
                f.write(f"@echo off\n")
                f.write(f"echo Setting AWS profile to {selected_profile}...\n")
                f.write(f"setx AWS_PROFILE {selected_profile}\n")
                f.write(f"echo Profile set to {selected_profile}\n")
                f.write(f"pause\n")
            
            # Execute the batch file
            subprocess.call(batch_path, shell=True)
            print(f"\nSwitched to profile '{selected_profile}'")
        
        elif choice == "8":
            return True
        
        else:
            print("Invalid choice.")
    
    except Exception as e:
        print(f"Error: {e}")
    
    input("\nPress Enter to continue...")
    return True


def manage_devops_tools(config):
    """Manage DevOps tools and workflows"""
    print("DevOps Tools Manager")
    print("=" * 50)
    
    devops_config = config.get("devops", {})
    
    # Show menu
    print("Select an option:")
    print("1. Manage Docker containers")
    print("2. Check Git repositories")
    print("3. Run Kubernetes commands")
    print("4. Check system services")
    print("5. Monitor resource usage")
    print("6. Return to main menu")
    
    choice = input("Enter your choice (1-6): ")
    
    try:
        if choice == "1":
            # Manage Docker containers
            print("\nDocker Container Management")
            print("-" * 30)
            
            # Check if Docker is installed
            try:
                result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
                print(result.stdout.strip())
            except:
                print("Docker not found. Please install Docker.")
                return
            
            # List running containers
            print("\nRunning containers:")
            subprocess.run(["docker", "ps"], shell=True)
            
            # Docker compose files
            compose_files = devops_config.get("docker_compose_files", [])
            expanded_files = [expand_path(f) for f in compose_files]
            valid_files = [f for f in expanded_files if os.path.exists(f)]
            
            if valid_files:
                print("\nAvailable docker-compose files:")
                for i, file in enumerate(valid_files):
                    print(f"{i+1}. {file}")
                
                file_idx = input("\nSelect file number (or press Enter to skip): ")
                if file_idx.isdigit() and 0 < int(file_idx) <= len(valid_files):
                    selected_file = valid_files[int(file_idx) - 1]
                    
                    print("\nDocker Compose actions:")
                    print("1. Up (start services)")
                    print("2. Down (stop services)")
                    print("3. Restart services")
                    print("4. View logs")
                    
                    action = input("Select action: ")
                    
                    if action == "1":
                        subprocess.run(["docker-compose", "-f", selected_file, "up", "-d"], shell=True)
                    elif action == "2":
                        subprocess.run(["docker-compose", "-f", selected_file, "down"], shell=True)
                    elif action == "3":
                        subprocess.run(["docker-compose", "-f", selected_file, "restart"], shell=True)
                    elif action == "4":
                        subprocess.run(["docker-compose", "-f", selected_file, "logs"], shell=True)
            else:
                print("No docker-compose files found.")
        
        elif choice == "2":
            # Check Git repositories
            print("\nGit Repository Management")
            print("-" * 30)
            
            # Check if Git is installed
            try:
                result = subprocess.run(["git", "--version"], capture_output=True, text=True)
                print(result.stdout.strip())
            except:
                print("Git not found. Please install Git.")
                return
            
            # Git repositories
            git_repos = devops_config.get("git_repos", [])
            expanded_repos = [expand_path(r) for r in git_repos]
            valid_repos = []
            
            for repo_path in expanded_repos:
                if os.path.exists(repo_path):
                    if os.path.isdir(repo_path):
                        # Check if it's a git repo or contains git repos
                        if os.path.exists(os.path.join(repo_path, ".git")):
                            valid_repos.append(repo_path)
                        else:
                            # Check subdirectories
                            for subdir in os.listdir(repo_path):
                                subdir_path = os.path.join(repo_path, subdir)
                                if os.path.isdir(subdir_path) and os.path.exists(os.path.join(subdir_path, ".git")):
                                    valid_repos.append(subdir_path)
            
            if valid_repos:
                print("\nAvailable Git repositories:")
                for i, repo in enumerate(valid_repos):
                    print(f"{i+1}. {repo}")
                
                repo_idx = input("\nSelect repository number (or press Enter to skip): ")
                if repo_idx.isdigit() and 0 < int(repo_idx) <= len(valid_repos):
                    selected_repo = valid_repos[int(repo_idx) - 1]
                    
                    print("\nGit actions:")
                    print("1. Status")
                    print("2. Pull latest changes")
                    print("3. View commit history")
                    print("4. Switch branch")
                    
                    action = input("Select action: ")
                    
                    if action == "1":
                        subprocess.run(["git", "-C", selected_repo, "status"], shell=True)
                    elif action == "2":
                        subprocess.run(["git", "-C", selected_repo, "pull"], shell=True)
                    elif action == "3":
                        subprocess.run(["git", "-C", selected_repo, "log", "--oneline", "--graph", "--decorate", "-n", "10"], shell=True)
                    elif action == "4":
                        # Get branches
                        result = subprocess.run(["git", "-C", selected_repo, "branch"], capture_output=True, text=True, shell=True)
                        branches = [b.strip() for b in result.stdout.split('\n') if b.strip()]
                        
                        print("\nAvailable branches:")
                        for branch in branches:
                            print(branch)
                        
                        branch_name = input("Enter branch name to switch to: ")
                        if branch_name:
                            subprocess.run(["git", "-C", selected_repo, "checkout", branch_name], shell=True)
            else:
                print("No Git repositories found.")
        
        elif choice == "3":
            # Run Kubernetes commands
            print("\nKubernetes Management")
            print("-" * 30)
            
            # Check if kubectl is installed
            try:
                result = subprocess.run(["kubectl", "version", "--client"], capture_output=True, text=True)
                print("kubectl client:", result.stdout.strip())
            except:
                print("kubectl not found. Please install kubectl.")
                return
            
            # Kubernetes config
            kube_config = expand_path(devops_config.get("kubernetes_config", "%USERPROFILE%\\.kube\\config"))
            
            if os.path.exists(kube_config):
                os.environ["KUBECONFIG"] = kube_config
                
                print("\nKubernetes actions:")
                print("1. Get nodes")
                print("2. Get pods")
                print("3. Get services")
                print("4. Get deployments")
                print("5. Describe resource")
                
                action = input("Select action: ")
                
                if action == "1":
                    subprocess.run(["kubectl", "get", "nodes"], shell=True)
                elif action == "2":
                    namespace = input("Enter namespace (or press Enter for all namespaces): ")
                    if namespace:
                        subprocess.run(["kubectl", "get", "pods", "-n", namespace], shell=True)
                    else:
                        subprocess.run(["kubectl", "get", "pods", "--all-namespaces"], shell=True)
                elif action == "3":
                    namespace = input("Enter namespace (or press Enter for all namespaces): ")
                    if namespace:
                        subprocess.run(["kubectl", "get", "services", "-n", namespace], shell=True)
                    else:
                        subprocess.run(["kubectl", "get", "services", "--all-namespaces"], shell=True)
                elif action == "4":
                    namespace = input("Enter namespace (or press Enter for all namespaces): ")
                    if namespace:
                        subprocess.run(["kubectl", "get", "deployments", "-n", namespace], shell=True)
                    else:
                        subprocess.run(["kubectl", "get", "deployments", "--all-namespaces"], shell=True)
                elif action == "5":
                    resource_type = input("Enter resource type (pod, service, deployment, etc.): ")
                    resource_name = input("Enter resource name: ")
                    namespace = input("Enter namespace: ")
                    
                    if resource_type and resource_name and namespace:
                        subprocess.run(["kubectl", "describe", resource_type, resource_name, "-n", namespace], shell=True)
            else:
                print(f"Kubernetes config not found: {kube_config}")
        
        elif choice == "4":
            # Check system services
            print("\nSystem Services Check")
            print("-" * 30)
            
            # List of common DevOps services to check
            services = [
                "docker", "kubelet", "jenkins", "nginx", "apache2", "postgresql", 
                "mysql", "mongodb", "redis", "elasticsearch"
            ]
            
            print("{:<20} {:<10}".format("Service", "Status"))
            print("-" * 30)
            
            for service in services:
                # Check if service exists and is running
                try:
                    result = subprocess.run(["sc", "query", service], capture_output=True, text=True)
                    if "RUNNING" in result.stdout:
                        status = "RUNNING"
                    elif "STOPPED" in result.stdout:
                        status = "STOPPED"
                    else:
                        status = "NOT FOUND"
                except:
                    status = "ERROR"
                
                print("{:<20} {:<10}".format(service, status))
        
        elif choice == "5":
            # Monitor resource usage
            print("\nSystem Resource Monitor")
            print("-" * 30)
            
            print("Monitoring system resources for 10 seconds...")
            
            for i in range(5):
                # CPU usage
                cpu_result = subprocess.run(["wmic", "cpu", "get", "loadpercentage"], capture_output=True, text=True)
                cpu_lines = cpu_result.stdout.strip().split('\n')
                cpu_usage = cpu_lines[1].strip() if len(cpu_lines) > 1 else "N/A"
                
                # Memory usage
                mem_result = subprocess.run(["wmic", "OS", "get", "FreePhysicalMemory,TotalVisibleMemorySize"], capture_output=True, text=True)
                mem_lines = mem_result.stdout.strip().split('\n')
                if len(mem_lines) > 1:
                    mem_values = mem_lines[1].split()
                    if len(mem_values) >= 2:
                        free_mem = int(mem_values[0]) / 1024  # Convert to MB
                        total_mem = int(mem_values[1]) / 1024  # Convert to MB
                        used_mem = total_mem - free_mem
                        mem_percent = (used_mem / total_mem) * 100
                    else:
                        mem_percent = "N/A"
                else:
                    mem_percent = "N/A"
                
                # Disk usage
                disk_result = subprocess.run(["wmic", "logicaldisk", "get", "deviceid,freespace,size"], capture_output=True, text=True)
                disk_lines = disk_result.stdout.strip().split('\n')
                
                print(f"\nSample {i+1}/5:")
                print(f"CPU Usage: {cpu_usage}%")
                print(f"Memory Usage: {mem_percent:.1f}%" if isinstance(mem_percent, float) else f"Memory Usage: {mem_percent}")
                
                if len(disk_lines) > 1:
                    print("Disk Usage:")
                    for line in disk_lines[1:]:  # Skip header
                        parts = line.split()
                        if len(parts) >= 3 and parts[0] and parts[1] and parts[2]:
                            try:
                                drive = parts[0]
                                free_space = int(parts[1]) / (1024**3)  # Convert to GB
                                total_space = int(parts[2]) / (1024**3)  # Convert to GB
                                used_space = total_space - free_space
                                usage_percent = (used_space / total_space) * 100 if total_space > 0 else 0
                                print(f"  {drive}: {usage_percent:.1f}% used ({used_space:.1f} GB / {total_space:.1f} GB)")
                            except:
                                pass
                
                # Network connections
                net_result = subprocess.run(["netstat", "-an"], capture_output=True, text=True)
                established = net_result.stdout.count("ESTABLISHED")
                listening = net_result.stdout.count("LISTENING")
                print(f"Network: {established} established, {listening} listening connections")
                
                if i < 4:  # Don't sleep after the last sample
                    time.sleep(2)
        
        elif choice == "6":
            return True
        
        else:
            print("Invalid choice.")
    
    except Exception as e:
        print(f"Error: {e}")
    
    input("\nPress Enter to continue...")
    return True




def main():
    parser = argparse.ArgumentParser(description="Dev Assistant - Streamline your Windows workflow")
    parser.add_argument("--clean", action="store_true", help="Clean temporary files")
    parser.add_argument("--organize", action="store_true", help="Organize files")
    parser.add_argument("--launch", action="store_true", help="Launch applications")
    parser.add_argument("--aws", action="store_true", help="Manage AWS resources")
    parser.add_argument("--devops", action="store_true", help="Manage DevOps tools")
    parser.add_argument("--config", action="store_true", help="Edit configuration")
    
    args = parser.parse_args()
    
    # If no arguments provided, show interactive menu
    run_all = not (args.clean or args.organize or args.launch or args.aws or args.devops or args.config)
    
    # Load configuration
    config = load_config()
    logging.info("Dev Assistant started")
    
    # Edit configuration if requested
    if args.config:
        config_path = os.path.abspath(CONFIG_FILE)
        print(f"Opening configuration file: {config_path}")
        os.system(f"notepad {config_path}")
        return
    

    
    # If specific arguments provided, run those actions
    if args.clean or args.organize or args.launch or args.aws or args.devops:
        print("Dev Assistant - Starting workflow automation")
        print("=" * 50)
        
        if args.clean:
            clean_disk_space(config)
            print("-" * 50)
        
        if args.organize:
            organize_files(config)
            print("-" * 50)
        
        if args.launch:
            launch_applications(config)
            print("-" * 50)
        
        if args.aws:
            manage_aws_resources(config)
            print("-" * 50)
        
        if args.devops:
            manage_devops_tools(config)
        
        print("=" * 50)
        print("Dev Assistant - Workflow automation complete")
        logging.info("Dev Assistant completed workflow automation")
        return
    
    # Interactive menu for all actions
    if run_all:
        while True:
            print("\n" + "=" * 50)
            print("Dev Assistant - Cloud & DevOps CLI")
            print("=" * 50)
            print("1. Clean disk space")
            print("2. Organize files")
            print("3. Launch applications")
            print("4. AWS Resource Manager")
            print("5. DevOps Tools Manager")
            print("6. Install DevOps Tools")
            print("7. Edit configuration")
            print("8. Exit")
            
            choice = input("\nEnter your choice (1-8): ")
            
            if choice == "1":
                clean_disk_space(config)
            elif choice == "2":
                organize_files(config)
            elif choice == "3":
                launch_applications(config)
            elif choice == "4":
                if AWS_AVAILABLE:
                    manage_aws_resources(config)
                else:
                    print("\nAWS SDK (boto3) not installed. To install boto3:")
                    print("1. Run: py -m pip install boto3")
                    print("2. If that doesn't work, try: python -m pip install boto3")
                    print("\nAlternatively, you can use the tool without AWS features.")
                    input("Press Enter to continue...")
            elif choice == "5":
                manage_devops_tools(config)
            elif choice == "6":
                # Install DevOps Tools
                install_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "install_tools.ps1")
                print(f"\nLaunching DevOps Tools Installer...")
                print("NOTE: This will open a new PowerShell window with admin privileges.")
                print("Please follow the instructions in that window.")
                
                # Launch PowerShell as admin with the install script
                subprocess.Popen(["powershell", "-ExecutionPolicy", "Bypass", "-Command", 
                                 f"Start-Process powershell -ArgumentList '-ExecutionPolicy Bypass -File \"{install_script}\"' -Verb RunAs"], 
                                shell=True)
                
                input("\nPress Enter to continue after installation is complete...")
            elif choice == "7":
                config_path = os.path.abspath(CONFIG_FILE)
                print(f"Opening configuration file: {config_path}")
                os.system(f"notepad {config_path}")
            elif choice == "8":
                print("Exiting Dev Assistant. Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")
        
        logging.info("Dev Assistant completed workflow automation")

if __name__ == "__main__":
    main()