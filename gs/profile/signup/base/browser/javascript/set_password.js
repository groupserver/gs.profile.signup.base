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

function gs_profile_signup_base_password_init() {
    var toggler = null;
    toggler = GSProfilePasswordToggle(
        '#form\\.password1',
        '#gs-profile-signup-base-password-toggle-widget');
}

jQuery(window).load(function() {
    jQuery('#form\\.password1').focus();
    gsJsLoader.with_module(
        '/++resource++gs-profile-password-toggle-min-20130516.js',
        gs_profile_signup_base_password_init);
});
