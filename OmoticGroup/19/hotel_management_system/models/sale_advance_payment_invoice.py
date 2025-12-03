# -*- coding: utf-8 -*-
##########################################################################
# Author : Webkul Software Pvt. Ltd. (<https://webkul.com/>;)
# Copyright(c): 2017-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>;
##########################################################################\

from odoo import fields, models, api, _

class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def create_invoices(self):
        for order in self.sale_order_ids:
            if order.booking_count >= 1:
                return self.env["wk.wizard.message"].genrated_message(
                    "<span class='text-danger' style='font-weight:bold;'>Can not create invoice for a booking from the sale order %s directly <br/> Go to the related bookings and create invoice from there!</span>"
                    % order.name,
                    name="Warning",
                )
        return super(SaleAdvancePaymentInv, self).create_invoices()