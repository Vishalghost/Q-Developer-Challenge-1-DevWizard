#!/usr/bin/env python
"""
AWS Profile Tray Manager - A system tray utility for quick AWS profile switching
"""
import os
import sys
import json
import configparser
import subprocess
from pathlib import Path
import threading
import time

# Optional imports - will be used if available
try:
    import pystray
    from PIL import Image, ImageDraw, ImageFont
    TRAY_AVAILABLE = True
except ImportError:
    TRAY_AVAILABLE = False

# Constants
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

def get_aws_profiles():
    """Get AWS profiles from credentials file"""
    config = load_config()
    aws_config = config.get("aws_profiles", {})
    credentials_path = expand_path(aws_config.get("credentials_path", "%USERPROFILE%\\.aws\\credentials"))
    config_path = expand_path(aws_config.get("config_path", "%USERPROFILE%\\.aws\\config"))
    favorites = aws_config.get("favorites", [])
    default_region = aws_config.get("default_region", "us-east-1")
    
    # Check if AWS credentials file exists
    if not os.path.exists(credentials_path):
        return [], "default", default_region, favorites
    
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
    
    # Get all profiles
    profiles = list(credentials.sections())
    if "default" not in profiles and credentials.has_section("default"):
        profiles.insert(0, "default")
    
    return profiles, current_profile, current_region, favorites

