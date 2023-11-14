# _*_ coding: utf-8 _*_
import qrcode
import vobject
import base64
from io import BytesIO

from odoo import models, fields, _, api


class HrQrGenerator(models.Model):
    _inherit = 'hr.employee'

    qr_code = fields.Binary("QR Code", compute='generate_hr_qr', store=True)

    @api.depends('name', 'job_title', 'mobile_phone', 'work_email')
    def generate_hr_qr(self):
        for rec in self:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            card = vobject.vCard()
            o = card.add('fn')
            o.value = rec.name or ''

            o = card.add('n')
            o.value = vobject.vcard.Name(family='', given=rec.name or '')

            o = card.add('tel')
            o.type_param = "cell"
            o.value = rec.mobile_phone or ''

            o = card.add('tel')
            o.type_param = "work"
            o.value = rec.work_phone or ''

            # o = card.add('tel')
            # o.type_param = "home"
            # o.value = '+49 181 99 00 00 00'

            o = card.add('org')
            o.value = rec.env.user.company_id.name or ''

            o = card.add('title')
            o.value = rec.job_title or ''

            o = card.add('url')
            o.value = rec.env.user.company_id.website or ''

            o = card.add('email')
            o.type_param = "pref"
            o.value = rec.work_email or ''

            print(card.serialize())
            qr.add_data(card.serialize())

            # Make the QR code
            qr.make(fit=True)

            # Create an image from the QR code
            img = qr.make_image(fill_color="black", back_color="white")

            tmp = BytesIO()
            img.save(tmp, format="PNG")
            qr_img = base64.b64encode(tmp.getvalue())
            rec.qr_code = qr_img

            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }
