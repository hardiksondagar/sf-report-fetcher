import os
import re
from setuptools import setup

def get_version():
    """Read version directly from version.py"""
    version_file = os.path.join(
        os.path.dirname(__file__),
        'salesforce_report_fetcher',
        'version.py'
    )
    with open(version_file, 'r') as f:
        version_match = re.search(r"VERSION = ['\"]([^'\"]*)['\"]", f.read())
        if version_match:
            return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

setup(
    name="sf-report-fetcher",
    version=get_version(),
    packages=["salesforce_report_fetcher"],
    install_requires=[
        "requests>=2.22.0,<3.0.0",
    ],
    python_requires=">=3.7",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
)