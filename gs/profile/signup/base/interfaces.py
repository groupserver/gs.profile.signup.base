# coding=utf-8
from zope.component import createObject
from zope.contentprovider.interfaces import IContentProvider
from zope.interface.interface import Interface
from zope.schema import ASCIILine, Text, URI, ValidationError
from zope.viewlet.interfaces import IViewletManager
from Products.GSProfile.interfaces import IGSEmailAddressEntry
from gs.profile.email.base.emailaddress import EmailAddress
from gs.profile.password.interfaces import ISetPassword


class IGSRequestRegistrationMarker(Interface):
    """Marker interface for the request registration page.
    """


class GroupIDNotFound(ValidationError):
    """Group identifier not found"""
    def __init__(self, value):
        self.value = value

    def __unicode__(self):
        retval = u'The group with the identifier %s is not in the '\
            u'list of visible groups.' % repr(self.value)
        return retval

    def __str__(self):
        retval = unicode(self).encode('ascii', 'ignore')
        return retval

    def doc(self):
        return self.__str__()


class GroupID(ASCIILine):
    def constraint(self, value):
        groupsInfo = createObject('groupserver.GroupsInfo', self.context)
        groupIds = groupsInfo.get_visible_group_ids()
        if value not in groupIds:
            raise GroupIDNotFound(value)
        return True


class IGSRequestRegistration(IGSEmailAddressEntry):
    """Schema use to define the user-interface that start the whole
    registration process"""
    # Unfortunately the group identifier is not checked against the
    #   joinable groups, because there is no "user" to check with.
    groupId = GroupID(title=u'Group Identifier',
      description=u'The identifier for the group that you '
        u'wish to join.',
      required=False)

    came_from = URI(title=u'Came From',
      description=u'The page to return to after registration has finished',
      required=False)


class IGSSetPasswordRegister(ISetPassword):
    groupId = GroupID(title=u'Group Identifier',
      description=u'The identifier for the group that you '
        u'wish to join.',
      required=False)

    came_from = URI(title=u'Came From',
      description=u'The page to return to after registration has finished',
      required=False)


# Change Profile is a bit special


class IGSResendVerification(IGSEmailAddressEntry):
    """Schema use to define the user-interface that the user uses to
    resend his or her verification email, while in the middle of
    registration."""


class IGSVerifyWait(IGSEmailAddressEntry):
    """Schema use to define the user-interface presented while the user
    waits for verification of his or her email address."""

    came_from = URI(title=u'Came From',
      description=u'The page to return to after registration has finished',
      required=False)


class IGSAwaitingVerificationJavaScriptContentProvider(IContentProvider):
    pageTemplateFileName = Text(title=u"Page Template File Name",
      description=u'The name of the ZPT file that is used to render the '
        u'javascript.',
      required=False,
      default=u"browser/templates/verify_wait_javascript.pt")

    email = EmailAddress(title=u'Email Address',
        description=u'Your email address.',
        required=True)


class ISignupMethods(IViewletManager):
    '''A viewlet manager for the alternative signup methods '''
