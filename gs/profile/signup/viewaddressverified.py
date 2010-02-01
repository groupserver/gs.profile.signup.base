# coding=utf-8
from Products.Five import BrowserView

class AddressVerifiedView(BrowserView):
    def __init__(self, context, request):
        assert context
        assert request
        self.context = context
        self.request = request
        
    def __call__(self):
        assert self.request
        assert self.context
        
        assert hasattr(self.request, 'form'), 'No form in request'
        assert 'email' in self.request.form.keys(), 'No email in form'
        email = self.request.form['email']
        verified = self.context.emailAddress_isVerified(email)
        retval = verified and '1' or '0'
        return retval

