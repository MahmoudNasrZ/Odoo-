from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ResPartner(models.Model):
    _inherit = 'res.partner'
    #patientID
    related_patient_id = fields.Many2one('hms.patient', string='Related Patient')
    # get Patient Name By id
    related_patient_name = fields.Char(string='Patient Name', compute='_compute_related_patient_name', store=True)
    vat = fields.Char(string='Tax ID') #TaxID
    #Check Related Names
    @api.depends('related_patient_id')
    def _compute_related_patient_name(self):
        for partner in self:
            partner.related_patient_name = partner.related_patient_id.full_name if partner.related_patient_id else ''
    #Email Mytkrarsh
    @api.constrains('related_patient_id')
    def _check_related_patient_email_unique(self):
        for record in self:
            # Ensure the partner is a customer (type is 'contact' and is a company or individual)
            if record.related_patient_id and (record.type == 'contact' or record.is_company):
                domain = [
                    ('id', '!=', record.id),
                    ('type', '=', 'contact'),  # Looking for other contacts (customers)
                    ('related_patient_id.email', '=', record.related_patient_id.email),
                ]
                if self.search(domain, limit=1):
                    raise ValidationError('This patient email is already linked to another CRM customer.')
    # update Email lma y8yr al patient
    @api.onchange('related_patient_id')
    def _onchange_related_patient(self):
        if self.related_patient_id:
            self.email = self.related_patient_id.email  
    # tax id rquired true
    @api.constrains('vat', 'type')
    def _check_tax_id(self):
        for record in self:
            if (record.type == 'contact' or record.is_company) and not record.vat:
                raise ValidationError('Tax ID (VAT) is mandatory for CRM customers.')
