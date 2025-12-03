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
##########################################################################

from odoo import models, fields, _, api

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    guest_info_ids = fields.One2many(
        "guest.info", "sale_order_line_id", string="Members"
    )
    is_free_service = fields.Boolean(string="Is Free Service")
    warning = fields.Text(string="Warning For Sale Order Line", compute="_compute_warning", store=True, readonly=False)
    max_child = fields.Integer(related="product_template_id.max_child", string="Max Child")
    max_adult = fields.Integer(related="product_template_id.max_adult", string="Max Adult")
    max_occupancy = fields.Integer(related="product_template_id.max_occupancy", string="Max Occupancy")
    base_occupancy = fields.Integer(related="product_template_id.base_occupancy", string="Base Occupancy")
    extra_charge_per_person = fields.Monetary(related="product_template_id.extra_charge_per_person", string="Extra Charge per person")

    adult_guest = fields.Integer("Adult Guest")
    children_guest = fields.Integer("Child Guest")

    @api.depends('guest_info_ids', 'guest_info_ids.is_adult')
    def _compute_warning(self):
        for line in self:
            adult = sum(1 for guest in line.guest_info_ids if guest.is_adult)
            child = len(line.guest_info_ids) - adult
            
            total_guests = adult + child

            if not line.guest_info_ids:
                line.warning = "Please fill the members details !!"
            elif line.max_adult < adult and line.max_child < child:
                line.warning = "No. of Adult Guests and Child Guests cannot be greater than Max Adult and Child count"
            elif line.max_adult < adult:
                line.warning = "No. of Adult Guests cannot be greater than Max Adult count"
            elif line.max_child < child:
                line.warning = "No. of Child Guests cannot be greater than Max Child count"
            elif total_guests > line.max_occupancy:
                line.warning = "Total number of guests cannot exceed the maximum occupancy limit"
            else:
                line.warning = ""

    @api.onchange('guest_info_ids')
    def update_extra_price(self):
        for line in self:
            extra_cost=0
            if line.guest_info_ids:
                total_guests=len(line.guest_info_ids)
                if total_guests > line.base_occupancy:
                    extra_guests=total_guests-line.base_occupancy
                    if extra_guests > 0:
                        extra_cost=extra_guests*line.extra_charge_per_person
                        base_price = line.order_id.pricelist_id._get_product_price(line.product_id, line.product_uom_qty)
                        line.price_unit  = base_price + extra_cost