def switch_profile(profile_name):
    """Switch to the selected AWS profile"""
    config = load_config()
    aws_config = config.get("aws_profiles", {})
    config_path = expand_path(aws_config.get("config_path", "%USERPROFILE%\\.aws\\config"))
    default_region = aws_config.get("default_region", "us-east-1")
    
    # Read AWS config file if it exists
    config_parser = configparser.ConfigParser()
    if os.path.exists(config_path):
        config_parser.read(config_path)
    
    # Get region for this profile
    section_name = "default" if profile_name == "default" else f"profile {profile_name}"
    if config_parser.has_section(section_name):
        selected_region = config_parser.get(section_name, "region", fallback=default_region)
    else:
        selected_region = default_region
    
    # Set environment variables for current session
    os.environ["AWS_PROFILE"] = profile_name
    os.environ["AWS_DEFAULT_REGION"] = selected_region
    
    # Create a batch file to set environment variables
    batch_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "set_aws_profile.bat")
    with open(batch_path, 'w') as f:
        f.write(f"@echo off\n")
        f.write(f"echo Setting AWS profile to {profile_name}...\n")
        f.write(f"setx AWS_PROFILE {profile_name}\n")
        f.write(f"setx AWS_DEFAULT_REGION {selected_region}\n")
        f.write(f"echo Profile set to {profile_name} ({selected_region})\n")
    
    # Execute the batch file silently
    subprocess.Popen(batch_path, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    return selected_region

def create_profile_icon(profile, color="blue"):
    """Create an icon with the profile's first letter"""
    # Map color names to RGB values
    color_map = {
        "red": (231, 76, 60),
        "green": (46, 204, 113),
        "blue": (52, 152, 219),
        "yellow": (241, 196, 15),
        "purple": (155, 89, 182),
        "orange": (230, 126, 34),
        "cyan": (26, 188, 156),
        "magenta": (236, 64, 122),
        "gray": (149, 165, 166)
    }
    
    # Default to blue if color not found
    bg_color = color_map.get(color.lower(), color_map["blue"])
    
    # Create a square icon
    icon_size = 64
    icon_image = Image.new('RGB', (icon_size, icon_size), color=bg_color)
    
    # Add the first letter of the profile
    draw = ImageDraw.Draw(icon_image)
    letter = profile[0].upper()
    
    # Try to use a font, fall back to simple text if font not available
    try:
        font = ImageFont.truetype("arial.ttf", 32)
        # Get text size to center it
        text_width, text_height = draw.textsize(letter, font=font)
        position = ((icon_size - text_width) // 2, (icon_size - text_height) // 2 - 2)
        draw.text(position, letter, fill=(255, 255, 255), font=font)
    except:
        # Fallback - just draw text approximately centered
        draw.text((24, 16), letter, fill=(255, 255, 255))
    
    return icon_image

def create_tray_icon():
    """Create system tray icon for AWS profile management"""
    if not TRAY_AVAILABLE:
        print("System tray feature unavailable: pystray or PIL not installed")
        return None
    
    # Get AWS profiles
    profiles, current_profile, current_region, favorites = get_aws_profiles()
    
    # Find color for current profile
    profile_color = "blue"
    for fav in favorites:
        if fav["name"] == current_profile:
            profile_color = fav.get("color", "blue")
            break
    
    # Create icon for current profile
    icon_image = create_profile_icon(current_profile, profile_color)
    
    # Function to create menu
    def create_menu():
        # Get updated profiles
        profiles, current_profile, current_region, favorites = get_aws_profiles()
        
        # Create profile menu items
        profile_items = []
        
        # Add favorites first
        if favorites:
            for fav in favorites:
                profile_name = fav["name"]
                if profile_name in profiles:
                    profile_items.append(
                        pystray.MenuItem(
                            f"★ {profile_name} ({fav.get('region', 'unknown')})",
                            lambda item, profile=profile_name: on_profile_switch(profile),
                            checked=lambda item, profile=profile_name: profile == current_profile
                        )
                    )
            
            # Add separator after favorites
            profile_items.append(pystray.Menu.SEPARATOR)
        
        # Add all profiles
        for profile in profiles:
            # Skip if already in favorites
            if any(fav["name"] == profile for fav in favorites):
                continue
                
            # Get region for this profile
            config = load_config()
            aws_config = config.get("aws_profiles", {})
            config_path = expand_path(aws_config.get("config_path", "%USERPROFILE%\\.aws\\config"))
            default_region = aws_config.get("default_region", "us-east-1")
            
            # Read AWS config file if it exists
            config_parser = configparser.ConfigParser()
            if os.path.exists(config_path):
                config_parser.read(config_path)
            
            # Get region for this profile
            section_name = "default" if profile == "default" else f"profile {profile}"
            if config_parser.has_section(section_name):
                region = config_parser.get(section_name, "region", fallback=default_region)
            else:
                region = default_region
                
            profile_items.append(
                pystray.MenuItem(
                    f"{profile} ({region})",
                    lambda item, profile=profile: on_profile_switch(profile),
                    checked=lambda item, profile=profile: profile == current_profile
                )
            )
        
        # Add management options
        menu_items = [
            pystray.MenuItem(f"Current: {current_profile} ({current_region})", None, enabled=False),
            pystray.Menu.SEPARATOR,
        ]
        
        # Add profile items
        menu_items.extend(profile_items)
        
        # Add management options
        menu_items.extend([
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Open AWS Profile Manager", on_open_manager),
            pystray.MenuItem("Refresh Profiles", on_refresh),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Exit", on_exit)
        ])
        
        return menu_items
    
    # Event handlers
    def on_profile_switch(profile_name):
        nonlocal icon_image, current_profile, current_region
        
        # Switch profile
        new_region = switch_profile(profile_name)
        current_profile = profile_name
        current_region = new_region
        
        # Find color for new profile
        profile_color = "blue"
        for fav in favorites:
            if fav["name"] == profile_name:
                profile_color = fav.get("color", "blue")
                break
        
        # Update icon
        new_icon = create_profile_icon(profile_name, profile_color)
        icon.icon = new_icon
        icon_image = new_icon
        
        # Update menu
        icon.menu = pystray.Menu(*create_menu())
        
        # Show notification
        icon.notify(f"AWS Profile switched to {profile_name} ({new_region})")
    
    def on_open_manager():
        # Open AWS profile manager
        subprocess.Popen(["cmd", "/c", "start", os.path.join(os.path.dirname(os.path.abspath(__file__)), "aws_profile.bat")])
    
    def on_refresh():
        nonlocal profiles, current_profile, current_region, favorites
        # Refresh profiles
        profiles, current_profile, current_region, favorites = get_aws_profiles()
        
        # Find color for current profile
        profile_color = "blue"
        for fav in favorites:
            if fav["name"] == current_profile:
                profile_color = fav.get("color", "blue")
                break
        
        # Update icon
        new_icon = create_profile_icon(current_profile, profile_color)
        icon.icon = new_icon
        
        # Update menu
        icon.menu = pystray.Menu(*create_menu())
        
        # Show notification
        icon.notify("AWS Profiles refreshed")
    
    def on_exit(icon):
        icon.stop()
    
    # Create the icon
    icon = pystray.Icon(
        "aws_profile_manager",
        icon_image,
        f"AWS Profile: {current_profile}",
        menu=pystray.Menu(*create_menu())
    )
    
    # Start a thread to periodically update the menu
    def update_thread():
        while True:
            time.sleep(30)  # Check every 30 seconds
            try:
                new_profiles, new_current, new_region, new_favorites = get_aws_profiles()
                
                # If profile changed externally, update the icon
                if new_current != current_profile:
                    # Find color for new profile
                    profile_color = "blue"
                    for fav in new_favorites:
                        if fav["name"] == new_current:
                            profile_color = fav.get("color", "blue")
                            break
                    
                    # Update icon
                    new_icon = create_profile_icon(new_current, profile_color)
                    icon.icon = new_icon
                    
                    # Update menu
                    icon.menu = pystray.Menu(*create_menu())
                    
                    # Update variables
                    nonlocal profiles, current_profile, current_region, favorites
                    profiles = new_profiles
                    current_profile = new_current
                    current_region = new_region
                    favorites = new_favorites
            except:
                # Ignore errors in the update thread
                pass
    
    # Start update thread
    threading.Thread(target=update_thread, daemon=True).start()
    
    return icon

def main():
    """Main function"""
    if not TRAY_AVAILABLE:
        print("System tray feature unavailable: pystray or PIL not installed")
        print("Please install the required packages:")
        print("pip install pystray pillow")
        return
    
    print("Starting AWS Profile Tray Manager...")
    print("The application will run in the system tray.")
    
    # Create and run tray icon
    icon = create_tray_icon()
    if icon:
        icon.run()

if __name__ == "__main__":
    main()