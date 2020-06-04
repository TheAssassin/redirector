from setuptools import find_packages, setup

tests_require=[
    "tox",
    "pytest",
    "lxml",
    "cssselect",
]


setup(
    name="redirector",
    packages=find_packages(),
    install_requires=[
        "Flask>=1.1",
        "Flask-Caching",
    ],
    tests_require=tests_require,
    extras_require={
        "test": tests_require,
    },
)
