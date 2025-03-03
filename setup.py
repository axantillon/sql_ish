#!/usr/bin/env python3
"""
setup.py - Installation script for SQL-ish

This file enables installation of the SQL-ish package using pip.
"""

from setuptools import setup, find_packages
import os
import sys

# Add the current directory to the Python path
sys.path.insert(0, os.path.abspath('.'))

# Read requirements from requirements.txt
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

# Read the version from __init__.py
with open('__init__.py') as f:
    for line in f:
        if line.startswith('__version__'):
            version = line.split('=')[1].strip().strip("'").strip('"')
            break

# Read the long description from README.md
with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="sql_ish",
    version=version,
    description="A lightweight SQL implementation in Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Axel Cantillon",
    author_email="example@example.com",  # Replace with your email if you want
    url="https://github.com/yourusername/sql-ish",  # Replace with your repository URL
    packages=['modules', 'modules.cli', 'modules.core', 'modules.engine', 'modules.parser', 'modules.utils', 'modules.tests'],
    package_dir={'modules': 'modules'},
    py_modules=["main", "__main__", "__init__"],
    include_package_data=True,
    install_requires=requirements,
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "sqlish=main:main",  # Use the main function from root main.py
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    keywords="sql, database, educational",
) 