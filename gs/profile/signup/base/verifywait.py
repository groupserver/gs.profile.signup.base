# -*- coding: utf-8 -*-
############################################################################
#
# Copyright © 2013, 2015 OnlineGroups.net and Contributors.
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
from urlparse import urlparse
from zope.cachedescriptors.property import Lazy
from zope.component import createObject
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from gs.content.form.base import SiteForm
from gs.group.member.invite.base.queries import InvitationQuery
from gs.profile.email.base.emailaddress import address_exists
from gs.profile.email.base.emailuser import EmailUser
from gs.profile.invite.invitation import Invitation
from Products.CustomUserFolder.interfaces import IGSUserInfo
from Products.XWFCore.XWFUtils import get_support_email,\
    get_the_actual_instance_from_zope
from .interfaces import IGSVerifyWait
from .utils import join_group
from . import GSMessageFactory as _


class VerifyWaitForm(SiteForm):
    label = _('verify-wait-label', 'Awaiting Verification')
    pageTemplateFileName = 'browser/templates/verify_wait.pt'
    template = ZopeTwoPageTemplateFile(pageTemplateFileName)
    form_fields = form.Fields(IGSVerifyWait)

    def __init__(self, context, request):
        super(VerifyWaitForm, self).__init__(context, request)

    def setUpWidgets(self, ignore_request=False):
        data = {'email': self.userEmail[0], }

        self.widgets = form.setUpWidgets(
            self.form_fields, self.prefix, self.context,
            self.request, form=self, data=data,
            ignore_request=ignore_request)
        assert self.widgets

    @property
    def ctx(self):
        return get_the_actual_instance_from_zope(self.context)

    @Lazy
    def userInfo(self):
        retval = IGSUserInfo(self.ctx)
        assert retval
        return retval

    @Lazy
    def emailUser(self):
        retval = EmailUser(self.context, self.userInfo)
        assert retval
        return retval

    @property
    def verificationEmailAddress(self):
        retval = get_support_email(self.context, self.siteInfo.id)
        assert type(retval) == str
        assert '@' in retval
        return retval

    @form.action(label=_('verify-wait-button', 'Finish'), name='finish',
                 failure='handle_set_action_failure')
    def handle_set(self, action, data):

        self.join_groups()

        cameFrom = str(data.get('came_from'))
        cameFrom = cameFrom if cameFrom != 'None' else '/'
        parsedCameFrom = urlparse(cameFrom)
        uri = '{0}?welcome=1'.format(parsedCameFrom.path)
        return self.request.RESPONSE.redirect(uri)

    def handle_set_action_failure(self, action, data, errors):
        if len(errors) == 1:
            s = _('single-error', 'There is an error:')
        else:
            s = _('multiple-errors', 'There are errors:')
        self.status = '<p>{0}</p>'.format(s)

    @form.action(label=u'Send', failure='handle_set_action_failure')
    def handle_send(self, action, data):
        assert data
        assert 'email' in data.keys()
        self.actual_handle_send(data)
        assert self.status

    def actual_handle_send(self, data):
        newEmail = data['email']
        xmlEmail = '<code class="email">%s</code>.' % newEmail
        if address_exists(self.context, newEmail):
            if newEmail in self.userEmail:
                # TODO: Audit
                m = 'GSVerifyWait: Resending verification message to ' \
                    '<%s> for the user "%s"' % (newEmail,
                                                self.context.getId())
                log.info(m)

                eu = createObject(
                    'groupserver.EmailVerificationUserFromEmail',
                    self.context, newEmail)
                eu.send_verification(self.request)
                self.status = _(
                    'verify-wait-resend',
                    'Another email address verification message has been '
                    'sent to ${email}.',
                    mapping={'email': xmlEmail})
            else:
                # TODO: Audit
                m = 'GSVerifyWait: Attempt to use another email address ' \
                    '<%s> by the user "%s"' % (newEmail,
                                               self.context.getId())
                log.info(m)

                self.status = _(
                    'verify-wait-existing-email',
                    'The address ${email} is already registered to another '
                    'user.',
                    mapping={'email': xmlEmail})
        else:  # The address does not exist
            oldEmail = self.remove_old_email()
            self.add_new_email(newEmail)
            oldXMLEmail = '<code class="email">%s</code>.' % (oldEmail)
            self.status = _(
                'verify-wait-address-change',
                'Changed your email address to ${newEmail} from '
                '${oldEmail}.',
                mapping={'newEmail': xmlEmail, 'oldEmail': oldXMLEmail})

    def remove_old_email(self):
        oldEmail = self.userEmail[0]
        self.emailUser.remove_address(oldEmail)
        assert oldEmail not in self.emailUser.get_addresses()
        return oldEmail

    def add_new_email(self, email):
        self.emailUser.add_address(email, isPreferred=True)
        eu = createObject('groupserver.EmailVerificationUserFromEmail',
                          self.context, email)
        eu.send_verification(self.request)
        assert email in self.emailUser.get_addresses()
        return email

    @property
    def userEmail(self):
        retval = self.emailUser.get_addresses()
        assert retval
        return retval

    def join_groups(self):
        # --=mpj17=-- This may seem a bit mad, but there is method to my
        #   madness. We have to join the groups *after* verifying the
        #   email address, otherwise the new group member will never get
        #   the Welcome email from the group
        #   <https://projects.iopen.net/groupserver/ticket/303>.
        # The way I record groups that the new member is about to join
        #   is with *invitations*. The user indicates that he or she
        #   wants to join a group on the previous Change Profile page.
        #   There I create a heap of invitations: from the user to the
        #   user. Here I pick the invitations up and actually join the
        #   groups, sending the Welcome message as a side effect.
        query = InvitationQuery()
        # The user should only have invitations that he or she has
        #   issued, as the user is brand new. *Should*  being the
        #   right word here. I hope this does not bite me\ldots
        # One odd side-effect of hacking on top of Invites is that it
        #   deals with a corner case of a person being invited then
        #   requesting membership.
        invs = query.get_current_invitiations_for_site(
            self.siteInfo.id, self.userInfo.id)
        invitations = [Invitation(self.ctx, i['invitation_id'])
                       for i in invs]
        for invite in invitations:
            invite.accept()
            join_group(self.userInfo, invite.groupInfo, self.request)
