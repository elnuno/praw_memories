try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup
    def find_packages(exclude=None):
        return []

readme = '''
'''

with open('requirements.txt') as f:
        requirements = [line.strip() for line in f.read().splitlines() if
                        line.strip() and not line.strip().startswith('#')]

setup(
    name='praw_memories',
    version='0.0.1',
    description='HTTP caching and DB persistence for PRAW',
    long_description=readme,
    author="elnuno",
    url='https://github.com/elnuno/praw_memories',
    packages=find_packages(exclude=['docs']),
    package_dir={'praw_memories':
                 'praw_memories'},
    install_requires=requirements,
    include_package_data=True,
    license="Apache Software License 2.0",
    zip_safe=False,
    keywords='praw reddit cache sqlalchemy',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',
    ],
    test_suite='tests',
)
