# custom_addons/hms/models/patient.py
from odoo import models, fields, api
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError

class Patient(models.Model):
    _name = 'hms.patient'
    _description = 'Patient'

    first_name = fields.Char('First Name', required=True)
    last_name = fields.Char('Last Name', required=True)
    birth_date = fields.Date('Birth Date')
    blood_type = fields.Selection([
        ('A', 'A'),
        ('A-', 'A-'),
        ('B', 'B'),
        ('B-', 'B-'),
        ('AB', 'AB'),
        ('AB-', 'AB-'),
        ('O', 'O'),
        ('O-', 'O-'),
    ], string="Blood Type")
    pcr = fields.Boolean('PCR Checked', default=False)
    history = fields.Text('History')
    department_id = fields.Many2one('hms.department', string='Department', ondelete='set null', domain="[('is_opened', '=', True)]")
    department_capacity = fields.Integer('Department Capacity', compute='_compute_department_capacity', store=True)
    doctor_ids = fields.Many2many('hms.doctor', string='Doctors')
    doctor_full_name = fields.Char('Doctor Full Name', compute='_compute_doctor_full_name')
    state = fields.Selection([
        ('undetermined', 'Undetermined'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('serious', 'Serious')
    ], string='State', default='undetermined')
    address = fields.Char('Address')
    image = fields.Image('Image')
    cr_ratio = fields.Float('CR Ratio')
    age = fields.Integer('Age', compute='_compute_age', store=True)
    log_ids = fields.One2many('hms.patient.log', 'patient_id', string='Log History')

    @api.depends('birth_date')
    def _compute_age(self):
        for record in self:
            if record.birth_date:
                today = fields.Date.today()
                delta = relativedelta(today, record.birth_date)
                record.age = delta.years
            else:
                record.age = 0

    @api.depends('department_id.capacity')
    def _compute_department_capacity(self):
        for record in self:
            record.department_capacity = record.department_id.capacity if record.department_id else 0

    @api.depends('doctor_ids')
    def _compute_doctor_full_name(self):
        for record in self:
            if record.doctor_ids:
                record.doctor_full_name = ', '.join(f"{doctor.first_name} {doctor.last_name}" for doctor in record.doctor_ids)
            else:
                record.doctor_full_name = 'No doctor assigned'

    @api.onchange('birth_date')
    def _onchange_birth_date(self):
        for record in self:
            record._compute_age()

            warnings = []

            # PCR: Checked if age < 30
            if record.age < 30 and not record.pcr:
                record.pcr = True
                warnings.append('PCR has been checked because the age is less than 30.')
            elif record.age >= 30 and record.pcr:
                record.pcr = False
                warnings.append('PCR has been unchecked because the age is 30 or greater.')

            # Clear history if age <= 50
            if record.age <= 50 and record.history:
                record.history = False
                warnings.append('Patient history has been hidden because the age is 50 or less.')

            # Warn if PCR checked but no CR ratio
            if record.pcr and not record.cr_ratio:
                warnings.append('Please enter the CR Ratio because PCR is checked.')

            if warnings:
                return {
                    'warning': {
                        'title': 'Patient Info Updated',
                        'message': '\n'.join(warnings)
                    }
                }

    @api.constrains('pcr', 'cr_ratio')
    def _check_cr_ratio_required(self):
        for record in self:
            if record.pcr and not record.cr_ratio:
                raise ValidationError('CR Ratio must be filled when PCR is checked.')

    def write(self, vals):
        """Create a log entry when the state changes."""
        if 'state' in vals:
            state_name = dict(self._fields['state'].selection).get(vals['state'], vals['state'])
            for patient in self:
                self.env['hms.patient.log'].create({
                    'patient_id': patient.id,
                    'description': f'State changed to {state_name}',
                    'created_by': self.env.user.id,
                    'date': fields.Datetime.now(),
                })
        return super(Patient, self).write(vals)
