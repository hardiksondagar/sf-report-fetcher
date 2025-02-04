import os
from setuptools import setup, find_packages

# Read version from version.py
about = {}
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "salesforce_report_fetcher", "version.py")) as f:
    exec(f.read(), about)

setup(
    name="sf-report-fetcher",
    version=about["VERSION"],
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
    ],
    python_requires=">=3.7",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
)