/** @odoo-module **/

/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */

import { PaymentForm } from "@payment/interactions/payment_form";
import { registry } from '@web/core/registry';

export class HotelPaymentForm extends PaymentForm {

    _prepareTransactionRouteParams() {
        const transactionRouteParams = super._prepareTransactionRouteParams(...arguments);
        const searchParams = new URLSearchParams(window.location.search);
        let order_id = searchParams.has('order_id') ? searchParams.get('order_id') : 0;
        console.log('--> Order ID from URL:', order_id);

        return {
            ...transactionRouteParams,
            'advance_payment_order_id': order_id,
        };
    }
}

registry.category('public.interactions').add('hotel_management_system.payment_form', HotelPaymentForm);
