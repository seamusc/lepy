from setuptools import setup


with open('README.md', 'r') as f:
    long_description = f.read()


setup(
    name='r7insight_logsearch',
    version='0.0.1',
    author='Seamus Cawley',
    author_email='seamuscawley@gmail.com',
    packages=['r7insight_logsearch'],
    scripts=[],
    url='http://pypi.python.org/pypi/R7Insight-Logsearch/',
    license='LICENSE',
    description='Python API to the Rapid7 Insight Log Search API',
    long_description=long_description,
    install_requires=[
        'certifi==2018.4.16',
        'chardet==3.0.4',
        'idna==2.7',
        'progress==1.4',
        'python-dateutil==2.7.3',
        'requests==2.19.1',
        'six==1.11.0',
        'tabulate==0.8.2',
        'urllib3==1.23'
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2'
    ]
)
