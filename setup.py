from setuptools import setup, find_packages

with open("README.md") as f:
    long_description = f.read()

setup(
    name="folder-sync-cli",
    version="1.1.5",
    packages=find_packages(),
    install_requires=["click"],
    description="A CLI tool to simplify rclone sync.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Heng-Tse Chou",
    author_email="hengtse.me@gmail.com",
    url="https://github.com/hank-chouu/folder-sync-cli",
    license="MIT",
    keywords="rclone CLI",
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 3 - Alpha",
        # Indicate who your project is intended for
        "Intended Audience :: End Users/Desktop",
        "Operating System :: Unix",
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        "Programming Language :: Python :: 3",
    ],
    entry_points={
        "console_scripts": [
            "folder-sync = folder_sync.main:cli",
        ],
    },
)
