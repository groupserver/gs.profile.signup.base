==========================
``gs.profile.signup.base``
==========================
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Sign up (register) a profile with GroupServer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Author: `Michael JasonSmith`_
:Contact: Michael JasonSmith <mpj17@onlinegroups.net>
:Date: 2014-10-10
:Organization: `GroupServer.org`_
:Copyright: This document is licensed under a
  `Creative Commons Attribution-Share Alike 4.0 International License`_
  by `OnlineGroups.net`_.

Introduction
============

This part of the GroupServer user-profile code concerned with
sign up (alias registration). It contains the pages, and
templates, that are specific to sign up. The interface highly
determines the new member, sending him or her through four pages:

* `Sign Up`_
* `Set Password`_
* `Change Profile`_
* `Verify Address`_

Sign Up
=======

This is the initial page seen during sign up. The new member
types his or her email address into the single text-entry and
hits *Sign up*. Then the following occurs

#. A new profile is created,
#. A *Verify* *Address* notification is sent to the member,
#. The member is logged in, and 
#. The member is sent to the `Set Password`_ page.

Set Password
============

This page allows the new member to set a password. The password
is entered *en-clear* as it causes fewer support problems in the
long run. After entering a password the new member is sent to the
`Change Profile`_ page.

Change Profile
==============

The change profile page that is used during sign-up is very
similar to the normal change profile. The main difference is that
it also allows the member so select some groups that he or she
wishes to join.

If the member has verified his or her address, then the change
profile page will redirect the member to the site
homepage. Otherwise the member will be sent to the `Verify
Address`_ page.

Verify Address
==============

This page is last in the sign-up sequence to give the
email-verification message a chance to arrive in the inbox of the
new member. In of itself the page does not do much other than
check if the address has been verified (using AJAX).

Resources
=========

- Code repository:
  https://github.com/groupserver/gs.profile.signup.base
- Questions and comments to
  http://groupserver.org/groups/development
- Report bugs at https://redmine.iopen.net/projects/groupserver

.. _GroupServer: http://groupserver.org/
.. _GroupServer.org: http://groupserver.org/
.. _OnlineGroups.Net: https://onlinegroups.net
.. _Michael JasonSmith: http://groupserver.org/p/mpj17
..  _Creative Commons Attribution-Share Alike 4.0 International License:
    http://creativecommons.org/licenses/by-sa/4.0/

..  LocalWords:  signup mpj groupserver
