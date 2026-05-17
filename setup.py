"""
Setup script for Security Analyst System
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = [
        line.strip() 
        for line in requirements_file.read_text().split('\n')
        if line.strip() and not line.startswith('#')
    ]

setup(
    name="security-analyst",
    version="1.0.0",
    author="Security Team",
    author_email="security@example.com",
    description="AI-powered security analysis and anomaly detection system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/security-analyst",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Security",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "security-analyst=main:cli",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.json", "*.yaml", "*.yml"],
    },
    zip_safe=False,
)

# Made with Bob
