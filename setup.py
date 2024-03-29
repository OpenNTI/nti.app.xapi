import codecs
from setuptools import setup
from setuptools import find_packages

entry_points = {
    'console_scripts': [
        "nti_xapi_recorder = nti.app.xapi.scripts.nti_xapi_recorder:main",
    ],
}

TESTS_REQUIRE = [
    'nti.app.testing',
    'zope.dottedname',
    'zope.testrunner',
]


def _read(fname):
    with codecs.open(fname, encoding='utf-8') as f:
        return f.read()


setup(
    name='nti.app.xapi',
    version=_read('version.txt').strip(),
    author='Chris Utz',
    author_email='chris@nextthought.com',
    description="NTI xAPI Pyramid layer",
    long_description=(
        _read('README.rst')
        + '\n\n'
        + _read("CHANGES.rst")
    ),
    license='Apache',
    keywords='xAPI',
    classifiers=[
        'Framework :: Zope3',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    zip_safe=True,
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    namespace_packages=['nti', 'nti.app'],
    tests_require=TESTS_REQUIRE,
    install_requires=[
        'setuptools',
        'nti.app.asynchronous',
        'nti.asynchronous',
        'nti.common',
        'nti.coremetadata',
        'nti.dataserver',
        'nti.site',
        'nti.traversal',
        'nti.xapi',
        'pyramid',
        'pyramid-debugtoolbar',
        'zope.component',
        'zope.i18nmessageid',
        'zope.interface',
        'zope.location',
        'zope.security',
    ],
    extras_require={
        'test': TESTS_REQUIRE,
        'docs': [
            'Sphinx',
            'repoze.sphinx.autointerface',
            'sphinx_rtd_theme',
        ],
    },
    entry_points=entry_points,
)
