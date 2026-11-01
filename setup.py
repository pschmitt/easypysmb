from setuptools import find_packages, setup

setup(
    name="easypysmb",
    version="1.4.4",
    license="GPL3",
    description="Easy to use PySMB wrapper library",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    python_requires=">=3.13",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Programming Language :: Python :: 3.15",
    ],
    author="Philipp Schmitt",
    author_email="philipp@schmitt.co",
    url="https://github.com/pschmitt/easypysmb",
    packages=find_packages(),
    install_requires=["pysmb"],
)
