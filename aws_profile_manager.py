#!/usr/bin/env python
"""
AWS Profile Manager - A simple tool to manage AWS CLI profiles
"""
import os
import json
import configparser
import subprocess
from pathlib import Path

# Load configuration
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

def load_config():
    """Load configuration from config.json file"""
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        return {}

def expand_path(path):
    """Expand environment variables in path"""
    return os.path.expandvars(path)

def manage_aws_profiles():
    """Manage AWS profiles and switch between them"""
    print("\nAWS Profile Manager")
    print("=" * 50)
    
    config = load_config()
    aws_config = config.get("aws_profiles", {})
    credentials_path = expand_path(aws_config.get("credentials_path", "%USERPROFILE%\\.aws\\credentials"))
    config_path = expand_path(aws_config.get("config_path", "%USERPROFILE%\\.aws\\config"))
    favorites = aws_config.get("favorites", [])
    default_region = aws_config.get("default_region", "us-east-1")
    
    # Check if AWS credentials file exists
    if not os.path.exists(credentials_path):
        print(f"AWS credentials file not found at: {credentials_path}")
        create_new = input("Would you like to create a new credentials file? (y/n): ").lower()
        if create_new == 'y':
            os.makedirs(os.path.dirname(credentials_path), exist_ok=True)
            with open(credentials_path, 'w') as f:
                f.write("[default]\n")
                f.write("aws_access_key_id = YOUR_ACCESS_KEY\n")
                f.write("aws_secret_access_key = YOUR_SECRET_KEY\n")
            print(f"Created credentials file at {credentials_path}")
            print("Please edit the file to add your AWS credentials")
        return
    
    # Read AWS credentials file
    credentials = configparser.ConfigParser()
    credentials.read(credentials_path)
    
    # Read AWS config file if it exists
    config_parser = configparser.ConfigParser()
    if os.path.exists(config_path):
        config_parser.read(config_path)
    
    # Get current default profile
    current_profile = "default"
    if "AWS_PROFILE" in os.environ:
        current_profile = os.environ["AWS_PROFILE"]
    
    # Get current region
    current_region = default_region
    if "AWS_REGION" in os.environ:
        current_region = os.environ["AWS_REGION"]
    elif "AWS_DEFAULT_REGION" in os.environ:
        current_region = os.environ["AWS_DEFAULT_REGION"]
    elif config_parser.has_section(f"profile {current_profile}") and config_parser.has_option(f"profile {current_profile}", "region"):
        current_region = config_parser.get(f"profile {current_profile}", "region")
    
    # Display available profiles
    print(f"\nCurrent profile: {current_profile} ({current_region})")
    print("\nAvailable profiles:")
    
    # Get all profiles
    profiles = list(credentials.sections())
    if "default" not in profiles and credentials.has_section("default"):
        profiles.insert(0, "default")
    
    # Display profiles with favorites highlighted
    favorite_names = [f["name"] for f in favorites]
    for i, profile in enumerate(profiles):
        profile_str = f"  {i+1}. {profile}"
        
        # Check if profile is a favorite
        if profile in favorite_names:
            fav = next(f for f in favorites if f["name"] == profile)
            profile_str = f"  {i+1}. * {profile} (favorite)"
        
        # Highlight current profile
        if profile == current_profile:
            profile_str += " (active)"
            
        print(profile_str)
    
    # Profile management options
    print("\nOptions:")
    print("  a. Add new profile")
    print("  e. Edit existing profile")
    print("  d. Delete profile")
    print("  r. Change region for a profile")
    print("  f. Add/remove from favorites")
    print("  q. Quit")
    
    choice = input("\nEnter profile number or option: ").strip().lower()
    
    if choice == 'q':
        return
    elif choice == 'a':
        # Add new profile
        new_profile = input("Enter new profile name: ").strip()
        if not new_profile:
            print("Profile name cannot be empty")
            return
        
        if credentials.has_section(new_profile):
            print(f"Profile '{new_profile}' already exists")
            return
        
        access_key = input("Enter AWS access key ID: ").strip()
        secret_key = input("Enter AWS secret access key: ").strip()
        region = input(f"Enter AWS region (default: {default_region}): ").strip() or default_region
        
        # Add to credentials file
        credentials.add_section(new_profile)
        credentials.set(new_profile, "aws_access_key_id", access_key)
        credentials.set(new_profile, "aws_secret_access_key", secret_key)
        
        with open(credentials_path, 'w') as f:
            credentials.write(f)
        
        # Add to config file
        if not config_parser.has_section(f"profile {new_profile}"):
            config_parser.add_section(f"profile {new_profile}")
        
        config_parser.set(f"profile {new_profile}", "region", region)
        
        # Create config file if it doesn't exist
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, 'w') as f:
            config_parser.write(f)
        
        print(f"\nProfile '{new_profile}' added successfully")
        
        # Ask if user wants to switch to this profile
        switch = input(f"Switch to profile '{new_profile}'? (y/n): ").lower()
        if switch == 'y':
            # Set environment variables for current session
            os.environ["AWS_PROFILE"] = new_profile
            os.environ["AWS_DEFAULT_REGION"] = region
            
            # Create a batch file to set environment variables
            batch_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "set_aws_profile.bat")
            with open(batch_path, 'w') as f:
                f.write(f"@echo off\n")
                f.write(f"echo Setting AWS profile to {new_profile}...\n")
                f.write(f"setx AWS_PROFILE {new_profile}\n")
                f.write(f"setx AWS_DEFAULT_REGION {region}\n")
                f.write(f"echo Profile set to {new_profile} ({region})\n")
                f.write(f"pause\n")
            
            # Execute the batch file
            subprocess.call(batch_path, shell=True)
            print(f"\nSwitched to profile '{new_profile}' with region '{region}'")
    
    elif choice.isdigit():
        # Switch to selected profile
        index = int(choice) - 1
        if 0 <= index < len(profiles):
            selected_profile = profiles[index]
            
            # Get region for this profile
            section_name = "default" if selected_profile == "default" else f"profile {selected_profile}"
            if config_parser.has_section(section_name):
                selected_region = config_parser.get(section_name, "region", fallback=default_region)
            else:
                selected_region = default_region
            
            # Set environment variables for current session
            os.environ["AWS_PROFILE"] = selected_profile
            os.environ["AWS_DEFAULT_REGION"] = selected_region
            
            # Create a batch file to set environment variables
            batch_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "set_aws_profile.bat")
            with open(batch_path, 'w') as f:
                f.write(f"@echo off\n")
                f.write(f"echo Setting AWS profile to {selected_profile}...\n")
                f.write(f"setx AWS_PROFILE {selected_profile}\n")
                f.write(f"setx AWS_DEFAULT_REGION {selected_region}\n")
                f.write(f"echo Profile set to {selected_profile} ({selected_region})\n")
                f.write(f"pause\n")
            
            # Execute the batch file
            subprocess.call(batch_path, shell=True)
            print(f"\nSwitched to profile '{selected_profile}' with region '{selected_region}'")
        else:
            print("Invalid profile number")
    
    else:
        print("Invalid option")

if __name__ == "__main__":
    manage_aws_profiles()