from odoo import models, fields

class Department(models.Model):
    _name = 'hms.department'
    _description = 'Department'

    name = fields.Char('Department Name', required=True)
    capacity = fields.Integer('Capacity')  # Added a 'Capacity' field
    is_opened = fields.Boolean('Is Opened', default=True)  # Added a 'Is Opened' field
    patients = fields.One2many('hms.patient', 'department_id', string='Patients')  # Updated to reflect the relation
