
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class MuneefHRCustom(models.Model):
    _inherit = 'hr.employee'

    
    identification_id = fields.Char(string='Identification No', tracking=True, required=True)
    laborer_status = fields.Selection([('working', 'Working'),('not_working','Not Working'),('ready', 'Ready'),('out of service', 'Out Of Service'),('holiday','Holiday'),],default='not_working' ,string="Laborers Status")
    laborer = fields.Boolean(string="Is laborers")
    hq = fields.Boolean(string="HQ")
    finance_manager = fields.Many2one('hr.employee',string='Finance Manager')
    is_check = fields.Boolean(string='Is Check')
    project_id = fields.Many2one('project.project',string='Project')
    laborer_type = fields.Selection([('retainer', 'Retainer'),('not_retainer','Not Retainer'),],string="Laborer Type")
    institution = fields.Selection([('under', 'Under Institution'),('outside','Outside The Institution'),],string="Employee Status")
    in_project = fields.Boolean(string='Is Project')

    @api.constrains('name', 'identification_id')
    def _check_name(self):
        if self.identification_id:
            employee_identity_id = self.env['hr.employee'].search(
                [('identification_id', '=', self.identification_id), ('id', '!=', self.id)])
            if employee_identity_id:
                raise UserError(('Identification Number of the Employee Already Exists!'))

    @api.onchange('laborer')
    def check_if_hqs(self):
        if self.laborer != True:
            self.hq = True
        else:
            self.hq = False

    @api.onchange('hq')
    def check_if_laborera(self):
        if self.hq != True:
            self.laborer = True
        else:
            self.laborer = False

    # @api.model
    # def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
    #     args = args or []
    #     domain = []
    #     if name:
    #         domain = [('identification_id', 'ilike',name)]
    #     return self._search(domain + args,limit=limit, access_rights_uid=name_get_uid)

    @api.onchange('laborer_status')
    def check_out_of_service(self):
        project_id = self.env['project.project'].search([('state','!=','close'),('state','!=','cancel')]).mapped('staff_ids')
        project_id2 = self.env['transfer.details'].search([])


        for rec in project_id2:
            if rec.employee_id.name ==self.name:
                rec.state = self.laborer_status
        for rec in project_id:
            if rec.employee_id.name == self.name:
                rec.laborer_status = self.laborer_status







    





            






  