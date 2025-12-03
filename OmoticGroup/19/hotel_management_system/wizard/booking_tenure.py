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
from odoo import api, fields, models

class BookingTenureWizard(models.TransientModel):
    _name = 'booking.tenure.wizard'
    _description = "Reschedule Stay Wizard"


    booking_id = fields.Many2one('hotel.booking', required=True)
    check_in = fields.Datetime(required=True)
    check_out = fields.Datetime(required=True)
    warning = fields.Char(readonly=True)
    available = fields.Boolean(default=False, readonly=True)

    @api.onchange('check_in', 'check_out')
    def _onchange_check_dates(self):
        res = self.booking_id.check_selected_rooms_availability(self.check_in, self.check_out)
        self.warning = res['message']
        self.available = res['available']

    def action_confirm_tenure_update(self):
        '''
        NEW IMP - EXPERIMENTAL w/ check_in & check_out
        -> Did some extra message post part in this method to reserve the order line description
        '''
        self.ensure_one()
        
        current_datetime = fields.Datetime.now()
        check_in_editable = self.env.context.get('status') != 'allot'
     
        booking_vals = {'check_out': self.check_out}
        if check_in_editable:
            booking_vals['check_in'] = self.check_in
        
        self.booking_id.write(booking_vals)

        if check_in_editable:
            all_booking_lines = self.booking_id.booking_line_ids
            
            for line in all_booking_lines:
                line.write({
                    'check_in': self.check_in,
                    'check_out': self.check_out
                })
            
                if line.sale_order_line_id:
                    new_days = (self.check_out.date() - self.check_in.date()).days or 1

                    chatter_message = line.description or ""

                    if chatter_message:
                        line.sale_order_line_id.order_id.message_post(
                            body=chatter_message,
                            subject=f"Exchange Details - {line.sale_order_line_id.product_id.display_name}",
                            message_type='comment',
                            subtype_xmlid='mail.mt_comment'
                        )
                    
                    line.sale_order_line_id.write({
                        'product_uom_qty': new_days,
                        'name': f"{line.product_id.name} ({self.check_in.date()} to {self.check_out.date()})"
                    })
                    
            print(f"Full rescheduling completed. Updated {len(all_booking_lines)} booking lines (both check_in and check_out).")
            
        else:
            future_booking_lines = self.booking_id.booking_line_ids.filtered(
                lambda line: line.check_out > current_datetime
            )
            
            for line in future_booking_lines:
                line.write({'check_out': self.check_out})
            
                if line.sale_order_line_id:
                    new_days = (self.check_out.date() - line.check_in.date()).days or 1

                    chatter_message = line.description or ""

                    if chatter_message:
                        line.sale_order_line_id.order_id.message_post(
                            body=chatter_message,
                            subject=f"Exchange Details - {line.sale_order_line_id.product_id.display_name}",
                            message_type='comment',
                            subtype_xmlid='mail.mt_comment'
                        )
                    
                    line.sale_order_line_id.write({
                        'product_uom_qty': new_days,
                        'name': f"{line.product_id.name} ({line.check_in.date()} to {self.check_out.date()})"
                    })
                    
        order = self.booking_id.order_id
        if order:
            order_vals = {'hotel_check_out': self.check_out}
            if check_in_editable:
                order_vals['hotel_check_in'] = self.check_in
                
            order.with_context(bypass_checkin_checkout=True).write(order_vals)
            
        return {'type': 'ir.actions.act_window_close'}
