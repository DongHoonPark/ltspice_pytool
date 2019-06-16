from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
  name = 'ltspice',         # How you named your package folder (MyLib)
  packages = ['ltspice'],   # Chose the same as "name"
  version = '0.3.2',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'DESC',   # Give a short description about your library
  long_description=long_description,
  long_description_content_type="text/markdown",
  url='https://github.com/DongHoonPark/ltspice_pytool',
  author = 'DonghoonPark',                   # Type in your name
  author_email = 'donghun94@snu.ac.kr',      # Type in your E-Mail
  download_url = 'https://pypi.org/project/ltspice',
  keywords = ['ltspice', 'multi point simulation'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
          'numpy',
      ],
  classifiers=[
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
)