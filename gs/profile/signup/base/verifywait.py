# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright © 2013 OnlineGroups.net and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
from __future__ import absolute_import
from zope.cachedescriptors.property import Lazy
from zope.component import createObject
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from gs.group.member.invite.base.queries import InvitationQuery
from gs.group.member.join.interfaces import IGSJoiningUser
from gs.profile.invite.invitation import Invitation
from Products.XWFCore.XWFUtils import get_support_email,\
    get_the_actual_instance_from_zope
from Products.CustomUserFolder.interfaces import IGSUserInfo
from gs.profile.email.base.emailaddress import address_exists
from gs.profile.email.base.emailuser import EmailUser
from gs.content.form import SiteForm
from .interfaces import IGSVerifyWait
import logging
log = logging.getLogger('gs.profile.signup.base')


class VerifyWaitForm(SiteForm):
    label = u'Awaiting Verification'
    pageTemplateFileName = 'browser/templates/verify_wait.pt'
    template = ZopeTwoPageTemplateFile(pageTemplateFileName)
    form_fields = form.Fields(IGSVerifyWait)

    def __init__(self, context, request):
        SiteForm.__init__(self, context, request)

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

    @form.action(label=u'Finish', failure='handle_set_action_failure')
    def handle_set(self, action, data):

        self.join_groups()

        uri = str(data.get('came_from'))
        if uri == 'None':
            uri = '/'
        uri = '%s?welcome=1' % uri
        return self.request.RESPONSE.redirect(uri)

    def handle_set_action_failure(self, action, data, errors):
        if len(errors) == 1:
            self.status = u'<p>There is an error:</p>'
        else:
            self.status = u'<p>There are errors:</p>'

    @form.action(label=u'Send', failure='handle_set_action_failure')
    def handle_send(self, action, data):
        assert data
        assert 'email' in data.keys()
        self.actual_handle_send(data)
        assert self.status
        assert type(self.status) == unicode

    def actual_handle_send(self, data):
        newEmail = data['email']
        if address_exists(self.context, newEmail):
            if newEmail in self.userEmail:
                # TODO: Audit
                m = 'GSVerifyWait: Resending verification message to ' \
                  '<%s> for the user "%s"' % (newEmail, self.context.getId())
                log.info(m)

                eu = createObject('groupserver.EmailVerificationUserFromEmail',
                                  self.context, newEmail)
                eu.send_verification(self.request)
                self.status = u'''Another email address verification
                  message has been sent to
                  <code class="email">%s</code>.''' % newEmail
            else:
                # TODO: Audit
                m = 'GSVerifyWait: Attempt to use another email address ' \
                  '<%s> by the user "%s"' % (newEmail, self.context.getId())
                log.info(m)

                self.status = u'''The address
                  <code class="email">%s</code> is already registered
                  to another user.''' % newEmail
        else:  # The address does not exist
            oldEmail = self.remove_old_email()
            self.add_new_email(newEmail)
            self.status = u'''Changed your email address from
              <code class="email">%s</code> to
              <code class="email">%s</code>.''' % (oldEmail, newEmail)

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
        invs = query.get_current_invitiations_for_site(self.siteInfo.id,
                self.userInfo.id)
        invitations = [Invitation(self.ctx, i['invitation_id'])
                        for i in invs]
        joiningUser = IGSJoiningUser(self.userInfo)
        for invite in invitations:
            joiningUser.join(invite.groupInfo)
            invite.accept()
