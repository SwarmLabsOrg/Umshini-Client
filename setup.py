from setuptools import find_packages, setup
from setuptools.command.install import install
from setuptools.command.develop import develop
from Cython.Build import cythonize
import numpy as np
import atexit
from subprocess import check_call


class PostDevelopCommand(develop):
    """Post-installation for development mode."""
    def run(self):
        print("pre develop")
        develop.run(self)
        # PUT YOUR POST-INSTALL SCRIPT HERE or CALL A FUNCTION
        check_call("AutoROM --accept-license".split())
        print("post develop")


class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        print("pre install")
        install.run(self)
        # PUT YOUR POST-INSTALL SCRIPT HERE or CALL A FUNCTION
        check_call("AutoROM --accept-license".split())
        print("post install")


VERSION = '0.0.1'
DESCRIPTION = 'Umshini Client API'
with open("README.md", 'r') as f:
    long_description = f.read()

setup(
    cmdclass={
        'develop': PostDevelopCommand,
        'install': PostInstallCommand,
    },
    name='umshini',
    version=VERSION,
    author='umshini team',
    author_email="justinkterry@gmail.com",
    description=DESCRIPTION,
    url='umshini.ml',
    long_description=long_description,
    #long_description_content_type="text/markdown",
    #keywords=["Reinforcement Learning", "game", "RL", "AI", "gym"],
    #python_requires=">=3.6, <3.10",
    #data_files=[("", ["LICENSE.txt"])],
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Cython',
        'colorama',
        'pettingzoo[atari,classic]==1.22.3',
        'supersuit==3.7.1',
        'autorom[accept-rom-license]',
        'gymnasium',
        'numpy',
        'halo',
    ],
    setup_requires=[
        'Cython',
        'colorama',
        'pettingzoo[atari,classic]==1.22.3',
        'supersuit==3.7.1',
        'autorom[accept-rom-license]',
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
