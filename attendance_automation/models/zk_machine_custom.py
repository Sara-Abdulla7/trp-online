from odoo import models, fields,api,_
from datetime import date,datetime
from odoo.exceptions import UserError, ValidationError

class HrAttendanceMachine(models.Model):
	_inherit = 'hr.attendance'

	def _check_validity_check_in_check_out(self):
		res =super(HrAttendanceMachine,self)._check_validity_check_in_check_out()
		if attendance.check_out < attendance.check_in:
			return False


	def _check_validity(self):
		res =super(HrAttendanceMachine,self)._check_validity()
		if last_attendance_before_check_in and last_attendance_before_check_in.check_out and last_attendance_before_check_in.check_out > attendance.check_in:
			return False






