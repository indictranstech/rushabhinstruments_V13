from setuptools import setup, find_packages

with open('requirements.txt') as f:
	install_requires = f.read().strip().split('\n')

# get version from __version__ variable in instrument/__init__.py
from instrument import __version__ as version

setup(
	name='instrument',
	version=version,
	description='instrument',
	author='instrument',
	author_email='test@gmail.com',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
