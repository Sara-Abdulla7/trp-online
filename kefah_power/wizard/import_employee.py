# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
import io
import xlrd
import babel
import logging
import tempfile
import binascii
from io import StringIO
from datetime import date, datetime, time
from odoo import api, fields, models, tools, _
from decimal import Decimal
from odoo.exceptions import Warning, UserError, ValidationError
_logger = logging.getLogger(__name__)

try:
	import csv
except ImportError:
	_logger.debug('Cannot `import csv`.')
try:
	import xlwt
except ImportError:
	_logger.debug('Cannot `import xlwt`.')
try:
	import cStringIO
except ImportError:
	_logger.debug('Cannot `import cStringIO`.')
try:
	import base64
except ImportError:
	_logger.debug('Cannot `import base64`.')


class ImportEmployee(models.TransientModel):
	_name = 'import.employee'
	_description = 'Import Employee'

	file_type = fields.Selection([('CSV', 'CSV File'),('XLS', 'XLS File')],string='File Type', default='CSV')
	file = fields.Binary(string="Upload File")

	def import_employee(self):
		if not self.file:
			raise ValidationError(_("Please Upload File to Import Employee !"))

		if self.file_type == 'CSV':
			line = keys = ['name','job_title','mobile_phone','work_phone','work_email','department_id','address_id','gender','birthday']
			try:
				csv_data = base64.b64decode(self.file)
				data_file = io.StringIO(csv_data.decode("utf-8"))
				data_file.seek(0)
				file_reader = []
				csv_reader = csv.reader(data_file, delimiter=',')
				file_reader.extend(csv_reader)
			except Exception:
				raise ValidationError(_("Please Select Valid File Format !"))
				
			values = {}
			for i in range(len(file_reader)):
				field = list(map(str, file_reader[i]))
				values = dict(zip(keys, field))
				if values:
					if i == 0:
						continue
					else:
						res = self.create_employee(values)
		else:
			try:
				file = tempfile.NamedTemporaryFile(delete= False,suffix=".xlsx")
				file.write(binascii.a2b_base64(self.file))
				file.seek(0)
				values = {}
				workbook = xlrd.open_workbook(file.name)
				sheet = workbook.sheet_by_index(0)
			except Exception:
				raise ValidationError(_("Please Select Valid File Format !"))

			for row_no in range(sheet.nrows):
				val = {}
				if row_no <= 0:
					fields = list(map(lambda row:row.value.encode('utf-8'), sheet.row(row_no)))
				else:
					line = list(map(lambda row:isinstance(row.value, bytes) and row.value.encode('utf-8') or str(row.value), sheet.row(row_no)))
					values.update( {
							'name':line[0],
							'identification_id':line[1],
							'parent_id':line[2],
							'institution':line[3],
							'laborer': line[4],
							})
					res = self.create_employee(values)


	def create_employee(self, values):
		employee = self.env['hr.employee']
		parent_id = self.get_manger(values.get('parent_id'))
		laborer = True


		vals = {
				'name' : values.get('name'),
				'identification_id':Decimal(values.get('identification_id')),
				'parent_id':parent_id.id,
				'institution':values.get('institution'),
				'laborer':laborer,
				}

		if values.get('parent_id')=='':
			raise UserError(_('manager Field can not be Empty!'))

		res = employee.create(vals)
		return res

	def get_manger(self, name):
		manager = self.env['hr.employee'].search([('name', '=',name)],limit=1)
		if manager:
			return manager
		else:
			raise UserError(_('"%s" manager is not found in system !') % name)
