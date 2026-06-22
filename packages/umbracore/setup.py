from setuptools import setup, find_packages

setup(
    name="vespera-core",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "Flask>=2.3.0",
        "Flask-Cors>=4.0.0",
        "psutil>=5.9.0",
    ],
    entry_points={
        "console_scripts": [
            "vespera-core=main:main",
        ],
    },
)
