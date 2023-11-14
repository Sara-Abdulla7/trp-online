odoo.define('ks_website_snippets.ks_website_snippets_options', function (require) {
 'use strict';
    var core = require('web.core');
    var _t = core._t;
    var globalVariable;
    const options = require('web_editor.snippets.options');
    const ajax = require('web.ajax');
    const { Component, useExternalListener, onMounted } = owl;
    const QWeb = core.qweb;

    options.registry.SpecialProduct = options.registry.SelectTemplate.extend({
        /**
         * @constructor
         */
        init() {
            this._super(...arguments);
            this.selectTemplateWidgetName = 'ks_website_snippets';
        },
        async selectTemplate(previewMode, widgetValue, params) {
            await this._templatesLoading;
            // Call the controller method with parameters
            const response = await ajax.jsonRpc("/website/snippet/special/render", 'call', {
                'template': widgetValue
            });
            if (previewMode === 'reset') {
                if (!this.beforePreviewNodes) {
                    return;
                }
                while (this.containerEl.lastChild) {
                    this.containerEl.removeChild(this.containerEl.lastChild);
                }
                for (const node of this.beforePreviewNodes) {
                    this.containerEl.appendChild(node);
                }
                this.beforePreviewNodes = null;
                return;
            }
            if (!this.beforePreviewNodes) {
                this.beforePreviewNodes = [...this.containerEl.childNodes];
            }
            while (this.containerEl.lastChild) {
                this.containerEl.removeChild(this.containerEl.lastChild);
            }
            if (response.qcontext == 'No Data Found'){
            }else{
                response.qcontext[0].set_active=true;
            }
            const temp =  QWeb.render(widgetValue,{'customer':response.qcontext});
            this.containerEl.insertAdjacentHTML('beforeend',temp);
            if (!previewMode) {
                this.beforePreviewNodes = null;
            }
        },
    });
    return {
        SpecialProduct: options.registry.SpecialProduct,
    };
});