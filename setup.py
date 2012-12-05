"""
decanter
========

A blogging framework based on Python-Flask.  The project is in it's infancy,
more details to come as things develop.

"""
import sys
import os
from setuptools import setup, find_packages

py = sys.version_info[:2]

if py > (2, 7) or py < (2, 5):
    raise RuntimeError('Python 2.5, 2.6 or 2.7 is required')

root = os.path.dirname(os.path.abspath(__file__))

README = os.path.join(root, 'README.rst')
if os.path.isfile(README):
    README = open(README).read()
else:
    README = None

version = '0.0.1'

install_requires = [
    'pytz==2012d',
    'PyYAML==3.10',
    'cement==2.0.2',
    'gunicorn==0.14.6',
    'yuicompressor==2.4.7',
    'itsdangerous==0.17',
    'flask==0.9',
    'flask-sqlalchemy==0.16',
    'flask-script==0.3.3',
    'flask-security==1.2.3',
    'flask-admin==1.0.2',
    'flask-assets',
    'flask-seasurf',
    'SQLAlchemy',
    'psycopg2==2.4.5',
]

tests_require = [
    'nose==1.1.2',
    'mock==0.8.0',
    'coverage==3.5.1',
    'flask-testing==0.3',
]

entry_points = dict()

setup(name='decanter',
      version=version,
      description="Blogging framework based on Python-Flask.",
      long_description=README,
      keywords='blog blogging vanity',
      author='Brian Oldfield',
      author_email='brian@oldfield.io',
      url='http://github.com/boldfield/decanter',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      extras_require={'tests': tests_require},
      install_requires=install_requires,
      entry_points=entry_points,
      classifiers=[
          # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'Topic :: Software Development',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Operating System :: OS Independent',
      ])
