from setuptools import setup, find_packages # Always prefer setuptools over distutils
from codecs import open # To use a consistent encoding
from os import path

# Get the long description from the relevant file
with open('Readme.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='apt',
    description='command line package manager for Osgeo4w',
    version='0.3',
    url='https://github.com/maphew/arcplus/blob/master/setup.py',
    license='GPL',
    classifiers=[
        'Development Status :: 3 - Alpha',    
        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: GNU Public License',
        'Programming Language :: Python :: 2',
    ],
    keywords='osgeo4w package-manager installer',
    #py_modules=['apt','dapt'],
    #install_requires=['Click'],
    install_requires=['requests'],
    entry_points='''
        [console_scripts]
        apt = apt:__main__
        #dapt = dapt:main
        ''',
    zip_safe=False,
    )
