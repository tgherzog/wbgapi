
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="wbgapi",
    version="0.1.0a10",
    author="Tim Herzog",
    # author_email="author@example.com",
    description="wbgapi provides a comprehensive interface to the World Bank's daeta and metadata APIs",
    license='MIT',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tgherzog/wbgapi",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
    ],
    install_requires=['requests', 'PyYAML', 'tabulate'],
    python_requires='>=3.0',
)
