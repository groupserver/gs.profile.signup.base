# coding=utf-8
from zope.component import createObject
from zope.formlib import form
try:
    from five.formlib.formbase import PageForm
except ImportError:
    from Products.Five.formlib.formbase import PageForm
from Products.Five.browser.pagetemplatefile \
    import ZopeTwoPageTemplateFile
from Products.CustomUserFolder.interfaces import IGSUserInfo
from Products.XWFCore.XWFUtils import get_the_actual_instance_from_zope
from Products.GSProfile import interfaces
from Products.GSProfile.profileaudit import *
from Products.GSProfile.edit_profile import EditProfileForm,\
    select_widget, wym_editor_widget, multi_check_box_widget
from Products.GSProfile.utils import profile_interface_name, \
    profile_interface, enforce_schema
from gs.group.member.join.interfaces import IGSJoiningUser
from gs.group.member.invite.base.inviter import Inviter
from gs.profile.email.base.emailuser import EmailUser
from zope.app.apidoc.interface import getFieldsInOrder

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
        profileInterfaceName = profile_interface_name(context)
        registerInterfaceName = '%sRegister' % profileInterfaceName
        
        self.profileInterface = getattr(interfaces, profileInterfaceName)
        self.registerInterface = interface = getattr(interfaces, registerInterfaceName)
        enforce_schema(context, interface)

        self.__userInfo = self.__emailUser = None
        self.__formFields = self.__siteInfo = None
        self.__profileFields = None
        self.__hiddenFieldNames = ['form.came_from']
    
    @property
    def form_fields(self):
        if self.__formFields == None:
            self.__formFields = form.Fields(self.registerInterface, 
                                    render_context=True)
            self.__formFields['tz'].custom_widget = select_widget
            self.__formFields['biography'].custom_widget = \
                wym_editor_widget
            self.__formFields['joinable_groups'].custom_widget = \
                multi_check_box_widget
                
        return self.__formFields
        
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
    def siteInfo(self):
        if self.__siteInfo == None:
            self.__siteInfo = createObject('groupserver.SiteInfo', 
                                self.ctx)
        assert self.__siteInfo
        return self.__siteInfo

    @property
    def ctx(self):
        return get_the_actual_instance_from_zope(self.context)

    @property
    def groupsInfo(self):
        if self.__groupsInfo == None:
            self.__groupsInfo = createObject('groupserver.GroupsInfo', 
                self.ctx)
        return self.__groupsInfo

    @property
    def userInfo(self):
        if self.__userInfo == None:
            self.__userInfo = IGSUserInfo(self.ctx)
        assert self.__userInfo
        return self.__userInfo
    
    @property
    def emailUser(self):
        if self.__emailUser == None:
            self.__emailUser = EmailUser(self.ctx, self.userInfo)
        return self.__emailUser
    
    @property
    def userEmail(self):
        retval = self.emailUser.get_addresses()
        assert retval
        return retval

    @form.action(label=u'Change', failure='handle_set_action_failure')
    def handle_set(self, action, data):
        self.auditer = ProfileAuditer(self.context)
        self.actual_handle_set(action, data)

        cf = str(data.pop('came_from'))
        if cf == 'None':
            cf = ''
        if self.user_has_verified_email:
            uri = str(data.get('came_from'))
            if uri == 'None':
                uri = '/'
            uri = '%s?welcome=1' % uri
        else:
            email = self.emailUser.get_addresses()[0]
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
            groupsToJoin = data.pop('joinable_groups')

        fields = self.form_fields.omit('joinable_groups')
        for field in fields:
            field.interface = self.registerInterface            
        changed = form.applyChanges(self.context, fields, data)

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
        joiningUser = IGSJoiningUser(self.userInfo)
        for groupId in groupsToJoin:
            groupInfo = createObject('groupserver.GroupInfo', 
                                      self.ctx, groupId)
            joiningUser.join(groupInfo)

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

    @property
    def profileWidgetNames(self):
        if self.__profileFields == None:
            self.__profileFields = \
                ['form.%s' % f[0] for f in getFieldsInOrder(self.profileInterface)]
            self.__profileFields = [f for f in self.__profileFields if f not in self.__hiddenFieldNames]
        assert type(self.__profileFields) == list
        
        return self.__profileFields
    
    @property
    def profileWidgets(self):
        widgets = [widget for widget in self.widgets if widget.name in self.profileWidgetNames]
        return widgets
    
    @property
    def nonProfileWidgets(self):
        widgets = [widget for widget in self.widgets if widget.name not in (self.profileWidgetNames+self.__hiddenFieldNames)]
        return widgets

    @property
    def hiddenWidgets(self):
        widgets = [widget for widget in self.widgets if widget.name in self.__hiddenFieldNames]
        
        return widgets    
        
    @property  
    def requiredProfileWidgets(self):
        widgets = [widget for widget in self.profileWidgets if widget.required == True]

        return widgets
    
    @property
    def optionalProfileWidgets(self):
        widgets = [widget for widget in self.profileWidgets if widget.required == False]
            
        return widgets
