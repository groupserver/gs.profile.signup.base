// GroupServer module for checking if email addresses are verified
jQuery.noConflict();
var GSCheckEmailVerified = function (email, buttonId, satusUpdateId, 
                                     thingsToCheckId) {

    // Private variables
    var button = null,
        satusUpdate = null,
        thingsToCheck = null,
        submitCount = null,
        ADDRESS = 'checkemailverified.ajax', // In the profile context
        TIMEOUT_DELTA = 8000,
        AUTOSUBMIT_TIMEOUT = 5000,
        CHECKING_MSG = '<strong>Checking</strong> verification ' +
            'status&#160;<img src="/++resource++anim/wait.gif"/>',
        UNVERIFIED_MSG = 'The email address is '+
            '<strong>not verified.</strong>',
        VERIFIED_MSG = 'The email address is <strong>verified.</strong> '+
            'You may now click the <samp class="button">FINISH</samp> ' +
            'button, or wait XSEC seconds.';

    // Private methods
    function checkServer() {
        var d = null;
        d = {
            type: "POST",
            url: ADDRESS, 
            cache: false,
            data: 'email='+email,
            success: checkReturn
        }
        jQuery.ajax(d);
        statusUpdate.html(CHECKING_MSG);
    };

    function checkReturn(data, textStatus) {
        var verified = null, halfDelta = null;
        verified = data == '1';
        if ( verified ) {
            button.removeAttr("disabled");
            updateVerifiedMessage();
            thingsToCheck.find('input').attr("disabled","disabled");
            window.setTimeout(autoSubmitForm, AUTOSUBMIT_TIMEOUT);
        } else {
            button.attr("disabled","disabled");
            // To give people time to read the message
            halfDelta = TIMEOUT_DELTA / 2;
            window.setTimeout(changeCheckingMessage, halfDelta)
            window.setTimeout(checkServer, TIMEOUT_DELTA);
        }
    }

    function updateVerifiedMessage() {
        var vm = null;
        vm = VERIFIED_MSG.replace('XSEC', submitCount)
        statusUpdate.html(vm);
        submitCount -= 1;
        if ( submitCount >= 0 ) {
            window.setTimeout(updateVerifiedMessage, 1000);
        }
    }

    function autoSubmitForm() {
        button.click();
        //jQuery(button).submit();
    }

    function changeCheckingMessage() {
        statusUpdate.html(UNVERIFIED_MSG);              
    }

    function init() {
        var buttonVal = null;

        button = jQuery(buttonId);
        statusUpdate = jQuery(satusUpdateId);
        thingsToCheck = jQuery(thingsToCheckId);

        buttonVal = button.attr('value');
        VERIFIED_MSG = VERIFIED_MSG.replace('FINISH', buttonVal);

        submitCount = AUTOSUBMIT_TIMEOUT / 1000;
    }
    init(); // Note the automatic execution.

    return {
        start: function () { checkServer(); },
    };
}; // GSCheckEmailVerified

jQuery(window).load(function () {
    var script = null, 
        email = null, 
        button = null, 
        statusUpdate = null, 
        thingsToCheck = null,
        checker = null;

    script = jQuery('#gs-profile-signup-verify-js');

    email = script.attr('data-email');
    button = script.attr('data-button');
    statusUpdate = script.attr('data-status');
    toCheck = script.attr('data-toCheck');

    checker = GSCheckEmailVerified(email, button, statusUpdate, toCheck);
    checker.start();
});
