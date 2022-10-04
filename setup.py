from setuptools import setup, find_packages

#Refer https://packaging.python.org/tutorials/packaging-projects/ for distribution

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
  name = 'ltspice',         # How you named your package folder (MyLib)
  packages = ['ltspice'],   # Chose the same as "name"
  version = '1.0.5',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'DESC',   # Give a short description about your library
  long_description=long_description,
  long_description_content_type="text/markdown",
  url='https://github.com/DongHoonPark/ltspice_pytool',
  author = 'DonghoonPark',                   # Type in your name
  author_email = 'donghun94@snu.ac.kr',      # Type in your E-Mail
  download_url = 'https://pypi.org/project/ltspice',
  keywords = ['ltspice', 'circuit data analysis', 'multi point simulation'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
          'numpy','deprecated', 'matplotlib',
          'typing_extensions; python_version < "3.8.0"'
      ],
  classifiers=[
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
  ],
)
