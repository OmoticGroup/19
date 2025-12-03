/** @odoo-module **/

import { WebsiteSale } from '@website_sale/interactions/website_sale';
import { registry } from '@web/core/registry';

// We are trying to remove JQuery dependencies with this new Odoo19 with our custom codes
export class CustomWebsiteSale extends WebsiteSale {

    dynamicContent = Object.assign({}, super.dynamicContent, {
        '.o-mail-custom-stars i': { 't-on-click': this.clickStars },
    });

    setup() {
        super.setup();
        this.orm = this.services.orm;
    }

    clickStars(ev) {
        const currentStar = ev.currentTarget;
        const starsContainer = currentStar.closest('.o-mail-custom-stars');
        const allStars = starsContainer.querySelectorAll('i');
        const currentIndex = Array.from(allStars).indexOf(currentStar);

        allStars.forEach((star, index) => {
            if (index <= currentIndex) {
                star.classList.add('fa-star');
                star.classList.remove('fa-star-o');
            } else {
                star.classList.add('fa-star-o');
                star.classList.remove('fa-star');
            }
        });

        const form = currentStar.closest('form');
        const feedbackInput = form?.querySelector('input.feedback_count');
        if (feedbackInput) {
            feedbackInput.value = currentIndex + 1;
        }
    }
}

registry.category('public.interactions').add('website_product_review.website_sale', CustomWebsiteSale);
