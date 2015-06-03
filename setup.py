"""
Install crossfit-registration.
"""
import os

from setuptools import setup

import crossfit_registration


setup(
    name='crossfit-registration',
    version=crossfit_registration.__version__,

    author=crossfit_registration.__author__,
    author_email=crossfit_registration.__email__,
    url=crossfit_registration.__url__,

    license=crossfit_registration.__license__,
    platforms='any',
    description="Carefree WOD subscriptions.",
    long_description=open(os.path.join('README.md')).read(),
    keywords='crossfit, registration, wod',

    zip_safe=False,

    install_requires=[
        'requests==2.7.0',
        'beautifulsoup4==4.3.2',
    ],
    entry_points={
        'console_scripts': [
            'crossfit-registration=crossfit_registration.scripts.registration:cmdline'
        ]
    }
)
