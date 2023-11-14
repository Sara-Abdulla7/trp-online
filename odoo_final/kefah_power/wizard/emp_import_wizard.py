# -*- coding: utf-8 -*-
from odoo.exceptions import UserError, ValidationError
from odoo import models, fields, exceptions, api, _
from datetime import datetime, date
import io
import tempfile
import binascii
from decimal import Decimal
try:
    import xlrd
except ImportError:
    _logger.debug('Cannot `import xlrd`.')

class TimeSheetWizard(models.TransientModel):
    _name = 'emp.import.wizard'

    data_file = fields.Binary(string='XLS File')
    file_name = fields.Char('Filename')

    def action_import(self):
        if self.file_name:
            try:
                fp = tempfile.NamedTemporaryFile(delete= False,suffix=".xlsx")
                fp.write(binascii.a2b_base64(self.data_file))
                fp.seek(0)
                workbook = xlrd.open_workbook(fp.name)
                sheet = workbook.sheet_by_index(0)
            except Exception:
                raise UserError(_("Invalid file!"))

            reader = []
            emp_list = []
            emp_surc = []
            calendar = []

            keys = sheet.row_values(0)
            values = [sheet.row_values(i) for i in range(1,sheet.nrows)]
            for value in values:
                reader.append(dict(zip(keys, value)))

            project = self.env['project.project'].browse(self.env.context.get('active_id'))
            emp_warning = []
            for line in reader:
                emp = self.env['hr.employee'].search([('laborer','=',True),('identification_id','=',Decimal(line['identification_no']))])
                if not emp:
                    raise UserError(_(f'There is an Employee Has Wrong Identification Number!? Places Please check it'))
                else:
                    val = ({
                        'project_id':project.id,
                        'employee_id':emp.id,
                        })
                data = self.env['project.staff'].create(val)
                data.get_employee()








                








