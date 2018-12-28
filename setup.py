from setuptools import setup, find_packages

setup(
    name             = 'ltspice',
    version          = '0.1',
    description      = 'ltspice python analysis tool',
    author           = 'Donghoon Park',
    author_email     = 'donghun94@gmail.com',
    install_requires = [numpy],
    packages         = find_packages(exclude = ['docs', 'tests*']),
    keywords         = ['ltspice'],
    python_requires  = '>=3',
    package_data     =  {},
    zip_safe=False,
    classifiers      = [
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ]
)
