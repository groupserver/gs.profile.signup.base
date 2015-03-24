Changelog
=========

3.3.1 (2015-03-24)
------------------

* Ridding the code of a meddlesome ``assert``

3.3.0 (2015-03-12)
------------------

* Dealing with email addresses with ``+`` characters in them,
  closing `Bug 4036`_
* Adding internationalisation_
* [FR] Adding a French translation, thanks to `Razique Mahroua`_

.. _Bug 4036: https://redmine.iopen.net/issues/4036
.. _internationalisation:
   https://www.transifex.com/projects/p/gs-profile-signup-base/
.. _Razique Mahroua:
   https://www.transifex.com/accounts/profile/Razique/

3.2.0 (2014-10-10)
------------------

* Pointing at GitHub_ as the canonical source repository
* Naming the reStructuredText files as such
* Dropping the ``IGSEmailAddressEntry``

.. _GitHub: https://github.com/groupserver/gs.profile.signup.base

3.1.3 (2014-06-12)
------------------

* Following the form code to ``gs.content.form.base``

3.1.2 (2014-01-23)
------------------

* Fixing an intra-document link, with thanks to Ben Cox (closing
  `Bug 4056`_)
* Switching to Unicode literals, and sanitise the email address
  that is entered on the *Request registration* page
* Metacleanup

.. _Issue 4056: https://redmine.iopen.net/issues/4056

3.1.0 (2013-11-14)
------------------

* Switching to the new WYMeditor

3.1.0 (2013-10-21)
------------------

* Fixing the *Remote registration request* code
* Sending the new *Verify* notification (closing `Issue 3483`_
  and `Issue 3484`_)
* Sending the new *Welcome* notification (closing `Issue 3471`_
  and `Issue 3477`_)

.. _Issue 3483: https://redmine.iopen.net/issues/3483
.. _Issue 3484: https://redmine.iopen.net/issues/3484
.. _Issue 3471: https://redmine.iopen.net/issues/3471
.. _Issue 3477: https://redmine.iopen.net/issues/3477

3.0.0 (2013-06-06)
------------------

* Update for the new UI
* Changing the name to *Register* from *Sign up*
* Added a password-visibility toggle to *Set password* page
* New JavaScript products

2.2.2 (2012-10-23)
------------------

* Code cleanup

2.2.1 (2012-06-22)
------------------

* Update to the SQL Alchemy code

2.2.0 (2012-05-15)
------------------

* Following ``gs.group.member.invite.base``

2.1.0 (2012-01-12)
------------------

* Improving the FAQ wording in the *Verify* email message
* Fixing the final button on the *Verify wait* page

2.0.1 (2011-09-08)
------------------

* Improving the ``GroupIdNotFound`` error.
* Fixes for the HTML

2.0.0 (2011-08-08)
------------------

* Changing the name-space for this product to
  ``gs.profile.signup.base``

1.7.0 (2011-06-16)
------------------

* Changes to make the email-address verification process less
  confusing

1.6.0 (2011-02-22)
------------------

* Following the core email-address code to
  ``gs.profile.email.base``

1.5.0 (2011-01-10)
------------------

* Following the email-address verification code to
  ``gs.profile.email.verify``

1.4.0 (2010-12-09)
------------------

* Following the *Set password* code to ``gs.profile.password``
* Moving the page-specific CSS to the global style-sheet
* Using the new form-message content provider

1.3.0 (2010-10-05)
------------------

* Improvements to the wording of the *Verify wait* page and *Sign
  up* page

1.2.0 (2010-08-19)
------------------

* Setting the focus of the forms correctly
* Code cleanup, and fixes for Zope2 2.13
* Following the moved invitation query

1.1.0 (2010-07-28)
------------------

* Use the new code in ``gs.group.member.join`` and
  ``gs.group.member.invite``
* Deal with ``PageForm`` moving to ``five.formlib``

1.0.3 (2010-05-31)
------------------

* Changing the permissions for the *Check email verified* page

1.0.2 (2010-03-18)
------------------

* Switching to the site support email-address for the source of
  the email-verification messages

1.0.1 (2010-03-04)
------------------

* Fixing an error with the timezone

1.0.0 (2010-02-15)
-------------------

* Split ``gs.profile.signup`` off from ``Products.GSProfile.``
* Reordered the pages involved in sign up:
  1. Sign Up
  2. Set Password
  3. Change Profile
  4. Verify Email
* The Set Password page now takes in the password *en clear*


..  LocalWords:  Changelog GitHub reStructuredText
