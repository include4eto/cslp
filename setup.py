#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
	name='CSLP',
	version='0.1',
	description='CSLP coursework',
	author='Traiko Dinev',
	author_email='s1448355@sms.ed.ac.uk',
	packages=find_packages(exclude=('tests', 'doc')),
	install_requires=['numpy', 'nose']
)