# DevWizard 🧙‍♂️

A magical CLI tool for cloud and DevOps engineers to streamline your Windows workflow.

```
 _____              _    _ _                       _ 
|  __ \            | |  | (_)                     | |
| |  | | _____   __| |  | |_ ______ _ _ __ __ _  | |
| |  | |/ _ \ \ / /| |/\| | |_  / _` | '__/ _` | | |
| |__| |  __/\ V / \  /\  / |/ / (_| | | | (_| | |_|
|_____/ \___| \_/   \/  \/|_/___\__,_|_|  \__,_| (_)
                                                   
        Your Magical DevOps Assistant - v1.0.0
```

## Features

- **Workspace Cleanup**: Remove temporary files with a single command
- **DevOps Tools Check**: Verify if Git, Docker, and kubectl are installed
- **System Monitoring**: Check CPU, memory, and disk usage in real-time
- **Application Launcher**: Start your development tools with one command
- **Tool Installer**: Easily install Git, Docker, and kubectl
- **Git Helper**: Streamline common Git operations (init, clone, commit, push)
- **Docker Helper**: Manage containers and images with ease
- **Kubernetes Helper**: Simplify kubectl commands and cluster management

## Installation

1. Ensure you have Python 3.6+ installed
2. Clone this repository
3. Run the tool:
   ```
   python devwizard.py
   ```

## Usage

Run the interactive menu:

```
python devwizard.py
```

Or use specific features:

```
python devwizard.py --clean     # Clean workspace
python devwizard.py --check     # Check DevOps tools
python devwizard.py --monitor   # Monitor system resources
python devwizard.py --launch    # Launch applications
python devwizard.py --install   # Install DevOps tools
python devwizard.py --config    # Edit configuration
```

## DevOps Features

### Git Helper
- Initialize repositories
- Clone repositories
- Check status
- Add and commit changes
- Push and pull changes

### Docker Helper
- List containers and images
- Run and manage containers
- Pull images
- Docker Compose operations

### Kubernetes Helper
- Get pods, services, and deployments
- Describe resources
- Apply YAML files
- Get logs
- Switch contexts

## System Features

### System Monitoring
- Real-time CPU usage
- Memory usage in MB
- Disk space utilization
- Process count

### Workspace Cleanup
- Remove temporary files based on age and extension
- Configurable cleanup directories

## Created with Amazon Q Developer

This tool was created with assistance from Amazon Q Developer.