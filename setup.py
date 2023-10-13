from setuptools import setup, find_packages

setup(
    name='stat-folder',
    version='v1.0',
    packages=find_packages(),
    install_requires=[
        'click',
    ],
    entry_points={
        'console_scripts': [
            'stat-folder = cli:main',
        ],
    },
)