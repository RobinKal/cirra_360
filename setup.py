from setuptools import setup, find_packages


with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in cirra_360/__init__.py
from cirra_360 import __version__ as version

setup(
	name="cirra_360",
	version=version,
	description="cirra_360",
	author="sujay",
	author_email="sujay.j@tacten.co",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
