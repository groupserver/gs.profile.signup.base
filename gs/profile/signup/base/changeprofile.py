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
from urllib import urlencode
from urlparse import urlparse
from zope.app.apidoc.interface import getFieldsInOrder
from zope.cachedescriptors.property import Lazy
from zope.component import createObject
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from gs.content.form.base import select_widget, multi_check_box_widget
from gs.content.form.base.utils import enforce_schema
from gs.group.member.invite.base.inviter import Inviter
from gs.profile.email.base.emailuser import EmailUser
from Products.CustomUserFolder.interfaces import IGSUserInfo
from Products.GSProfile import interfaces
from Products.GSProfile.profileaudit import *  # lint:ok
from Products.GSProfile.edit_profile import (EditProfileForm,
                                             wym_editor_widget)
from Products.GSProfile.utils import profile_interface_name
from Products.XWFCore.XWFUtils import get_the_actual_instance_from_zope
from .utils import join_group
from . import GSMessageFactory as _


class ChangeProfileForm(EditProfileForm):
    """The Change Profile page used during registration is slightly
    different from the standard Change Profile page, as the user is able
    to join groups.
    """
    label = _('change-profile-page-title', 'Change profile')
    pageTemplateFileName = 'browser/templates/changeprofile.pt'
    template = ZopeTwoPageTemplateFile(pageTemplateFileName)

    def __init__(self, profile, request):
        super(ChangeProfileForm, self).__init__(profile, request)
        profileInterfaceName = profile_interface_name(profile)
        registerInterfaceName = '%sRegister' % profileInterfaceName

        self.profileInterface = getattr(interfaces, profileInterfaceName)
        self.registerInterface = interface = getattr(interfaces,
                                                     registerInterfaceName)
        enforce_schema(profile, interface)

        self.__hiddenFieldNames = ['form.came_from']

    @Lazy
    def form_fields(self):
        retval = form.Fields(self.registerInterface,
                             render_context=True)
        retval['tz'].custom_widget = select_widget
        retval['biography'].custom_widget = wym_editor_widget
        retval['joinable_groups'].custom_widget = multi_check_box_widget
        return retval

    def setUpWidgets(self, ignore_request=False):
        data = {'tz': self.get_timezone()}
        self.widgets = form.setUpWidgets(
            self.form_fields, self.prefix, self.context,
            self.request, form=self, data=data,
            ignore_request=ignore_request)

    def get_timezone(self):
        if self.request.form.get('form.tz', ''):
            retval = self.request.form['form.tz']
        else:
            gTz = siteTz = self.siteInfo.get_property('tz', 'UTC')
            joinableGroups = self.request.form.get('form.joinable_groups',
                                                   [])
            gIds = [i for i in joinableGroups
                    if i and i != 'None']
            # Zope Sux. For some reason, kept to itself, Zope gives me a
            #   Resource Not Found error when I try and create a
            #   GroupInfo instance. The instance *is* created ok, but it
            #   returns a Resource Not Found anyway. Being Zope,
            #   actually stating which resource could not be found is
            #   too hard, or too useful, so I am hacking around this.
            #   Someone should fix it after some heads have been nailed
            # to wardrobe doors.
            groups = getattr(self.siteInfo.siteObj, 'groups')

            gTzs = []
            for gId in gIds:
                if hasattr(groups, gId):
                    gTzs.append(getattr(groups, gId).getProperty('tz',
                                                                 siteTz))
            if gTzs:
                tzs = {}
                for tz in gTzs:
                    tzs[tz] = (tzs.get(tz, 0) + 1)
                assert len(tzs) > 0
                if len(tzs) == 1:
                    gTz = tzs.keys()[0]
                else:
                    gTz = siteTz
            retval = gTz
        assert retval
        return retval

    @Lazy
    def siteInfo(self):
        retval = createObject('groupserver.SiteInfo', self.ctx)
        return retval

    @Lazy
    def ctx(self):
        return get_the_actual_instance_from_zope(self.context)

    @Lazy
    def groupsInfo(self):
        retval = createObject('groupserver.GroupsInfo', self.ctx)
        return retval

    @Lazy
    def userInfo(self):
        retval = IGSUserInfo(self.ctx)
        assert retval
        return retval

    @Lazy
    def emailUser(self):
        retval = EmailUser(self.ctx, self.userInfo)
        return retval

    @property
    def userEmail(self):
        retval = self.emailUser.get_addresses()
        assert retval
        return retval

    @form.action(label=_('change-profile-button', 'Change'),
                 name='change', failure='handle_set_action_failure')
    def handle_set(self, action, data):
        self.auditer = ProfileAuditer(self.context)
        self.actual_handle_set(action, data)

        cf = str(data.pop('came_from'))
        cf = cf if cf != 'None' else ''
        if self.user_has_verified_email:
            parsedCameFrom = urlparse(cf)
            p = parsedCameFrom.path if cf else '/'
            uri = '{0}?welcome=1'.format(p)
        else:
            email = self.emailUser.get_addresses()[0]
            u = '{0}/verify_wait.html?{1}'
            d = {'form.email': email,
                 'form.came_from': cf}
            queryString = urlencode(d)
            uri = u.format(self.userInfo.url, queryString)

        return self.request.RESPONSE.redirect(uri)

    def handle_set_action_failure(self, action, data, errors):
        if len(errors) == 1:
            s = _('single-error', 'There is an error:')
        else:
            s = _('multiple-errors', 'There are errors:')
        self.status = '<p>{0}</p>'.format(s)

    def actual_handle_set(self, action, data):
        groupsToJoin = None
        if 'joinable_groups' in data.keys():
            groupsToJoin = data.pop('joinable_groups')

        fields = self.form_fields.omit('joinable_groups')
        for field in fields:
            field.interface = self.registerInterface
        form.applyChanges(self.context, fields, data)

        if groupsToJoin and self.user_has_verified_email:
            self.join_groups(groupsToJoin)
        elif groupsToJoin:
            self.invite_groups(groupsToJoin)

    @property
    def user_has_verified_email(self):
        email = self.emailUser.get_addresses()[0]
        retval = self.emailUser.is_address_verified(email)
        return retval

    def join_groups(self, groupsToJoin):
        for groupId in groupsToJoin:
            groupInfo = createObject('groupserver.GroupInfo',
                                     self.ctx, groupId)
            join_group(self.userInfo, groupInfo, self.request)

    def invite_groups(self, groupsToJoin):
        # --=mpj17=-- See the verifywait.VerifyWaitForm.join_groups
        #   method for the reason we do this.
        initial = True
        for groupId in groupsToJoin:
            groupInfo = createObject('groupserver.GroupInfo',
                                     self.ctx, groupId)
            # TODO: Create an inviter that is not so clunky. See
            #   IGSJoiningUser for a better pattern.
            inviter = Inviter(self.ctx, self.request,
                              self.userInfo, self.userInfo,
                              self.siteInfo, groupInfo)
            inviter.create_invitation({}, initial)
            initial = False

    @Lazy
    def profileWidgetNames(self):
        retval = ['form.%s' % f[0] for f in
                  getFieldsInOrder(self.profileInterface)]
        retval = [f for f in retval if f not in self.__hiddenFieldNames]
        assert type(retval) == list
        return retval

    @property
    def profileWidgets(self):
        widgets = [widget for widget in self.widgets
                   if widget.name in self.profileWidgetNames]
        return widgets

    @property
    def nonProfileWidgets(self):
        pw = self.profileWidgetNames + self.__hiddenFieldNames
        widgets = [widget for widget in self.widgets
                   if widget.name not in pw]
        return widgets

    @property
    def hiddenWidgets(self):
        widgets = [widget for widget in self.widgets
                   if widget.name in self.__hiddenFieldNames]
        return widgets

    @property
    def requiredProfileWidgets(self):
        widgets = [widget for widget in self.profileWidgets
                   if widget.required]
        return widgets

    @property
    def optionalProfileWidgets(self):
        widgets = [widget for widget in self.profileWidgets
                   if not(widget.required)]
        return widgets
