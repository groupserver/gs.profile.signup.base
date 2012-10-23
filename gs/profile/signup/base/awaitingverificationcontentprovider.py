# coding=utf-8
from zope.pagetemplate.pagetemplatefile import PageTemplateFile
from zope.contentprovider.interfaces import UpdateNotCalled
from gs.viewlet.contentprovider import SiteContentProvider


class GSAwaitingVerificationJavaScriptContentProvider(SiteContentProvider):
    """Content provider for the awaiting verification JavaScript."""

    def __init__(self, context, request, view):
        s = super(GSAwaitingVerificationJavaScriptContentProvider, self)
        s.__init__(context, request, view)
        self.__updated = False

    def update(self):
        self.__updated = True

    def render(self):
        if not self.__updated:
            raise UpdateNotCalled

        pageTemplate = PageTemplateFile(self.pageTemplateFileName)
        return pageTemplate(view=self)
