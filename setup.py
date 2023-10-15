from setuptools import setup, find_packages

setup(
    name='stat-folder',
    version='v1.0',
    packages=find_packages(),
    python_requires=">=3.10",
    package_data={"": ["*.ini"]},
    entry_points={
        "console_scripts": [
            "stat-folder = src.main:cli",
        ],
    },
)
