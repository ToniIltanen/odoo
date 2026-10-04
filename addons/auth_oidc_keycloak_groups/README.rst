====================
OIDC Keycloak Groups
====================

This Odoo 19 add-on extends ``auth_oidc`` with Keycloak group-based user
provisioning. It applies only to an OAuth/OIDC provider whose Client ID is
``odoo``. Other providers use the standard sign-in behavior.

A validated ID token must contain a verified email address, a ``sub`` claim,
and a ``groups`` claim. The Keycloak groups determine the Odoo access level:

* ``user``: internal user (``base.group_user``).
* ``admin``: internal user with Access Rights
  (``base.group_erp_manager``) and Settings
  (``base.group_system``) permissions.
* Neither group: sig

If both groups are present, ``admin`` takes precedence. The Keycloak
``admin`` group does **not** authenticate as Odoo's technical superuser.

Installation
============

1. Install and configure ``auth_oidc`` for Keycloak authorization code flow.
2. Place this add-on beside ``auth_oidc`` in a directory included in Odoo's
   ``addons_path`` (for example, ``/mnt/extra-addons``).
3. Update the Apps list and install ``OIDC Keycloak Groups``.

Configuration
=============

Keycloak
--------

Create the ``user`` and ``admin`` groups and assign them only to users who
should be allowed into Odoo. In the Odoo client's dedicated scope, add a
``Group Membership`` protocol mapper with:

* Token claim name: ``groups``.
* Add to ID token: enabled.
* Full group path: disabled, so the values are ``user`` and ``admin``
  rather than ``/user`` and ``/admin``.

Verify the ID token's group values using Keycloak's Evaluate function. The
add-on matches exact group names; nested or full-path values are not
recognized by the current implementation.

Odoo
----

Configure the Keycloak provider in Odoo as documented by ``auth_oidc``.
The provider's Client ID must be ``odoo`` for this add-on to apply. If your
Client ID differs, change the provider-selection condition in
``models/res_users.py`` before use. Keep this provider check narrowly scoped;
do not apply the group mapping to unrelated OAuth providers.

Usage
=====

Use the Keycloak sign-in button on the Odoo login page. On a first
successful sign-in, the add-on creates a personal Odoo user with the verified
email address as login and links it using the provider and the token's
``sub`` identifier. It does not link an existing Odoo account solely because
its email address matches. A matching existing login blocks automatic
provisioning and needs administrator review.

On subsequent sign-ins, the add-on checks the Keycloak group claim again.
It updates the Odoo management groups it controls: ``admin`` receives the
Access Rights and Settings groups; ``user`` does not retain those two groups
if ``admin`` was removed. Other existing groups are preserved. Users with
neither recognized group are denied sign-in, including previously linked
users. Review active Odoo sessions separately when removing access: this
add-on does not revoke an already established session merely because a
Keycloak group changes.

This add-on suppresses the automatic password-reset invitation when it
provisions a user through OIDC. Users should sign in through Keycloak.

Security notes
==============

* The group mapping relies on ``auth_oidc`` validating the ID token. Do not
  read role information from unverified request parameters or an unvalidated
  token.
* ``admin`` grants broad Odoo administration rights, including Settings.
  Restrict membership of this Keycloak group and test with a separate user.
* The current implementation calls ``request.update_env(user=SUPERUSER_ID)``
  on successful sign-in to accommodate an Odoo 19 OAuth callback flush when
  the unauthenticated request otherwise has no environment user. This changes
  the request environment temporarily; assess its lifecycle and security
  before production use. The final Odoo session is authenticated separately
  as the personal Odoo user, not as the technical superuser.
* Remove temporary ``SSO diagnostic`` logging from any locally modified
  ``auth_oidc`` files. Do not log ID tokens, access tokens, authorization
  codes, or personally identifying claims.
* This module is not a complete identity lifecycle manager: it does not
  automatically deactivate users or revoke existing sessions.

Known issues / Roadmap
======================

* Replace the temporary superuser request-environment workaround with a
  reviewed, narrowly scoped fix for the Odoo 19 OAuth callback flush.
* Make the provider selection and exact group mapping configurable rather
  than hard-coded if more than one Keycloak client is required.
* Add automated tests for user/admin provisioning, loss of admin membership,
  missing groups, existing-login collisions, and other providers.

Credits
=======

This is a local extension of the OCA ``auth_oidc`` add-on, not an OCA module.
Its ``AGPL-3`` manifest license is separate from, and does not imply
maintainership by, the Odoo Community Association.