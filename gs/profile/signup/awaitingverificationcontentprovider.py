# coding=utf-8
from zope.component import createObject
from zope.pagetemplate.pagetemplatefile import PageTemplateFile
import zope.interface, zope.component, zope.publisher.interfaces
import zope.viewlet.interfaces, zope.contentprovider.interfaces 
from interfaces import IGSAwaitingVerificationJavaScriptContentProvider

class GSAwaitingVerificationJavaScriptContentProvider(object):
    """Content provider for the awaiting verification JavaScript."""
    zope.interface.implements( IGSAwaitingVerificationJavaScriptContentProvider )
    zope.component.adapts(zope.interface.Interface,
        zope.publisher.interfaces.browser.IDefaultBrowserLayer,
        zope.interface.Interface)

    def __init__(self, context, request, view):
        self.__parent__ = self.view = view
        self.__updated = False
        self.context = context
        self.request = request
        
    def update(self):
        self.__updated = True
        self.siteInfo = createObject('groupserver.SiteInfo', 
          self.context)

    def render(self):
        if not self.__updated:
            raise interfaces.UpdateNotCalled

        pageTemplate = PageTemplateFile(self.pageTemplateFileName)
        return pageTemplate(view=self)

zope.component.provideAdapter(GSAwaitingVerificationJavaScriptContentProvider,
    provides=zope.contentprovider.interfaces.IContentProvider,
    name="groupserver.AwaitingVerificationJavaScript")

