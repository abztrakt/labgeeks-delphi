from setuptools import setup

setup(
    name = 'labgeeks-delphi',
    version = '1.0',
    license = 'Apache',
    url = 'http://github.com/abztrakt/labgeeks_delphi',
    description = 'The knowledge base app in the labgeeks suite of student staff management tools.',
    author = 'Craig Stimmel',
    packages = ['labgeeks_delphi',],
    install_requires = [
        'setuptools',
        'labgeeks-sybil',
        'South==0.7.3',
        'Markdown==2.2.0',
    ],
)
