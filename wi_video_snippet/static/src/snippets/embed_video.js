/** @odoo-module **/

import { BaseOptionComponent } from "@html_builder/core/utils";
import { _t } from "@web/core/l10n/translation";
import { renderToMarkup } from "@web/core/utils/render";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { Plugin } from "@html_editor/plugin";
import { withSequence } from "@html_editor/utils/resource";
import { BEGIN } from "@html_builder/utils/option_sequence";
import { registry } from "@web/core/registry";
import { BuilderAction } from "@html_builder/core/builder_action";

export class EmbedVideoOption extends BaseOptionComponent {
    static template = "wi_video_snippet.wi_video_embed_options";
 }

export class EmbedVideoPlugin extends Plugin {
    static id = "EmbedVideoPlugin";

    resources = {
        builder_options: [
            withSequence(BEGIN, {
                selector: ".wi_video_embed",
                OptionComponent: EmbedVideoOption,
                props: {},
            }),
        ],
        builder_actions: {
            EmbedVideoAction,
        },
    };
}


export class EmbedVideoAction extends BuilderAction {
    static id = "EmbedVideoAction";
    async load({ editingElement }) {
        debugger
        const container = editingElement.querySelector(".wi_video_embed_embedded_class");
        debugger

        await new Promise((resolve) => {
            this.services.dialog.add(ConfirmationDialog, {
                title: _t("Add Video URL"),
                body: renderToMarkup("wi_video_snippet.embed_video_dialog"),
                confirm: () => {
                    const src = document.querySelector("#video_url").value;
                    if (editingElement.querySelector('video')){
                        editingElement.querySelector('video').remove()
                    }
                    const videoHtml = `
                        <video class="w-100" controls autoplay loop preload="auto">
                            <source src="${src}">
                        </video>`;
                    container.insertAdjacentHTML("afterend", videoHtml);
                    container.classList.add("d-none");
                    resolve();
                },
                cancel: () => resolve(),
            });
        });
    }
}


registry.category("website-plugins").add(EmbedVideoPlugin.id, EmbedVideoPlugin);
