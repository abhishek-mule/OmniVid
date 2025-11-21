import os
from setuptools import setup, find_packages

# Read requirements from the clean file if it exists, otherwise use defaults
requirements = []
if os.path.exists("requirements_clean.txt"):
    with open("requirements_clean.txt", "r") as f:
        requirements = [
            line.strip() for line in f if line.strip() and not line.startswith("#")
        ]
else:
    requirements = [
        "fastapi==0.103.1",
        "uvicorn[standard]==0.23.2",
        "python-multipart==0.0.6",
        "python-jose[cryptography]==3.3.0",
        "passlib[bcrypt]==1.7.4",
        "python-dotenv==1.0.0",
        "sqlalchemy==2.0.20",
        "psycopg2-binary==2.9.7",
        "alembic==1.12.0",
        "pydantic[email]==2.3.0",
    ]

# Read long description from README.md if it exists
current_dir = os.path.abspath(os.path.dirname(__file__))
readme_path = os.path.join(current_dir, "README.md")
long_description = ""
if os.path.exists(readme_path):
    with open(readme_path, "r", encoding="utf-8") as f:
        long_description = f.read()

setup(
    name="omnivid-backend",
    version="0.1.0",
    author="OmniVid Team",
    author_email="contact@omnivid.example",
    description="Backend service for OmniVid video processing platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/abhishek-mule/OmniVid",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
