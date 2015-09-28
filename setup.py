import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="gpiozero",
    version="0.6.0",
    author="Ben Nuttall",
    description="A simple interface to everyday GPIO components used with Raspberry Pi",
    license="BSD",
    keywords=[
        "raspberrypi",
        "gpio",
    ],
    url="https://github.com/RPi-Distro/gpio-zero",
    packages=find_packages(),
    install_requires=[
        "RPi.GPIO",
        "w1thermsensor",
    ],
    long_description=read('README.rst'),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Intended Audience :: Developers",
        "Topic :: Education",
        "Topic :: System :: Hardware",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
    ],
)
