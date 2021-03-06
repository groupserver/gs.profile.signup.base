# -*- coding: utf-8 -*-
############################################################################
#
# Copyright © 2014, 2015 OnlineGroups.net and Contributors.
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
import logging
log = logging.getLogger('gs.profile.signup.base')
from zope.component import createObject
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from Products.XWFCore.XWFUtils import get_support_email
from Products.GSProfile.utils import login, create_user_from_email
from gs.content.form.base import SiteForm
from gs.profile.email.base import (NewEmailAddress, EmailAddressExists,
                                   sanitise_address)
from gs.profile.email.verify.emailverificationuser import \
    EmailVerificationUser
from Products.GSProfile.profileaudit import *  # lint:ok
from Products.GSAuditTrail.queries import AuditQuery
from gs.profile.password.audit import SET, \
    SUBSYSTEM as GS_PROFILE_PASSWORD_SUBSYSTEM
from .interfaces import IGSRequestRegistration
from . import GSMessageFactory as _


class RequestRegistrationForm(SiteForm):
    form_fields = form.Fields(IGSRequestRegistration)
    label = _('register-page-label', 'Register')
    pageTemplateFileName = 'browser/templates/signup.pt'
    template = ZopeTwoPageTemplateFile(pageTemplateFileName)

    def __init__(self, context, request):
        super(RequestRegistrationForm, self).__init__(context, request)
        self.groupsInfo = createObject('groupserver.GroupsInfo', context)

        self.groupInfo = None
        if 'form.groupId' in request.form:
            gId = request.form['form.groupId']
            if gId in self.groupsInfo.get_visible_group_ids():
                self.groupInfo = createObject('groupserver.GroupInfo',
                                              context, gId)

        # handle errors from other signup methods where the user has already
        # been registered wih a given email address
        if 'email' in request.form:
            try:
                nextPage = self.next_page_from_email(request.form['email'])
                self.status = nextPage.message
                self.errors = []
            except:
                m = "Passed an email {0}, but an error occurred while "\
                    "processing it.".format(request.form['email'])
                log.error(m)

    @property
    def verificationEmailAddress(self):
        retval = get_support_email(self.context, self.siteInfo.id)
        assert type(retval) in (str, unicode)
        assert '@' in retval
        return retval

    def validate(self, action, data):
        return (form.getWidgetsData(self.widgets, self.prefix, data) +
                form.checkInvariants(self.form_fields, data))

    # --=mpj17=--
    # The "form.action" decorator creates an action instance, with
    #   "handle_reset" set to the success handler,
    #   "handle_reset_action_failure" as the failure handler, and adds the
    #   action to the "actions" instance variable (creating it if
    #   necessary). I did not need to explicitly state the label, but it
    #   helps with readability.
    @form.action(label=_('register-button', 'Register'), name='register',
                 failure='handle_register_action_failure',
                 validator='validate')
    def handle_register(self, action, data):
        assert self.form_fields
        assert action
        assert data

        email = sanitise_address(data['email'])
        emailChecker = NewEmailAddress(title='Email')
        emailChecker.context = self.context  # --=mpj17=-- Legit? Works!
        try:
            emailChecker.validate(email)
        except EmailAddressExists, e:
            logMsg = 'RequestRegistrationForm: Registration attempted '\
                     'with existing address <{}>\n{}'.format(email, e)
            log.info(logMsg)

            nextPage = self.next_page_from_email(email)

            if nextPage.systemLoginRequired:
                acl_users = self.context.acl_users
                user = acl_users.get_userByEmail(email)
                login(self.context, user)
            if nextPage.uri:
                uri = '%s%s' % (nextPage.uri, self.get_uri_end(data))
                return self.request.RESPONSE.redirect(uri)
            else:
                # Display a message
                self.status = nextPage.message
                self.errors = []
        else:  # The address does not exist!
            userInfo = self.createUser(email)

            uri = '%s/register_password.html%s' % \
                (userInfo.url, self.get_uri_end(data))

            return self.request.RESPONSE.redirect(uri)

    def handle_register_action_failure(self, action, data, errors):
        if len(errors) == 1:
            s = _('single-error', 'There is an error:')
        else:
            s = _('multiple-errors', 'There are errors:')
        self.status = '<p>{0}</p>'.format(s)

    def next_page_from_email(self, email):
        '''Figure out the next page for the existing user

Description
-----------

If the user exists there are a number of possibilities where he or she
should go next, depending on the user's state

    * *Sign Up* page has been completed but the *Set Password* page has
      not.

        + Send the member to the *Set Password* page.

    * The *Set Password* page has been completed, but the *Change
      Profile* page has not.

        + Send the member to the *Change Profile* page (requires login).

    * The *Change Profile* page has been completed, but the *Await
      Verification* page has not.

        + Send the member to the *Await Verification* page (requires login).

    * Sign up has been finished, so there are three possible options
      to present to the user:

        + Login,
        + Sign up using a different email address, or
        + Reset the password.

Returns
-------

A ``NextPageInfo`` containing
    * The link to the new page, if needed,
    * A message, if needed,
    * A flag to say if the user should be automatically logged in
      by the system, or not.

Side Effects
------------

None.'''
        uri = ''
        m = ''
        systemLoginRequired = False

        emailUser = createObject('groupserver.EmailUserFromEmailAddress',
                                 self.context, email)
        userInfo = emailUser.userInfo

        # Checks for incomplete sign up.
        changedProfile = email.split('@')[0] != userInfo.name
        verified = emailUser.get_verified_addresses() != []

        if not password_set(self.context, userInfo.user):
            # Go to the Set Password page. This is no worse than
            # someone just registering with someone else's email
            # address. (That is, pointless as the address cannot be
            # verified).
            uri = '%s/register_password.html' % userInfo.url
            systemLoginRequired = True
        elif not changedProfile:
            # The password has been set, but the profile has not
            #   been changed.
            uri = '%s/registration_profile.html' % userInfo.url
        elif not verified:
            uri = '%s/verify_wait.html' % userInfo.url
        else:  # set password, changed profile, and verified
            d = {
                'email': email,
                'site': self.siteInfo.name,
                'resetUrl': 'reset_password.html?form.email=%s' % email,
                'loginUrl': '/login.html',
            }
            m = '''A user with the email address
                <code class="email">%(email)s</code> already exists on
                <span class="site">%(site)s</span>. Either
                <ul>
                  <li><a href="%(resetUrl)s"><strong>Reset</strong> your
                      password,</a></li>
                  <li><a href="%(loginUrl)s"><strong>Login,</strong></a>
                  <li><strong>Register</strong> with another email
                    address.</li>
                </ul>''' % d

        retval = NextPageInfo(uri, m, systemLoginRequired)
        assert isinstance(retval, NextPageInfo)
        return retval

    def createUser(self, email):
        '''Create a new user instance from the email address

Arguments
---------

``email``   The email address of the new member.

Returns
-------

A user-info for the new instance.

Side Effects
------------

    * Creates the new user instance.
    * Logs the new member in.
    * Sets the ``email`` to the member's primary email address.
    * Sets the member's ``fn`` to the left-hand side of ``email``.
    * Sends an address verification message to ``email``.'''
        user = create_user_from_email(self.context, email)
        userInfo = IGSUserInfo(user)
        login(self.context, user)

        auditer = ProfileAuditer(user)
        auditer.info(REGISTER, email)
        #   We want the user to be in the context of the site.
        #     It makes as much sense as the rest of aquisition.
        ctx = self.context.acl_users.getUser(userInfo.id)
        evu = EmailVerificationUser(ctx, userInfo, email)
        evu.send_verification(self.request)

        return userInfo

    def get_uri_end(self, data):
        '''Get the snippet of a URI that comes at the end of all redirects
        from this page.'''
        cf = unicode(data.get('came_from'))
        if cf == 'None':
            cf = ''
        gid = unicode(data.get('groupId'))
        if gid == 'None':
            gid = ''
        retval = '?form.groupId=%s&form.came_from=%s' % (gid, cf)
        return retval


class NextPageInfo(object):
    def __init__(self, uri='', message=u'', systemLoginRequired=False):
        self.uri = uri
        self.message = message
        self.systemLoginRequired = systemLoginRequired


def password_set(context, user):
    '''Check if a password has ever been set.

Description
-----------

We cannot check the password itself to see if the password is blank,
because it may be hashed in all sorts of ways, so a blank password
does no look blank. Instead this little method looks in the audit-trail
for a profile-event that corresponds to a member setting a password.

Arguments
---------

  * ``context``: The Zope context, which is used to find the data
    adapter.
  * ``user``: The GroupServer CustomUser instance that is to be checked.

Returns
-------

Boolean, True if a password has been set.

Side Effects
------------

None.

Acknowledgements
---------------

Thanks to Alice for suggesting that I trawl the audit-logs for the
set-password events.'''
    q = AuditQuery()
    items = q.get_instance_user_events(user.getId(), limit=128)
    setPasswordItems = [
        i for i in items
        if (((i['subsystem'] == SUBSYSTEM) and (i['code'] == SET_PASSWORD))
            or ((i['subsystem'] == GS_PROFILE_PASSWORD_SUBSYSTEM)
            and (i['code'] == SET)))]

    retval = bool(setPasswordItems)
    return retval
