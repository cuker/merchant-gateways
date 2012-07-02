from setuptools import setup, find_packages

if __name__ == '__main__':
    import sys, os
    if sys.argv.count('--xml'):
        sys.argv.remove('--xml')
        os.environ['XML_OUTPUT'] = 'True'

setup(
    name = "merchant-gateways",  #  TODO  merchant-gateways ?
    version = "0.0.1",
    author = "Cuker Interactive",
    author_email = "jasonk@cukerinteractive.com",
    url = "http://github.com/cuker/merchant-gateways/",

    packages = find_packages('lib'),
    package_dir = {'':'lib'},
    license = "MIT License",
    keywords = "django creditcard merchant authorization purchase",
    description = "Unifying the diversity of gateways into a common interface",
    install_requires=[
        'lxml',  #  TODO  what else?
        #python-money
    ],
    classifiers = [
        "Intended Audience :: Developers",  # TODO  do these!
        "License :: OSI Approved :: MIT License",
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Testing',
    ],
    test_suite='tests.testrunner.runtests',
    include_package_data = True,
)
