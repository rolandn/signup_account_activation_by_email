# -*- coding: utf-8 -*-

import logging
import werkzeug

from odoo import http, _
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.http import request

_logger = logging.getLogger(__name__)

try:
    from validate_email import validate_email
except ImportError:
    _logger.debug("Cannot import `validate_email`.")


class SignupVerifyEmail(AuthSignupHome):
    @http.route()
    def web_auth_signup(self, *args, **kw):
        return self.passwordless_signup(http.request.params)

    def passwordless_signup(self, values):
        qcontext = self.get_auth_signup_qcontext()

        if not values.get("login"):
            return http.request.render("auth_signup.signup", qcontext)

        if not (values.get("login") or values.get("password") or values.get("confirm_password")):
            qcontext["error"] = _("Required field are missing.")
            return http.request.render("auth_signup.signup", qcontext)

        # Check field values are valid
        # if not validate_email(values.get("login", "")):
        #     qcontext["error"] = _("That does not seem to be an email address.")
        #     return http.request.render("auth_signup.signup", qcontext)
        # elif values.get("password") != values.get("confirm_password"):
        #     qcontext["error"] = _("Password and Confirm Password does't match.")
        #     return http.request.render("auth_signup.signup", qcontext)
        # elif not values.get("email"):
        #     values["email"] = values.get("login")

        sudo_users = (http.request.env["res.users"].with_context(create_user=True).sudo())

        try:
            sudo_users.activate_signup(values, qcontext.get("token"))
            sudo_users.account_active(values.get("login"))
        except Exception as error:
            _logger.exception(error)
            http.request.env.cr.rollback()
            qcontext["error"] = _("Something went wrong, please try again later.")
            return http.request.render("auth_signup.signup", qcontext)

        welcome_msg = """Thank you for your registration. \
            An E-Mail has been send to you, kindly authenticate your email address."""
        qcontext["message"] = _(welcome_msg)
        return http.request.render("auth_signup.reset_password", qcontext)

    @http.route('/web/activate', type='http', auth='public', website=True)
    def web_signup_account_active(self, *args, **kw):
        qcontext = self.get_auth_signup_qcontext()

        if not qcontext.get('token'):
            raise werkzeug.exceptions.NotFound()

        if 'error' not in qcontext and request.httprequest.method == 'GET':
            try:
                User = request.env['res.users'].sudo().search(
                    [('login', '=', qcontext.get('login')), ('active', '=', False)])
                if User.partner_id.signup_token == qcontext['token']:
                    User.partner_id.signup_token = False
                    User.partner_id.signup_type = False
                    User.partner_id.signup_expiration = False
                    User.active = True

                    qcontext["message"] = _("Your account activated.")
                    return werkzeug.utils.redirect('/web/login')
                else:
                    qcontext['error'] = _("Invalid or expired token number.")
            except Exception, e:
                qcontext['error'] = _(e.message)

            return http.request.render("auth_signup.signup", qcontext)
