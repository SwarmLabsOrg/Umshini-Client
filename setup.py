from setuptools import find_packages, setup
import codecs
import os

VERSION = '0.0.1'
DESCRIPTION = 'Umshini Client API'

setup(
    name='umshini',
    version=VERSION,
    author='umshini team',
    author_email="justinkterry@gmail.com",
    description=DESCRIPTION,
    url='umshini.ml',
    #long_description=long_description,
    #long_description_content_type="text/markdown",
    #keywords=["Reinforcement Learning", "game", "RL", "AI", "gym"],
    #python_requires=">=3.6, <3.10",
    #data_files=[("", ["LICENSE.txt"])],
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'colorama',
        'pettingzoo[atari,classic]==1.22.2',
        'supersuit==3.7.0',
        'gymnasium',
        'numpy',
        'halo',
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ]
)
