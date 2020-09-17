from setuptools import setup

setup(
    name='covasim_australia',
    version='1.0.0',
    url='https://github.com/optimamodel/covasim-australia',
    install_requires=[
        'matplotlib>=3.0',
        'numpy>=1.10.1',
        'scipy>=1.2.1',
        'pandas',
        'xlsxwriter',
        'covasim',
        'sciris',
        'tqdm',
        'networkx',
    ],
)
