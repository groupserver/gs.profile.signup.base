'use strict';
// GroupServer module for checking if email addresses are verified
// Copyright © 2016 OnlineGroups.net and Contributors.
// All Rights Reserved.
//
// This software is subject to the provisions of the Zope Public License,
// Version 2.1 (ZPL). http://groupserver.org/downloads/license/
//
// THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
// WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
// WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND
// FITNESS FOR A PARTICULAR PURPOSE.
jQuery.noConflict();
function GSCheckEmailVerified(email, buttonId, msgCheckingId, msgUnverifiedId,
                              msgVerifiedId,  thingsToCheckId) {

    // Private variables
    var button = null,
        satusUpdate = null,
        thingsToCheck = null,
        submitCount = null,
        msgChecking = null,
        msgUnverified = null,
        msgVerified = null,
        ADDRESS = 'checkemailverified.ajax', // In the profile context
        TIMEOUT_DELTA = 8000,
        AUTOSUBMIT_TIMEOUT = 5000;

    // Private methods
    function checkServer() {
        var d = null;
        jQuery('.status').removeClass('status-current');
        d = {
            type: 'POST',
            url: ADDRESS,
            cache: false,
            data: {'email': email},
            success: checkReturn
        };
        jQuery.ajax(d);
        msgChecking.addClass('status-current');
    }// checkServer

    function checkReturn(data, textStatus) {
        var verified = null, halfDelta = null;
        verified = data == '1';
        if (verified) {
            button.removeAttr('disabled');
            jQuery('.status').removeClass('status-current');
            msgVerified.addClass('status-current');
            updateVerifiedMessage();
            thingsToCheck.find('input').attr('disabled', 'disabled');
            window.setTimeout(autoSubmitForm, AUTOSUBMIT_TIMEOUT);
        } else {
            button.attr('disabled', 'disabled');
            // To give people time to read the message
            halfDelta = TIMEOUT_DELTA / 2;
            window.setTimeout(changeCheckingMessage, halfDelta);
            window.setTimeout(checkServer, TIMEOUT_DELTA);
        }
    }// checkReturn

    function updateVerifiedMessage() {
        submitCount -= 1;
        msgVerified.children('.seconds').html(submitCount);
        if (submitCount > 0) {
            window.setTimeout(updateVerifiedMessage, 1000);
        }
    }// updateVerifiedMessage

    function autoSubmitForm() {
        button.click();
    }// autoSubmitForm

    function changeCheckingMessage() {
        jQuery('.status').removeClass('status-current');
        msgUnverified.addClass('status-current');
    }// changeCheckingMessage

    function init() {
        msgChecking = jQuery(msgCheckingId);
        msgUnverified = jQuery(msgUnverifiedId);
        msgVerified = jQuery(msgVerifiedId);

        button = jQuery(buttonId);
        thingsToCheck = jQuery(thingsToCheckId);
        submitCount = AUTOSUBMIT_TIMEOUT / 1000;
        msgVerified.children('.seconds').html(submitCount);
    }// init
    init(); // Note the automatic execution.

    return {
        start: function() { checkServer(); }
    };
}// GSCheckEmailVerified

jQuery(window).load(function() {
    var script = null,
        email = null,
        button = null,
        msgCheckingId = null,
        msgUnverifiedId = null,
        msgVerifiedId = null,
        thingsToCheck = null,
        autosubmit = null,
        checker = null;

    script = jQuery('#gs-profile-signup-verify-js');

    email = script.data('email');
    button = script.data('button');
    msgCheckingId = script.data('msg-checking');
    msgUnverifiedId = script.data('msg-unverified');
    msgVerifiedId = script.data('msg-verified');
    thingsToCheck = script.data('toCheck');

    checker = GSCheckEmailVerified(email, button, msgCheckingId,
                                   msgUnverifiedId, msgVerifiedId,
                                   thingsToCheck);
    checker.start();
});
