from odoo import fields, models, api


class CustomerHierarchy(models.Model):
    _name = 'customer.hierarchy'
    _description = 'Customer Hierarchy'
    _rec_name = 'parent_id'

    parent_id = fields.Many2one('res.users')
    position = fields.Char()
    children_ids = fields.One2many('hierarchy.children', 'hierarchy_id')


class HierarchyChildren(models.Model):
    _name = 'hierarchy.children'
    _description = 'Hierarchy Children'

    hierarchy_id = fields.Many2one('customer.hierarchy')
    partner_id = fields.Many2one('res.users')
    position = fields.Char(compute='find_job_title')
    sequence_show = fields.Integer(related='sequence')
    sequence = fields.Integer('Sequence', default=0)

    @api.depends('partner_id')
    def find_job_title(self):
        for rec in self:
            employee = self.env['hr.employee'].search(
                [('user_id', '=', rec.partner_id.id)], limit=1)
            if employee:
                rec.position = employee.job_title
            else:
                rec.position = ''
