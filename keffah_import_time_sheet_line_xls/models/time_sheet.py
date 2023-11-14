# -*- coding: utf-8 -*-
from odoo import models

class TimeSheetDetails(models.Model):
    _inherit = 'time.sheet.details'

    def action_time_sheet_import(self):
        action = self.env.ref('keffah_import_time_sheet_line_xls.action_time_sheet_import_wizard').read()[0]
        action.update({'views': [[False, 'form']]})
        return action
