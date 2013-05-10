// GroupServer module for checking if email addresses are verified
jQuery.noConflict();
GSCheckEmailVerified = function () {

    // Private variables
    var email = null,
        button = null,
        satusUpdate = null,
        thingsToCheck = null
        ADDRESS = 'checkemailverified.ajax',
        TIMEOUT_DELTA = 4000,
        AUTOSUBMIT_TIMEOUT = 5000,
        CHECKING_MSG = '<strong>Checking</strong> verification ' +
            'status&#160;<img src="/++resource++anim/wait.gif"/>',
        UNVERIFIED_MSG = 'The email address is '+
            '<strong>not verified.</strong>',
        VERIFIED_MSG = 'The email address is <strong>verified.</strong> '+
            'You may now click the <samp class="button">Finish</samp> ' +
            'button, or simply wait XSEC seconds.';
    // Private methods

    // Public methods and properties. The "checkServer" and "checkReturn"
    // methods have to be public, due to oddities with "setTimeout".
    return {
        init: function (e, f, b, s, c) {
            /* Add the address-checking code to the correct widgets
            
            ARGUMENTS
              e:  String containing the selector for the email address
              f:  String containing the selector for the form
              b:  String containing the selector for the submit button 
                  for the form
              s:  String containing the selector for the status-update
                  container.
              c:  String containing the selector for the Things to Check
                  section.
            */
            email = e;
            form = f;
            button = b;
            VERIFIED_MSG = VERIFIED_MSG.replace('Finish', 
                                                jQuery(b).attr('value'))
            statusUpdate = s;
            thingsToCheck = c;
            submitCount = AUTOSUBMIT_TIMEOUT / 1000;
            GSCheckEmailVerified.checkServer();
        },
        checkServer: function () {
            jQuery.ajax({
              type: "POST",
              url: ADDRESS, 
              cache: false,
              data: 'email='+email,
              success: GSCheckEmailVerified.checkReturn});
            jQuery(statusUpdate).html(CHECKING_MSG);
        },
        checkReturn: function (data, textStatus) {
            var verified = data == '1';
            if (verified) {
                jQuery(button).attr("disabled","");
                jQuery(thingsToCheck + ' input').attr("disabled","disabled");
                GSCheckEmailVerified.updateVerifiedMessage();
                setTimeout("GSCheckEmailVerified.autoSubmitForm()",
                    AUTOSUBMIT_TIMEOUT);
            } else {
                jQuery(button).attr("disabled","disabled");
                setTimeout("GSCheckEmailVerified.checkServer()",
                  TIMEOUT_DELTA);
                setTimeout("GSCheckEmailVerified.changeCheckingMessage()",
                  TIMEOUT_DELTA / 2)
            }
        },
        changeCheckingMessage: function() {
            jQuery(statusUpdate).html(UNVERIFIED_MSG);              
        },
        updateVerifiedMessage: function() {
            vm = VERIFIED_MSG.replace('XSEC',submitCount)
            jQuery(statusUpdate).html(vm);
            submitCount -= 1;
            setTimeout("GSCheckEmailVerified.updateVerifiedMessage()", 1000);
        },
        autoSubmitForm: function() {
            jQuery(button).click();
            jQuery(button).submit();
        }
    };
}(); // GSCheckEmailVerified
