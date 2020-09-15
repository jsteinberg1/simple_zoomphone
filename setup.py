import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="simple_zoomphone",
    version="0.0.1",
    author="Justin Steinberg",
    author_email="jsteinberg@gmail.com",
    install_requires=["requests", "PyJWT", "requests_oauthlib"],
    description="Opinionated REST api client for Zoom Phone.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jsteinberg1/simple_zoomphone",
    packages=["simple_zoomphone"],
    include_package_data=True,
    platforms="any",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU3 License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)