from setuptools import setup, find_packages

with open('requirements.txt') as f:
	install_requires = f.read().strip().split('\n')

# get version from __version__ variable in elite_core/__init__.py
from elite_core import __version__ as version

setup(
	name='elite_core',
	version=version,
	description='Frappe Framework extensions by Elite Business',
	author='Elite Business',
	author_email='support@doxerp.com',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
