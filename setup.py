from setuptools import setup, find_packages
import sys, os

py = sys.version_info[:2]

if py > (2, 7) or py < (2,5):
    raise RuntimeError('Python 2.5, 2.6 or 2.7 is required')

root = os.path.dirname(os.path.abspath(__file__))

README = os.path.join(root, 'README.rst')
if os.path.isfile(README):
    README = open(README).read()
else:
    README = None

version = '0.0.1'

install_requires = [
    'Flask==0.9',
    'Flask-SQLAlchemy==0.16',
    'Flask-Testing==0.3',
    'Flask-Security==1.2.3',
    'SQLAlchemy==0.7.8',
    'pytz==2012d',
]

tests_require = [
    'nose==1.1.2',
    'mock==0.8.0',
    'coverage==3.5.1',
]

entry_points = dict()

setup(name='decanter',
      version=version,
      description="Blogging framework based on Python-Flask.",
      long_description=README,
      keywords='blog blogging vanity',
      author='Brian Oldfield',
      author_email='brian.oldfield@gmail.com',
      url='',
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
      ],
)
