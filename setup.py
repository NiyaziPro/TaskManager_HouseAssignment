#!/usr/bin/env python3
"""
Setup script for TaskMeister - Worker Assignment System
"""

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Read requirements
def read_requirements():
    """Read requirements from requirements.txt file."""
    requirements_path = os.path.join(this_directory, 'requirements.txt')
    with open(requirements_path, encoding='utf-8') as f:
        requirements = []
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                requirements.append(line)
    return requirements

setup(
    name="taskmeister",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A comprehensive GUI application for managing worker assignments to houses",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/taskmeister",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/taskmeister/issues",
        "Documentation": "https://github.com/yourusername/taskmeister/wiki",
        "Source Code": "https://github.com/yourusername/taskmeister",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Office/Business :: Scheduling",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Environment :: X11 Applications :: Gtk",
        "Environment :: MacOS X",
        "Environment :: Win32 (MS Windows)",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "black>=21.0.0",
            "flake8>=3.8.0",
            "mypy>=0.812",
            "pytest-cov>=2.10.0",
        ],
        "docs": [
            "sphinx>=3.0.0",
            "sphinx-rtd-theme>=0.5.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "taskmeister=taskmeister:main",
        ],
    },
    include_package_data=True,
    package_data={
        "taskmeister": [
            "*.md",
            "docs/*",
        ],
    },
    keywords=[
        "task management",
        "worker assignment",
        "scheduling",
        "GUI application",
        "tkinter",
        "email notifications",
        "database management",
        "house management",
    ],
    zip_safe=False,
)