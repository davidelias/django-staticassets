import os
import codecs
from setuptools import setup

README = codecs.open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-staticassets',
    version='0.1',
    packages=['staticassets'],
    include_package_data=True,
    license='MIT License',
    description='Compiles and bundles static assets. Uses a directive processor similiar to Ruby\'s Sprockets',
    long_description=README,
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
