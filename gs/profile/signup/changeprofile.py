# coding=utf-8
from zope.component import createObject
from zope.formlib import form
from Products.Five.formlib.formbase import PageForm
from Products.Five.browser.pagetemplatefile \
    import ZopeTwoPageTemplateFile
from Products.CustomUserFolder.interfaces import IGSUserInfo
from Products.GSGroupMember.groupmembership import join_group
from Products.GSGroupMember.utils import inform_ptn_coach_of_join
from Products.GSProfile.edit_profile import EditProfileForm,\
    select_widget, wym_editor_widget, multi_check_box_widget
from Products.GSProfile.utils import profile_interface_name, \
    profile_interface, enforce_schema
from Products.GSProfile import interfaces
from Products.GSProfile.profileaudit import *

class ChangeProfileForm(EditProfileForm):
    """The Change Profile page used during registration is slightly 
    different from the standard Change Profile page, as the user is able
    to join groups.
    """
    label = u'Change Profile'
    pageTemplateFileName = 'browser/templates/changeprofile.pt'
    template = ZopeTwoPageTemplateFile(pageTemplateFileName)

    def __init__(self, context, request):
        PageForm.__init__(self, context, request)
        self.siteInfo = createObject('groupserver.SiteInfo', context)
        self.groupsInfo = createObject('groupserver.GroupsInfo', context)
        self.userInfo = IGSUserInfo(context)

        interfaceName = '%sRegister' % profile_interface_name(context)
        self.interface = interface = getattr(interfaces,interfaceName)
        enforce_schema(context, interface)
        
        request.form['form.tz'] = self.get_timezone() # Look, a hack!
        self.form_fields = form.Fields(interface, render_context=True)

        self.form_fields['tz'].custom_widget = select_widget
        self.form_fields['biography'].custom_widget = wym_editor_widget
        #assert self.form_fields.has_key('joinable_groups'), \
        #    'No joinable_groups in %s' % interfaceName
        self.form_fields['joinable_groups'].custom_widget = \
          multi_check_box_widget

    def get_timezone(self):
        if self.request.form.get('form.tz', ''):
            retval = self.request.form.get['form.tz']
        else:
            gTz = siteTz = self.siteInfo.get_property('tz', 'UTC')
            joinableGroups = self.request.form.get('form.joinable_groups',[])
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
                    gTzs.append(getattr(groups, gId).getProperty('tz', siteTz))
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
        
    @property
    def userEmail(self):
        retval = self.context.get_emailAddresses()
        assert retval
        return retval

    @form.action(label=u'Change', failure='handle_set_action_failure')
    def handle_set(self, action, data):
        self.auditer = ProfileAuditer(self.context)
        self.actual_handle_set(action, data)

        cf = str(data.pop('came_from'))
        if cf == 'None':
          cf = ''
        if self.user_has_verified_email():
            uri = str(data.get('came_from'))
            if uri == 'None':
                uri = '/'
            uri = '%s?welcome=1' % uri
        else:
            email = self.context.get_emailAddresses()[0]
            uri = 'verify_wait.html?form.email=%s&form.came_from=%s' %\
              (email, cf)

        return self.request.RESPONSE.redirect(uri)
        
    def handle_set_action_failure(self, action, data, errors):
        if len(errors) == 1:
            self.status = u'<p>There is an error:</p>'
        else:
            self.status = u'<p>There are errors:</p>'
        
    def actual_handle_set(self, action, data):
        groupsToJoin = None
        if 'joinable_groups' in data.keys():
            # --=mpj17=-- Site member?
            groupsToJoin = data.pop('joinable_groups')

        self.form_fields = self.form_fields.omit('joinable_groups')
        print '======== Timezone: %s' % data['tz']
        self.set_data(data)

        if groupsToJoin:
            self.join_groups(groupsToJoin)
        
    def user_has_verified_email(self):
        email = self.context.get_emailAddresses()[0]
        retval = self.context.emailAddress_isVerified(email)
        return retval

    def join_groups(self, groupsToJoin):
        ui = IGSUserInfo(self.context)
        joinableGroups = \
            self.groupsInfo.get_joinable_group_ids_for_user(self.context)

        for groupId in groupsToJoin:
            assert groupId in joinableGroups, \
              '%s not a joinable group' % groupId
            groupInfo = createObject('groupserver.GroupInfo', 
                                      self.groupsInfo.groupsObj,
                                      groupId)
            
            join_group(self.context, groupInfo)

            ptnCoachId = groupInfo.get_property('ptn_coach_id', '')
            if ptnCoachId:
                ptnCoachInfo = createObject('groupserver.UserFromId', 
                                            self.context, ptnCoachId)
                inform_ptn_coach_of_join(ptnCoachInfo, self.userInfo,
                                         groupInfo)

