import os
from setuptools import setup, find_packages

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-staticassets',
    version='0.2.0',
    packages=find_packages(exclude=['docs', 'tests']),
    include_package_data=True,
    license='MIT License',
    description='Compiles and bundles static assets. Uses a directive processor similiar to Ruby\'s Sprockets',
    long_description=open('README.rst').read(),
    url='https://github.com/davidelias/django-staticassets',
    author='David Elias',
    author_email='david@david-elias.net',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
