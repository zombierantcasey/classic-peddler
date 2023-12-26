from setuptools import setup

setup(
    name="peddler",
    version="0.1.0",
    author="Pierre MacKay",
    author_email="mail@pierremackay.com",
    install_requires=["mysql-connector-python"],
    entry_points={"console_scripts": ["peddler = peddler.__main__:main"]},
)
