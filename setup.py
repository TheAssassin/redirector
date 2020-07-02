from setuptools import find_packages, setup

tests_require=[
    "tox",
    "pytest",
]


setup(
    name="redirector",
    packages=find_packages(),
    install_requires=[
        "Flask>=1.1",
        "Flask-Caching",
        "requests",
        "cssselect",
        "lxml",
    ],
    tests_require=tests_require,
    extras_require={
        "test": tests_require,
    },
)
