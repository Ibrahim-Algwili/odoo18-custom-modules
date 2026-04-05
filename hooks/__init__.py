import logging

from odoo import SUPERUSER_ID, api

from . import hooks

_logger = logging.getLogger(__name__)


# You Should use the (env) not cr directly in the parameters
def _hemo_pre_init_hook(env):
    """here you can use database cursor and ORM in the new versions"""
    print("Hello this is pre_init_hook Called.")

    env.cr.execute(
        """
                UPDATE res_partner
                SET mobile = '1234567'
                 WHERE mobile IS NULL
                """
    )
    print("pre_init_hook dont with SQL Query")

    # using env directly
    env["res.partner"].create({"name": "pre_init hook user"})


def _hemo_post_init_hook(env):
    """here you can use database cursor and ORM"""
    print("Hello this POST-INIT-HOOK Called.")

    env.cr.execute(
        """
                    UPDATE res_partner SET vat = 'SU45@D' WHERE vat IS NULL
                    """
    )

    # using ORM
    env["res.partner"].create({"name": "post_init hook user"})


def _hemo_uninstall_hook(env):
    print("hello this is UNINSTALL-HOOK Called.")

    env.cr.execute(
        """
            UPDATE res_partner
            SET vat = NULL
            WHERE vat = 'SU45@D'
        """
    )
    _logger.info("VAT updated for %d records", env.cr.rowcount)
