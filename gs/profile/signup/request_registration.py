# coding=utf-8
'''Implementation of the Sign Up form.'''
from Products.Five.formlib.formbase import PageForm
from zope.component import createObject
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from Products.XWFCore.XWFUtils import get_support_email
from Products.CustomUserFolder.interfaces import IGSUserInfo
from Products.GSProfile.utils import login, create_user_from_email, \
    send_verification_message
from Products.GSProfile.emailaddress import NewEmailAddress, \
    EmailAddressExists
from interfaces import IGSRequestRegistration
import logging
log = logging.getLogger('GSProfile')
from Products.GSProfile.profileaudit import *
from Products.GSAuditTrail.queries import AuditQuery

class RequestRegistrationForm(PageForm):
    form_fields = form.Fields(IGSRequestRegistration)
    label = u'Sign Up'
    pageTemplateFileName = 'browser/templates/signup.pt'
    template = ZopeTwoPageTemplateFile(pageTemplateFileName)

    def __init__(self, context, request):
        PageForm.__init__(self, context, request)
        self.context = context
        self.request = request
        self.siteInfo = createObject('groupserver.SiteInfo', context)
        self.groupsInfo = createObject('groupserver.GroupsInfo', context)

        self.groupInfo = None
        if 'form.groupId' in request.form.keys():
            gId = request.form['form.groupId']
            if gId in self.groupsInfo.get_visible_group_ids():
                self.groupInfo = createObject('groupserver.GroupInfo',
                                              context, gId)
            
    @property
    def verificationEmailAddress(self):
        retval = get_support_email(self.context, self.siteInfo.id)
        assert type(retval) == str
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
    @form.action(label=u'Sign up', failure='handle_register_action_failure', 
      validator='validate')
    def handle_register(self, action, data):
        assert self.form_fields
        assert action
        assert data

        email = data['email'].strip()
        emailChecker = NewEmailAddress(title=u'Email')
        emailChecker.context = self.context # --=mpj17=-- Legit? Works!
        try:
            emailChecker.validate(email)
        except EmailAddressExists, e:
            logMsg = 'RequestRegistrationForm: Registration attempted with '\
              'existing address <%s>' % email
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
        else: # The address does not exist!
            userInfo =  self.createUser(email)

            uri = '%s/register_password.html%s' % \
                (userInfo.url, self.get_uri_end(data))

            return self.request.RESPONSE.redirect(uri)

    def handle_register_action_failure(self, action, data, errors):
        if len(errors) == 1:
            self.status = u'<p>There is an error:</p>'
        else:
            self.status = u'<p>There are errors:</p>'

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
    * A message, if neede,
    * A flag to say if the user should be automatically logged in
      by the system, or not.

Side Effects
------------

None.'''
        uri = ''
        m = u''
        systemLoginRequired = False
            
        acl_users = self.context.acl_users
        emailUser = acl_users.get_userByEmail(email)
        userInfo = IGSUserInfo(emailUser)

        # Checks for incomplete sign up.
        changedProfile = email.split('@')[0] != userInfo.name
        verified = emailUser.get_verifiedEmailAddresses() != []

        if not password_set(self.context, emailUser):
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
        else: # set password, changed profile, and verified
            d = {
                'email':    email,
                'site':     self.siteInfo.name,
                'resetUrl': 'reset_password.html?form.email=%s' % email,
                'loginUrl': '/login.html',
            }
            m = u'''A user with the email address 
                <code class="email">%(email)s</code> already exists on 
                <span class="site">%(site)s</span>. Either
                <ul>
                  <li><a href="%(resetUrl)s"><strong>Reset</strong> your 
                      password,</a></li>
                  <li><a href="%(loginUrl)s"><strong>Login,</strong></a>
                  <li><strong>Sign up</strong> with another email 
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

        site = self.siteInfo.siteObj
        send_verification_message(site, user, email)
        
        return userInfo        

    def get_uri_end(self,data):
        '''Get the snippit of a URI that comes at the end of all redirects
        from this page.'''
        cf = str(data.get('came_from'))
        if cf == 'None':
            cf = ''
        gid = str(data.get('groupId'))
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
    q = AuditQuery(context.zsqlalchemy)
    items = q.get_instance_user_events(user.getId(), limit=128)
    setPasswordItems = [i for i in items 
                        if ((i['subsystem'] == SUBSYSTEM)
                            and (i['code'] == SET_PASSWORD))]
    retval = bool(setPasswordItems)
    return retval



