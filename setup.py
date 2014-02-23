from setuptools import setup
from os.path import join, dirname

execfile(join(dirname(__file__), 'YamlVariablesLibrary', 'version.py'))


setup(
    name='robotframework-YamlVariablesLibrary',
    version=VERSION,
    author='Jules Barnes',
    author_email='jules@julesbarnes.com',
    packages=['YamlVariablesLibrary', 'YamlVariablesLibrary.tests'],
    url='https://code.google.com/p/robotframework-YamlVariablesLibrary/',
    license='LICENSE.txt',
    description='Robot Framework Library allowing to variables stored in yaml files',
    long_description=open('README.txt').read(),
    install_requires = ['PyYAML >= 3.10'],
)