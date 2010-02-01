// GroupServer module for checking if email addresses are verified
jQuery.noConflict();
GSCheckEmailVerified = function () {

    // Private variables
    var email = null;
    var button = null;
    var satusUpdate = null;
    var thingsToCheck = null;
    
    var ADDRESS = 'verify_email.ajax';
    var TIMEOUT_DELTA = 8000;
    var CHECKING_MSG = '<strong>Checking</strong> verification ' +
      'status&#160;<img src="/++resource++anim/wait.gif"/>';
    var UNVERIFIED_MSG = 'The email address is '+
      '<strong>not verified.</strong>';
    var VERIFIED_MSG = 'The email address is <strong>verified.</strong> ' +
      'Click <samp class="button">Next</samp> to go to the next page.';
    // Private methods

    // Public methods and properties. The "checkServer" and "checkReturn"
    // methods have to b public, due to oddities with "setTimeout".
    return {
        init: function (e, b, s, c) {
            /* Add the address-checking code to the correct widgets
            
            ARGUMENTS
              e:  String containing the selector for the email address
              b:  String containing the selector for the submit button 
                  for the form
              s:  String containing the selector for the status-update
                  container.
              c:  String containing the selector for the Things to Check
                  section.
            */
            email = e;
            button = b;
            statusUpdate = s;
            thingsToCheck = c;
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
                jQuery(statusUpdate).html(VERIFIED_MSG);
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
        }
    };
}(); // GSCheckEmailVerified

