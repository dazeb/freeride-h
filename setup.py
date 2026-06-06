from setuptools import setup

setup(
    name="freeride-h",
    version="1.0.0",
    py_modules=["freeride", "watcher"],
    entry_points={
        "console_scripts": [
            "freeride=freeride:main",
            "freeride-watcher=watcher:main",
        ],
    },
    python_requires=">=3.10",
    description="Multi-provider free-model manager for Hermes AI agents. Browse, switch, and auto-rotate across 9 providers and 43+ free models.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="dazeb",
    author_email="dazeb2025@gmail.com",
    url="https://github.com/dazeb/freeride-h",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
