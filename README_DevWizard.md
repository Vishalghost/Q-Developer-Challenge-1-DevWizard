# DevWizard 🧙‍♂️

A magical CLI tool for cloud and DevOps engineers to streamline your Windows workflow.

```
 _____             __          ___                      _ 
|  __ \            \ \        / (_)                    | |
| |  | | _____   __ \ \  /\  / / _ ______ _ _ __ ___ __| |
| |  | |/ _ \ \ / /  \ \/  \/ / | |_  / _` | '__/ _ \ _` |
| |__| |  __/\ V /    \  /\  /  | |/ / (_| | | |  __/ (_| |
|_____/ \___| \_/      \/  \/   |_/___\__,_|_|  \___|\__,_|
                                                          
        Your Magical DevOps Assistant - v1.0.0
```

## Features

- **Workspace Cleanup**: Remove temporary files with a single command
- **DevOps Tools Check**: Verify if Git, Docker, and kubectl are installed
- **System Monitoring**: Check CPU, memory, and disk usage
- **Application Launcher**: Start your development tools with one command
- **Tool Installer**: Easily install Git, Docker, and kubectl

## Installation

1. Ensure you have Python 3.6+ installed
2. Clone or download this repository
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

## Configuration

Edit the `devwizard_config.json` file to customize:

- Workspace cleanup settings
- Tool paths
- Cloud provider settings
- Applications to launch

You can edit the configuration directly or use:

```
python devwizard.py --config
```

## Why DevWizard?

DevWizard makes your development workflow magical by:

- Eliminating repetitive setup tasks
- Ensuring your tools are properly installed
- Providing quick access to system information
- Streamlining your development environment

## Created with Amazon Q Developer

This tool was created with assistance from Amazon Q Developer.