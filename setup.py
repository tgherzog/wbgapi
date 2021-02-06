
import setuptools
import sys

from wbgapi.__version__ import __version__ as pkgVersion

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="wbgapi",
    version=pkgVersion,
    author="Tim Herzog",
    # author_email="author@example.com",
    description="wbgapi provides a comprehensive interface to the World Bank's data and metadata APIs",
    license='MIT',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tgherzog/wbgapi",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
    ],
    install_requires=['requests', 'PyYAML', 'tabulate'],
    python_requires='>=3.0',
)
