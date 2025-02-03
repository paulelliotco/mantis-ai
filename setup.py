from setuptools import setup, find_packages
import os
import re


def get_version():
    with open(os.path.join("mantis", "__init__.py"), "r") as f:
        version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", f.read(), re.M)
        if version_match:
            return version_match.group(1)
        raise RuntimeError("Unable to find version string.")


setup(
    name="mantis",
    version=get_version(),
    author="Your Name",
    author_email="your.email@example.com",
    description="A Python package for transcribing audio files, summarizing text, and extracting information using Gemini AI and Pydantic.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/mantis",
    packages=find_packages(),
    install_requires=[
        "pydantic>=1.8",
        "google-generativeai",  # Ensure this is the correct package name
        "requests",  # For making API calls
        "python-dotenv",
        "yt_dlp",
        "sphinx",
        "sphinx_rtd_theme",
        "sphinx-autodoc-typehints",
        "flake8",
        "black",
    ],
    entry_points={
        "console_scripts": [
            "mantis=mantis.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
