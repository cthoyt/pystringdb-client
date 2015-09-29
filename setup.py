from setuptools import setup

setup(name='pystringdb-client',
      version='0.1',
      description='Python client for STRING db',
      author='Jonathan Ronen',
      license='GPLv2',
      author_email='yableeatgmaildotcom',
      url='',
      packages=['pystringdb_client'],
      install_requires=[
          'pandas>=0.16.1',
          'six>=1.9.0',
          'requests>=2.7.0'
      ]
     )
