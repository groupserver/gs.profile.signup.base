# coding=utf-8
from zope.component import createObject
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from Products.CustomUserFolder.userinfo import GSUserInfo
from gs.content.form.form import SiteForm
from gs.profile.email.base.emailuser import EmailUser
from gs.profile.password.interfaces import IGSPasswordUser
from interfaces import IGSSetPasswordRegister

class SetPasswordForm(SiteForm):
    form_fields = form.Fields(IGSSetPasswordRegister)
    label = u'Set Password'
    pageTemplateFileName = 'browser/templates/setpassword.pt'
    template = ZopeTwoPageTemplateFile(pageTemplateFileName)
    
    def __init__(self, context, request):
        SiteForm.__init__(self, context, request)
        self.userInfo = GSUserInfo(context)
        self.emailUser = EmailUser(context, self.userInfo)
               
    @form.action(label=u'Set', failure='handle_set_action_failure')
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
            self.status = u'<p>There is an error:</p>'
        else:
            self.status = u'<p>There are errors:</p>'

    @property
    def userEmail(self):
        retval = self.emailUser.get_addresses()
        assert retval
        return retval

