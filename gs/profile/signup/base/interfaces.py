# -*- coding: utf-8 -*-
############################################################################
#
# Copyright © 2013, 2014 OnlineGroups.net and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
############################################################################
from __future__ import absolute_import, unicode_literals
from zope.component import createObject
from zope.contentprovider.interfaces import IContentProvider
from zope.interface.interface import Interface
from zope.schema import ASCIILine, Text, URI, ValidationError
from zope.viewlet.interfaces import IViewletManager
from gs.core import to_ascii
from gs.profile.email.base.emailaddress import EmailAddress
from gs.profile.password.interfaces import ISetPassword
from . import GSMessageFactory as _


class IGSRequestRegistrationMarker(Interface):
    """Marker interface for the request registration page.
    """


class GroupIDNotFound(ValidationError):
    """Group identifier not found"""
    def __init__(self, value):
        self.value = value

    def __unicode__(self):
        retval = 'The group with the identifier %s is not in the '\
                 'list of visible groups.' % repr(self.value)
        return retval

    def __str__(self):
        retval = to_ascii(unicode(self))
        return retval

    def doc(self):
        return str(self)


class GroupID(ASCIILine):
    def constraint(self, value):
        groupsInfo = createObject('groupserver.GroupsInfo', self.context)
        groupIds = groupsInfo.get_visible_group_ids()
        if value not in groupIds:
            raise GroupIDNotFound(value)
        return True


class IGSRequestRegistration(Interface):
    """Schema use to define the user-interface that start the whole
    registration process"""
    # Unfortunately the group identifier is not checked against the
    #   joinable groups, because there is no "user" to check with.
    email = EmailAddress(
        title=('request-email-label', 'Email address'),
        description=_('request-email-help', 'Your email address.'),
        required=True)
    groupId = GroupID(
        title='Group identifier',
        description='The identifier for the group that you wish to join.',
        required=False)

    came_from = URI(
        title='Came from',
        description='The page to return to after registration has finished',
        required=False)


class IGSSetPasswordRegister(ISetPassword):
    groupId = GroupID(
        title='Group identifier',
        description='The identifier for the group that you wish to join.',
        required=False)

    came_from = URI(
        title='Came from',
        description='The page to return to after registration has finished',
        required=False)


# Change Profile is a bit special


class IGSResendVerification(Interface):
    """Schema use to define the user-interface that the user uses to
    resend his or her verification email, while in the middle of
    registration."""
    email = EmailAddress(
        title=_('resend-verification-label', 'Email address'),
        description=_('resend-verification-help',
                      'Your email address that you want to verify.'),
        required=True)


class IGSVerifyWait(Interface):
    """Schema use to define the user-interface presented while the user
    waits for verification of his or her email address."""
    email = EmailAddress(
        title=_('verify-wait-email-label', 'Email address'),
        description=_('verify-wait-email-help', 'Your email address.'),
        required=True)
    came_from = URI(
        title='Came from',
        description='The page to return to after registration has finished',
        required=False)


class IGSAwaitingVerificationJavaScriptContentProvider(IContentProvider):
    pageTemplateFileName = Text(
        title="Page Template File Name",
        description='The name of the ZPT file that is used to render the '
                    'javascript.',
        required=False,
        default="browser/templates/verify_wait_javascript.pt")

    email = EmailAddress(
        title='Email address',
        description='Your email address.',
        required=True)


class ISignupMethods(IViewletManager):
    '''A viewlet manager for the alternative signup methods '''
