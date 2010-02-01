# coding=utf-8
from zope.component import createObject
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from Products.Five.formlib.formbase import PageForm
from Products.CustomUserFolder.userinfo import GSUserInfo
from Products.GSGroupMember.utils import inform_ptn_coach_of_join
from Products.GSProfile.set_password import set_password
from interfaces import IGSSetPasswordRegister

class SetPasswordForm(PageForm):
    form_fields = form.Fields(IGSSetPasswordRegister)
    label = u'Set Password'
    pageTemplateFileName = 'browser/templates/set_password_register.pt'
    template = ZopeTwoPageTemplateFile(pageTemplateFileName)
    
    def __init__(self, context, request):
        PageForm.__init__(self, context, request)
        self.siteInfo = createObject('groupserver.SiteInfo', context)
        self.userInfo = GSUserInfo(context)
               
    @form.action(label=u'Set', failure='handle_set_action_failure')
    def handle_set(self, action, data):
        assert self.context
        assert self.form_fields
        assert action
        assert data

        set_password(self.context, data['password1'])

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

    @property
    def userEmail(self):
        retval = self.context.get_emailAddresses()
        assert retval
        return retval

