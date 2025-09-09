from setuptools import setup, find_packages

setup(
    name="aila",
    version="2.0.0",
    packages=find_packages(),
    install_requires=[
        "google-genai>=0.1.0",
    ],
    entry_points={
        "console_scripts": [
            "aila=aila.cli:main",
        ],
    },
    python_requires=">=3.9",
    description="Aila 2.0: AI-powered programming language using Gemini",
    author="Your Name",
)
