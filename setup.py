from setuptools import setup

setup(
    name='stat-folder',
    version='v1.0',
    install_requires=[
        'click',
    ],
    python_requires=">=3.10",
    entry_points={
        'console_scripts': [
            'stat-folder = main:cli',
        ],
    },
)