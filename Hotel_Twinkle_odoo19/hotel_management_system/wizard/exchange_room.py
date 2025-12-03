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
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)


class ExchangeRoom(models.TransientModel):
    _name = "exchange.room"
    _description = "Exchange rooms if available"

    booking_line_id = fields.Many2one(
        'hotel.booking.line', string='Reference No')
    price = fields.Float(related='booking_line_id.price',
                         string="Current Price")
    available_room_ids = fields.Many2many('product.product')
    exchange_room = fields.Many2one('product.product', string='Exchange Room')
    exchange_price = fields.Float(
        related="exchange_room.lst_price", string="Exchange Price")
    price_difference = fields.Float(
        compute='_compute_price_difference', store=True, string="Price Difference")
    warning = fields.Text(string="Warning In Exchange Rooms", store=True, readonly=False)

    @api.depends('exchange_room')
    def _compute_price_difference(self):
        for rec in self:
            if rec.exchange_room:
                booking_line = self.env['hotel.booking.line'].browse(
                    self._context.get("active_ids"))
                rec.price_difference = booking_line.price - rec.exchange_room.lst_price

                adult = sum(
                    1 for guest in rec.booking_line_id.guest_info_ids if guest.is_adult)
                child = len(rec.booking_line_id.guest_info_ids) - adult

                if adult > rec.exchange_room.max_adult or child > rec.exchange_room.max_child:
                    rec.warning = "The number of current guests exceeds the room's allowed limit."
                else:
                    rec.warning = ""

    @api.onchange('booking_line_id')
    def booking_line_compute(self):
        booking_line = self.env['hotel.booking.line'].browse(
            self._context.get("active_ids"))
        self.booking_line_id = booking_line
        booking = booking_line.booking_id
        self.available_room_ids = booking.get_available_room_products(
            booking.check_in, booking.check_out, booking.hotel_id.id, room_exchange=True)

    def action_exchange_room(self):
        '''
        NEW IMP - EXPERIMENTAL w/ check_in & check_out
        -> We have now managed multiple conditions here. A logic for same date exchange and a logic
        for different dates exchange room
        '''
        booking_line = self.env['hotel.booking.line'].browse(
            self._context.get("active_ids"))
        line = booking_line.sale_order_line_id

        if not (booking_line or line):
            return
        
        order = booking_line.sale_order_line_id.order_id

        if order:
            posted_invoice_count = len(
                order.invoice_ids.filtered(lambda i: i.state == 'posted'))

            if (posted_invoice_count):
                raise ValidationError(
                    _('You cannot exchange a room if an invoice or delivery has been created for the related sale order.'))
            elif (self.exchange_room):
                exchange_datetime = fields.Datetime.now()
                exchange_date = exchange_datetime.date().strftime('%Y-%m-%d')

                booking_check_in_date = booking_line.check_in.date() if booking_line.check_in else None
                
                if booking_check_in_date == exchange_datetime.date():
                    '''
                    CASE: For same day of exchange as check_in date
                    '''
                    old_room_name = booking_line.product_id.name
                
                    extra_cost = 0
                    if booking_line.guest_info_ids:
                        total_guests = len(booking_line.guest_info_ids)
                        if total_guests > self.exchange_room.product_tmpl_id.base_occupancy:
                            extra_guests = total_guests - self.exchange_room.product_tmpl_id.base_occupancy
                            extra_cost = extra_guests * self.exchange_room.product_tmpl_id.extra_charge_per_person

                    new_description = f"{old_room_name} Exchanged with {self.exchange_room.display_name} on {exchange_date}."
                    booking_line.with_context(bypass_for_exchange_room=True).write({
                        "product_id": self.exchange_room.id,
                        "price": self.exchange_room.lst_price + extra_cost,
                        "description": new_description,
                    })

                    order.with_context(bypass_for_exchange_room=True).write({'state': 'draft'})
                    line.unlink()
                    
                    sale_order_line = self.env['sale.order.line'].create({
                        'order_id': order.id,
                        'product_id': booking_line.product_id.id,
                        'tax_ids': [(6, 0, booking_line.tax_ids.ids)],
                        'price_unit': booking_line.price,
                        'product_uom_qty': booking_line.booking_days,
                        'guest_info_ids': [(6, 0, booking_line.guest_info_ids.ids)],
                        'name': f"{self.exchange_room.name}\n{new_description}",
                    })
                    
                    booking_line.with_context(bypass_for_exchange_room=True).write(
                        {"sale_order_line_id": sale_order_line.id})
                    
                    order.with_context(bypass_for_exchange_room=True).write({'state': 'sale'})
                    
                else:
                    '''
                    CASE: For different day of exchange
                    '''
                    original_product = booking_line.product_id
                    original_check_in = booking_line.check_in
                    original_check_out = booking_line.check_out
                    original_price = booking_line.price
                    original_tax_ids = booking_line.tax_ids.ids
                    original_discount = booking_line.discount
                    original_guest_info = booking_line.guest_info_ids

                    guest_info_data_for_old_room = []
                    guest_info_data_for_new_room = []
                    
                    for guest in original_guest_info:
                        guest_data = {
                            'name': guest.name,
                            'age': guest.age,
                            'gender': guest.gender,
                            'is_adult': guest.is_adult,
                        }
                        guest_info_data_for_old_room.append((0, 0, guest_data.copy()))
                        guest_info_data_for_new_room.append((0, 0, guest_data.copy()))

                    old_room_description = f"This room was occupied till {exchange_date}."

                    new_line_vals = {
                        'booking_id': booking_line.booking_id.id,
                        'product_id': original_product.id,
                        'check_in': original_check_in,
                        'check_out': exchange_datetime,
                        'guest_info_ids': guest_info_data_for_old_room,
                        'tax_ids': [(6, 0, original_tax_ids)],
                        'discount': original_discount,
                        'price': original_price,
                        'description': old_room_description,
                    }
                    
                    new_booking_line = self.env['hotel.booking.line'].create(new_line_vals)

                    old_room_days = (exchange_datetime.date() - original_check_in.date()).days or 1

                    old_room_sale_order_line = self.env['sale.order.line'].create({
                        'order_id': order.id,
                        'product_id': new_booking_line.product_id.id,
                        'tax_ids': [(6, 0, new_booking_line.tax_ids.ids)],
                        'price_unit': new_booking_line.price,
                        'product_uom_qty': old_room_days,
                        'guest_info_ids': guest_info_data_for_old_room,
                        'name': f"{original_product.name}\n{old_room_description}",
                    })

                    new_booking_line.with_context(bypass_for_exchange_room=True).write({
                        "sale_order_line_id": old_room_sale_order_line.id
                    })

                    extra_cost = 0
                    if booking_line.guest_info_ids:
                        total_guests = len(booking_line.guest_info_ids)
                        if total_guests > self.exchange_room.product_tmpl_id.base_occupancy:
                            extra_guests = total_guests - self.exchange_room.product_tmpl_id.base_occupancy
                            extra_cost = extra_guests * self.exchange_room.product_tmpl_id.extra_charge_per_person

                    new_room_description = f"{original_product.name} Exchanged with {self.exchange_room.name} on {exchange_date}."
 
                    booking_line.with_context(bypass_for_exchange_room=True).write({
                        "product_id": self.exchange_room.id,
                        "check_in": exchange_datetime,
                        "check_out": original_check_out,
                        "guest_info_ids": [(5, 0, 0)] + guest_info_data_for_new_room,
                        "price": self.exchange_room.lst_price + extra_cost,
                        "description": new_room_description,
                    })

                    new_room_days = (original_check_out.date() - exchange_datetime.date()).days or 1

                    order.with_context(bypass_for_exchange_room=True).write({'state': 'draft'})
                    line.unlink()  

                    new_room_sale_order_line = self.env['sale.order.line'].create({
                        'order_id': order.id,
                        'product_id': booking_line.product_id.id,
                        'tax_ids': [(6, 0, booking_line.tax_ids.ids)],
                        'price_unit': booking_line.price,
                        'product_uom_qty': new_room_days,
                        'guest_info_ids': guest_info_data_for_new_room,
                        'name': f"{self.exchange_room.name} - {new_room_description}",
                    })
                    
                    booking_line.with_context(bypass_for_exchange_room=True).write(
                        {"sale_order_line_id": new_room_sale_order_line.id})
                    
                    order.with_context(bypass_for_exchange_room=True).write({'state': 'sale'})

            templ_id = self.env.ref('hotel_management_system.hotel_booking_exchange_id')
            templ_id.send_mail(booking_line.booking_id.id, force_send=True)

            if booking_line.hotel_service_lines:
                hb_object = booking_line.booking_id.manage_alloted_services(is_checkout=False)
                if hb_object:
                    return hb_object
            
            return True
        else:
            return self.env['wk.wizard.message'].genrated_message("Exchange is not possible", name='Message')


class AvailableProduct(models.TransientModel):
    _name = "available.product"
    _description = "Available Rooms"

    name = fields.Char("Room Name")
    room_id = fields.Integer("Room Id", store=True)
    exchange_id = fields.Many2one("exchange.room")
    template_attribute_value_ids = fields.Many2many(
        'product.template.attribute.value', string="Attribute Values")
