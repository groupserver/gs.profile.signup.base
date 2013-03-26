# -*- coding: utf-8 -*-
'''Implementation of the Remote Request Registration form.
'''
from gs.content.base import SitePage


class GSRemoteRequestRegistration(SitePage):
    '''View object for the GroupServer Remote Request Registration'''
    def __init__(self, context, request):
        super(GSRemoteRequestRegistration, self).__init__(context, request)
