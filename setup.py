from setuptools import find_packages, setup
import codecs
import os

VERSION = '0.0.3'
DESCRIPTION = 'Umshini Client API'

setup(
    name='umshini',
    version=VERSION,
    author='umshini team',
    author_email="j.k.terry@swarmlabs.com",
    description=DESCRIPTION,
    url='https://github.com/umshini/umshini',
    #long_description=long_description,
    #long_description_content_type="text/markdown",
    #keywords=["Reinforcement Learning", "game", "RL", "AI", "gym"],
    #python_requires=">=3.6, <3.10",
    #data_files=[("", ["LICENSE.txt"])],
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'colorama',
        'pettingzoo==1.22.2',
        'supersuit==3.7.0',
        'gymnasium',
        'numpy',
        'halo',
    ],
    extras_require={
        "atari": ['pettingzoo[atari]==1.22.2'],
        "classic": ['pettingzoo[classic]==1.22.2'],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ]
)
