from setuptools import find_packages, setup

VERSION = '0.0.7'
DESCRIPTION = 'Umshini Client API'
with open("README.md", 'r') as f:
    long_description = f.read()

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
    python_requires=">=3.6, <3.11",
    #data_files=[("", ["LICENSE.txt"])],
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        ''
        'Cython',
        'colorama',
        'pettingzoo==1.23.0',
        'pettingzoo[classic]==1.23.0',
        'rlcard',
        'supersuit==3.8.0',
        'gymnasium',
        'numpy',
        'halo',
    ],
    extras_require={
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
