# DevWizard 🧙‍♂️

A magical CLI tool for cloud and DevOps engineers to streamline your workflow across Windows, macOS, and Linux.

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
- **DevOps Tools Check**: Verify if Git, Docker, kubectl, Terraform, AWS CLI, Ansible, and many other DevOps tools are installed
- **System Monitoring**: Check CPU, memory, and disk usage in real-time
- **Application Launcher**: Start your development tools with one command
- **Tool Installer**: Easily install Git, Docker, kubectl, Terraform, AWS CLI, and other DevOps tools with a customizable selection
- **Git Helper**: Streamline common Git operations (init, clone, commit, push)
- **Docker Helper**: Manage containers and images with ease
- **Kubernetes Helper**: Simplify kubectl commands and cluster management
- **AWS Helper**: Manage EC2, S3, Lambda, and other AWS resources

## Installation

### Option 1: Install from GitHub

```
# Clone the repository
git clone https://github.com/Vishalghost/Q-Developer-Challenge-1-DevWizard.git

# Navigate to the directory
cd Q-Developer-Challenge-1-DevWizard

# Install DevWizard
pip install -e .
```

After installation, you can run DevWizard from anywhere by simply typing:

```
devwizard
```

### Option 2: Install from PyPI (Coming Soon)

```
pip install devwizard
```

### Required Tools (Optional)

DevWizard can help you install these tools, but they're required for certain features:
- Git (for Git helper)
- Docker (for Docker helper)
- kubectl (for Kubernetes helper)
- AWS CLI (for AWS helper)

## Usage

### Basic Usage

1. Open a command prompt, PowerShell, or terminal window
2. Run the tool: `devwizard`
3. Use the interactive menu to select the feature you want to use
4. Follow the on-screen prompts for each feature

### Command Line Options

You can also run specific features directly from the command line:

```
devwizard --clean     # Clean workspace
devwizard --check     # Check DevOps tools
devwizard --monitor   # Monitor system resources
devwizard --launch    # Launch applications
devwizard --install   # Install DevOps tools
devwizard --config    # Edit configuration
```

### Using the Helpers

#### Git Helper
1. Select "Git Helper" from the main menu
2. Choose the Git operation you want to perform
3. Follow the prompts to provide repository paths, commit messages, etc.

#### Docker Helper
1. Select "Docker Helper" from the main menu
2. Choose the Docker operation you want to perform
3. Follow the prompts to provide container names, image names, etc.

#### Kubernetes Helper
1. Select "Kubernetes Helper" from the main menu
2. Choose the Kubernetes operation you want to perform
3. Follow the prompts to provide namespace, resource types, etc.

#### AWS Helper
1. Select "AWS Helper" from the main menu
2. Choose the AWS operation you want to perform
3. Follow the prompts to provide instance IDs, profile names, etc.

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

### AWS Helper
- List EC2 instances, S3 buckets, and Lambda functions
- Describe and manage EC2 instances
- Switch between AWS profiles
- Check AWS service status

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

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.