from setuptools import setup, find_packages

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

# get version from __version__ variable in plant_manager/__init__.py
from plant_manager import __version__ as version

setup(
    name="plant_manager",
    version=version,
    description="Plant Management System for ERPNext",
    author="AI Agent",
    author_email="ai@example.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires
)