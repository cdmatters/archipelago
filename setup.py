from setuptools import setup

setup(name='archipelago',
      version='0.1',
      description='a tool for accessing publically available UK Government data on Members of Parliament (MPs)',
      url='https://github.com/condnsdmatters/archipelago',
      author='Eric Hambro',
      author_email='ehambro@gmail.com',
      license='MIT',
      packages=['archipelago'],
      install_requires=['requests', 'lxml', 'tqdm'],
      zip_safe=False,
      test_suite='nose.collector',
      tests_require=['nose']     
     )
