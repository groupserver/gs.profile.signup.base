# coding=utf-8
from zope.component import createObject, provideAdapter, adapts
from zope.pagetemplate.pagetemplatefile import PageTemplateFile
from zope.interface import Interface, implements
from zope.publisher.interfaces import IDefaultBrowserLayer
from zope.contentprovider.interfaces import UpdateNotCalled, IContentProvider
from interfaces import IGSAwaitingVerificationJavaScriptContentProvider


class GSAwaitingVerificationJavaScriptContentProvider(object):
    """Content provider for the awaiting verification JavaScript."""
    implements(IGSAwaitingVerificationJavaScriptContentProvider)
    adapts(Interface, IDefaultBrowserLayer, Interface)

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
            raise UpdateNotCalled

        pageTemplate = PageTemplateFile(self.pageTemplateFileName)
        return pageTemplate(view=self)

provideAdapter(GSAwaitingVerificationJavaScriptContentProvider,
    provides=IContentProvider,
    name="groupserver.AwaitingVerificationJavaScript")
