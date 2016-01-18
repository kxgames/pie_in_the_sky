#!/usr/bin/env python3
# encoding: utf-8

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open('pie_in_the_sky/metadata.py') as metadata_file:
    exec(metadata_file.read())

with open('README.rst') as readme_file:
    readme = readme_file.read()

setup(
    name='pie_in_the_sky',
    version=__version__,
    author=__author__,
    author_email=__email__,
    description='Throw some pies!',
    long_description=readme,
    url='https://github.com/alexmitchell/pie_in_the_sky',
    packages=[
        'pie_in_the_sky',
    ],
    entry_points = {
        'console_scripts': [
            'pie_in_the_sky=pie_in_the_sky:main',
        ],
    },
    include_package_data=True,
    install_requires=[
        'kxg',
        'pymunk',
        'vecrec',
        'glooey',
        'nonstdlib',
    ],
    license='GPLv3',
    zip_safe=False,
    keywords=[
        'pie_in_the_sky',
        'game',
    ],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Games/Entertainment',
    ],
)
