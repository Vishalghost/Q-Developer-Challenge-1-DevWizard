# Dev Assistant for Cloud & DevOps

A CLI automation tool built with Amazon Q Developer to streamline your Windows workflow for cloud and DevOps engineers. Automate routine tasks, manage AWS resources, and control DevOps tools from a single interface.

## Features

- **Disk Cleanup**: Removes temporary files based on age and extension
- **File Organization**: Automatically sorts files into folders based on file types
- **Application Launcher**: Starts your daily development tools with one command
- **AWS Resource Manager**: Manage EC2 instances, S3 buckets, and monitor AWS costs
- **DevOps Tools**: Control Docker containers, Git repositories, and Kubernetes clusters
- **System Monitoring**: Check service status and resource usage

## Installation

1. Ensure you have Python 3.6+ installed
2. Clone or download this repository
3. Run the tool and use the built-in installer:
   ```
   python dev_assistant.py
   ```
   Then select option 6 "Install DevOps Tools" from the menu

4. Alternatively, install dependencies manually:
   ```
   pip install boto3
   ```

## Usage

Run the interactive menu:

```
python dev_assistant.py
```

Or use specific features:

```
python dev_assistant.py --clean     # Only clean temporary files
python dev_assistant.py --organize  # Only organize files
python dev_assistant.py --launch    # Only launch applications
python dev_assistant.py --aws       # Manage AWS resources
python dev_assistant.py --devops    # Manage DevOps tools
python dev_assistant.py --config    # Edit configuration file
```

## AWS Features

- List and manage EC2 instances
- Browse S3 buckets
- Check AWS service health
- Deploy CloudFormation stacks
- Run Terraform plans
- Monitor AWS costs
- Switch between AWS profiles

## DevOps Features

- Manage Docker containers
- Check Git repositories
- Run Kubernetes commands
- Monitor system services
- Track resource usage
- Install required DevOps tools (Git, Docker, kubectl)

## Configuration

Edit the `config.json` file to customize:

- Which directories to clean
- File organization rules
- Applications to launch
- AWS settings and paths
- DevOps tool configurations

You can edit the configuration directly or use:

```
python dev_assistant.py --config
```

## Created with Amazon Q Developer

This tool was created with assistance from Amazon Q Developer.