from odoo import models, fields

class PatientLog(models.Model):
    _name = 'hms.patient.log'
    _description = 'Patient Log History'

    patient_id = fields.Many2one('hms.patient', string='Patient', required=True, ondelete='cascade')
    created_by = fields.Many2one('res.users', string='Created By', default=lambda self: self.env.user, readonly=True)
    date = fields.Datetime('Date', default=fields.Datetime.now, readonly=True)
    description = fields.Text('Description', required=True)
