odoo.define('ks_website_snippets.customer_snippet', function (require) {
   var PublicWidget = require('web.public.widget');
   var rpc = require('web.rpc');
   var core =  require('web.core');
   var Qweb = core.qweb;
   var DynamicHierarchy = PublicWidget.Widget.extend({
          selector: '.hierarchy_special_products_options',
            start: async function () {
            var self = this;
           await rpc.query({
               route: '/customer/hierarchy',
               params: {},
           }).then(function (res) {
           $('.hierarchy_special_customers').empty();
           $('.hierarchy_special_customers').append(Qweb.render('ks_website_snippets.hierarchy_customer',{'res': res}));
           });
            },
   });
   PublicWidget.registry.dynamic_snippet_hierarchy = DynamicHierarchy;
   return DynamicHierarchy;
});
