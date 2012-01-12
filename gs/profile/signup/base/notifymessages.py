# coding=utf-8
from urllib import quote
from zope.cachedescriptors.property import Lazy
from gs.profile.base.page import ProfilePage
from Products.GSGroup.interfaces import IGSMailingListInfo
UTF8 = 'utf-8'

class VerifyAddress(ProfilePage):
    @Lazy
    def email(self):
        l = IGSMailingListInfo(self.groupInfo.groupObj)
        retval = l.get_property('mailto')
        return retval
    
    def get_support_email(self, verificationLink, emailAddress):
        msg = u'Hi,\n\nI received a message to verify the email '\
          u'address <%s>,\nusing the link <%s> and...' %\
          (emailAddress, verificationLink)
        sub = quote('Verify Address')
        retval = 'mailto:%s?Subject=%s&body=%s' % \
            (self.siteInfo.get_support_email(), sub, quote(msg.encode(UTF8)))
        return retval
        
class VerifyAddressText(VerifyAddress):
    def __init__(self, context, request):
        NotifyMemberMessage.__init__(self, context, request)
        response = request.response
        response.setHeader("Content-Type", 'text/plain; charset=UTF-8')
        filename = 'verify-address-%s.txt' % self.groupInfo.name
        response.setHeader('Content-Disposition',
                            'inline; filename="%s"' % filename)

