import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "pysmtlib",
    version = "0.0.1-alpha",
    author = "Felipe Andres Manzano",
    author_email = "feliam@binamuse.com",
    description = ("A tool for symbolic execution of Intel 64 binaries."),
    requires =  ['' ],
    provides =  ['pysmtlib'],
    license = "BSD",
    url = 'http://github.com/pysmtlib',
    download_url= 'http://github.com/pysmtlib',
    platforms = ['linux', 'win32', 'win64'],
    keywords = "A python layer to interface with several SMTlIBv2 enabled SMT solvers",
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Testing"
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Quality Assurance",
    ],
    test_suite="test",
)


