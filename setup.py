from setuptools import setup

def readme():
      with open('README.md') as f:
            return f.read()

setup(name='mindfulness_bot',
      version='0.1',
      description='a mindfulness bot for discord',
      url='http://github.com/PhilippRisius/MindfulnessBot',
      author='Travis Herrick',
      author_email='',
      license='MIT',
      packages=['MindfulnessBot'],
      zip_safe=False,
      test_suite='pytest',
      tests_require=['pytest'],
      install_requires=[
            'datetime',
            'python-dotenv',
            'discord.py',
            'pymongo',
      ],
      scripts=[],
      include_package_data=True
      )
