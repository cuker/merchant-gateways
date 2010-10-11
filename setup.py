from setuptools import setup, find_packages

setup(
    name = "merchant_gateways",  #  TODO  merchant-gateways ?
    version = "0.0.1",
    author = "Cuker Interactive",
    author_email = "TODO@morethanseven.net",
    url = "http://github.com/cuker/merchant_gateways/",

    packages = find_packages('lib'),
    package_dir = {'':'lib'},
    license = "MIT License",
    keywords = "django creditcard merchant authorization purchase",
    description = "Unifying the diversity of gateways into a common interface",
    install_requires=[
        'setuptools',
        'lxml'  #  TODO  what else?
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
)
