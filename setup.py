# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages
from version import get_version

version = get_version()

setup(name='gs.profile.signup.base',
    version=version,
    description="The profile pages that are required for user-initiated"
        "sign up (registration)",
    long_description=open("README.txt").read() + "\n" +
                    open(os.path.join("docs", "HISTORY.txt")).read(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        "Environment :: Web Environment",
        "Framework :: Zope2",
        "Intended Audience :: Developers",
        'License :: OSI Approved :: Zope Public License',
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux"
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords='sign up, registration, profile, user, join',
    author='Michael JasonSmith',
    author_email='mpj17@onlinegroups.net',
    url='http://groupserver.org',
    license='ZPL 2.1',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['gs', 'gs.profile', 'gs.profile.signup'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'zope.app.apidoc',
        'zope.cachedescriptors',
        'zope.component',
        'zope.contentprovider',
        'zope.formlib',
        'zope.interface',
        'zope.pagetemplate',
        'zope.publisher',
        'zope.schema',
        'zope.viewlet',
        'Zope2',
        'gs.content.base',
        'gs.content.form',
        'gs.group.member.invite.base',
        'gs.group.member.join',
        'gs.help',  # For the help viewlet
        'gs.profile.email.base',
        'gs.profile.email.verify',
        'gs.profile.invite',
        'gs.profile.password',
        'gs.viewlet',
        'Products.CustomUserFolder',
        'Products.GSAuditTrail',
        'Products.GSProfile',
        'Products.XWFCore',
    ],
    entry_points="""
    # -*- Entry points: -*-
    """,
)
