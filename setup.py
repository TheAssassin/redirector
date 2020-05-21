from setuptools import find_packages, setup

setup(
    name="redirector",
    packages=find_packages(),
    install_requires=[
        "Flask>=1.1"
    ],
)
