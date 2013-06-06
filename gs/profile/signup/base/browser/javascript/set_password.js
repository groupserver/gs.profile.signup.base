jQuery.noConflict();

function gs_profile_signup_base_password_init () {
    var toggler = null;
    toggler = GSProfilePasswordToggle('#form\\.password1', 
                                      '#gs-profile-signup-base-password-toggle-widget');
}

jQuery(window).load( function () {
    jQuery('#form\\.password1').focus();
    gsJsLoader.with_module('/++resource++gs-profile-password-toggle-min-20130516.js', 
                           gs_profile_signup_base_password_init);
});
