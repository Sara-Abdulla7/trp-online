odoo.define('ks_website_snippets.ks_website_snippets_partner', function (require) {
 'use strict';
    var core = require('web.core');
    var _t = core._t;
    var globalVariable;
    const options = require('web_editor.snippets.options');
    const ajax = require('web.ajax');
    const { Component, useExternalListener, onMounted } = owl;
    const QWeb = core.qweb;

    options.registry.SpecialPartner = options.registry.SelectTemplate.extend({
        /**
         * @constructor
         */
        init() {
            this._super(...arguments);
            this.selectTemplateWidgetName = 'ks_website_snippets_partner';
            this.renderTemplate()
        },
        async renderTemplate(){
            const response = await ajax.jsonRpc("/partner/snippet", 'call', {
            });
            if (response.qcontext == 'No Data Found'){
            }else{
                response.qcontext[0].set_active=true;
            }
            const temp =  QWeb.render('ks_website_snippets.partner_snippet_tmp',{'customer':response.qcontext});
            this.containerEl.insertAdjacentHTML('beforeend',temp);
        },
    });
    return {
        SpecialPartner: options.registry.SpecialPartner,
    };
});
