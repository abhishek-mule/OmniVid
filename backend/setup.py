from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="omnivid-backend",
    version="0.1.0",
    author="OmniVid Team",
    author_email="contact@omnivid.example",
    description="Backend service for OmniVid video processing platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/abhishek-mule/OmniVid",
    packages=find_packages(where="src", include=["src*"]),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            "omnivid-backend=src.main:main",
        ],
    },
)
