odoo.define('ks_website_snippets.employee_snippet', function (require) {
   var PublicWidget = require('web.public.widget');
   var rpc = require('web.rpc');
   var core =  require('web.core');
   var Qweb = core.qweb;
   var EmployeeMonth = PublicWidget.Widget.extend({
          selector: '.employee_of_the_month',
           start: async function () {
           var self = this;
           await rpc.query({
               route: '/employee/of/the/month',
               params: {},
           }).then(function (res) {
           $('.employee_month').empty();
           $('.employee_month').append(Qweb.render('ks_website_snippets.employee_of_the_month',{'res': res}));
           });
        },
   });
   PublicWidget.registry.dynamic_snippet_employee = EmployeeMonth;
   return EmployeeMonth;
});
