import logging

from odoo import Command, api, models, SUPERUSER_ID
from odoo.exceptions import AccessDenied
from odoo.http import request

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model
    def _auth_oauth_signin(self, provider, validation, params):
        oauth_provider = self.env["auth.oauth.provider"].browse(provider)

        # Leave other OAuth/OIDC providers unchanged. Set this provider's
        # client ID to "odoo" in Keycloak, as in the current configuration.
        if oauth_provider.client_id != "odoo":
            return super()._auth_oauth_signin(provider, validation, params)

        groups = validation.get("groups")
        if not isinstance(groups, list) or not all(
            isinstance(group, str) for group in groups
        ):
            raise AccessDenied()

        # Both groups may be present: admin takes precedence.
        is_admin = "admin" in groups
        if not is_admin and "user" not in groups:
            raise AccessDenied()

        if validation.get("email_verified") is not True:
            raise AccessDenied()

        email = validation.get("email")
        subject = validation.get("sub")
        if not isinstance(email, str) or not email.strip():
            raise AccessDenied()
        if not isinstance(subject, str) or not subject.strip():
            raise AccessDenied()

        access_token = params.get("access_token")
        if not access_token:
            raise AccessDenied()

        Users = self.sudo()
        existing = Users.search([
            ("oauth_provider_id", "=", provider),
            ("oauth_uid", "=", subject),
        ], limit=2)
        if len(existing) != 1 and existing:
            raise AccessDenied()

        if existing:
            # Never silently turn a former admin into an admin again
            # without a fresh admin group claim.
            desired_group_ids = [
                self.env.ref("base.group_user").id,
            ]
            if is_admin:
                desired_group_ids += [
                    self.env.ref("base.group_erp_manager").id,
                    self.env.ref("base.group_system").id,
                ]

            managed_group_ids = {
                self.env.ref("base.group_erp_manager").id,
                self.env.ref("base.group_system").id,
            }
            preserved = set(existing.group_ids.ids) - managed_group_ids
            existing.write({
                "group_ids": [Command.set(list(preserved | set(desired_group_ids)))],
                "oauth_access_token": access_token,
            })
            request.update_env(user=SUPERUSER_ID)
            return existing.login

        normalized_email = email.strip().lower()
        if Users.search([("login", "=ilike", normalized_email)], limit=1):
            _logger.warning("OIDC provisioning rejected: login already exists")
            raise AccessDenied()

        group_ids = [self.env.ref("base.group_user").id]
        if is_admin:
            group_ids.extend([
                self.env.ref("base.group_erp_manager").id,
                self.env.ref("base.group_system").id,
            ])

        name = validation.get("name")
        if not isinstance(name, str) or not name.strip():
            name = normalized_email

        user = Users.with_context(no_reset_password=True).create({
            "name": name.strip(),
            "login": normalized_email,
            "email": normalized_email,
            "oauth_provider_id": provider,
            "oauth_uid": subject,
            "oauth_access_token": access_token,
            "group_ids": [Command.set(group_ids)],
        })
        _logger.warning(
            "OIDC env check: self_uid=%s; users_uid=%s; request_uid=%s; request_user_ids=%s",
            self.env.uid,
            Users.env.uid,
            request.env.uid,
            request.env.user.ids,
        )
        _logger.info("OIDC user provisioned: uid=%s; role=%s",
                     user.id, "admin" if is_admin else "user")
        request.update_env(user=SUPERUSER_ID)
        return user.login
