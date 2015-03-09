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
from zope.component import createObject
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from Products.CustomUserFolder.userinfo import GSUserInfo
from gs.content.form.base import SiteForm
from gs.profile.email.base.emailuser import EmailUser
from gs.profile.password.interfaces import IGSPasswordUser
from .interfaces import IGSSetPasswordRegister
from . import GSMessageFactory as _


class SetPasswordForm(SiteForm):
    form_fields = form.Fields(IGSSetPasswordRegister)
    label = _('set-password-label', 'Set password')
    pageTemplateFileName = 'browser/templates/setpassword.pt'
    template = ZopeTwoPageTemplateFile(pageTemplateFileName)

    def __init__(self, context, request):
        SiteForm.__init__(self, context, request)
        self.userInfo = GSUserInfo(context)
        self.emailUser = EmailUser(context, self.userInfo)

    @form.action(label=_('set-password-button', 'Set'), name='set',
                 failure='handle_set_action_failure')
    def handle_set(self, action, data):
        assert self.context
        assert self.form_fields
        assert action
        assert data

        pu = IGSPasswordUser(self.userInfo)
        pu.set_password(data['password1'])

        userInfo = createObject('groupserver.LoggedInUser', self.context)
        uri = '%s/registration_profile.html' % userInfo.url
        cf = str(data.get('came_from'))
        if cf == 'None':
            cf = ''
        gid = str(data.get('groupId'))
        if gid == 'None':
            gid = ''
        uri = '%s?form.joinable_groups:list=%s&form.came_from=%s' %\
            (uri, gid, cf)
        return self.request.RESPONSE.redirect(uri)

    def handle_set_action_failure(self, action, data, errors):
        if len(errors) == 1:
            s = _('single-error', 'There is an error:')
        else:
            s = _('multiple-errors', 'There are errors:')
        self.status = '<p>{0}</p>'.format(s)

    @property
    def userEmail(self):
        retval = self.emailUser.get_addresses()
        assert retval
        return retval
