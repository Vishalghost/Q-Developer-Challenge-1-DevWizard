from setuptools import setup, find_packages

setup(
    name="devwizard",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "psutil>=5.9.0",
    ],
    entry_points={
        "console_scripts": [
            "devwizard=devwizard:main",
        ],
    },
    author="DevWizard Team",
    author_email="example@example.com",
    description="A magical CLI tool for cloud and DevOps engineers",
    keywords="devops, cli, tools, cloud",
    url="https://github.com/Vishalghost/Q-Developer-Challenge-1-DevWizard",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)