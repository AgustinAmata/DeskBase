from setuptools import setup, find_packages
from os.path import join, dirname
setup(
    name='DeskBase',
    version='1.0',
    author="Agustin Amata",
    author_email="agus.amata2002@gmail.com",
    url="https://github.com/AgustinAmata/DeskBase.git",
    packages=find_packages(),
    long_description=open(join(dirname(__file__), 'README.md')).read(),
    install_requires=["customtkinter==5.2.2",
                     "mysql-connector-python==9.2.0",
                     "numpy==2.2.4",
                     "pandas==2.2.3"]
)
