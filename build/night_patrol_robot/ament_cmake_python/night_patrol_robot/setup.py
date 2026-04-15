from setuptools import find_packages
from setuptools import setup

setup(
    name='night_patrol_robot',
    version='0.1.0',
    packages=find_packages(
        include=('night_patrol_robot', 'night_patrol_robot.*')),
)
