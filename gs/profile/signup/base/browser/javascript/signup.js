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

function gs_profile_signup_init_disclosure() {
    jQuery('#privacy-button').click(function() {
        var uri = '/policies/privacy/ #privacy';
        jQuery('#privacy-content').load(uri);
    });

    jQuery('#tc-button').click(function() {
        var uri = '/policies/aup/ #aup';
        jQuery('#tc-content').load(uri);
    });
}

function gs_profile_signup_init_webmail_check() {
    var webmail = new Array('gmail', 'hotmail', 'yahoo');
    GSCheckEmailAddress.init(
        '#form\\.email',
        '#form\\.actions\\.register',
        '#addressBookHelp',
        webmail,
        '#emailHelp');
}

jQuery(window).load(function() {
    gs_profile_signup_init_disclosure();
    gsJsLoader.with_module('/++resource++check_email-20110222.js',
                           gs_profile_signup_init_webmail_check);
    jQuery('#form\\.email').focus();
});
