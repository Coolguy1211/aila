from setuptools import setup, find_packages

setup(
    name="aila",
    version="3.0.0",
    packages=find_packages(),
    install_requires=[
        "google-genai>=0.1.0",
        "ollama>=0.3.0",
    ],
    entry_points={
        "console_scripts": [
            "aila=aila.cli:main",
        ],
    },
    python_requires=">=3.9",
    description="Aila 3.0: AI-powered programming language with local interpreter and GUI",
    author="Your Name",
)
