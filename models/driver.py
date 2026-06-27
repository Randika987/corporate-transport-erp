from odoo import models, fields,api



class TransportDriver(models.Model):
    _name = 'transport.driver'
    _description = 'Transport Driver'
    _rec_name = 'name'

    _sql_constraints = [

    (
    'unique_driver_code',
    'unique(driver_code)',
    'Driver Code already exists!'
     ),    
    (
        'unique_nic',
        'unique(nic)',
        'NIC Number already exists!'
    ),
    (
        'unique_license',
        'unique(license_number)',
        'License Number already exists!'
    ),
]

    driver_code = fields.Char(string="Driver Code", default="New", readonly=True)
    name = fields.Char(string="Driver Name", required=True)
    photo = fields.Image(string="Photo")

    nic = fields.Char(string="NIC Number")
    phone = fields.Char(string="Phone Number")
    email = fields.Char(string="Email")
    address = fields.Text(string="Address")
    emergency_contact = fields.Char(string="Emergency Contact")

    license_number = fields.Char(string="License Number")
    license_class = fields.Selection([
        ('A', 'A - Motorcycle'),
        ('B', 'B - Car/Van'),
        ('C', 'C - Heavy Vehicle'),
        ('D', 'D - Bus')
    ], string="License Class")
    license_expiry = fields.Date(string="License Expiry")

    assigned_vehicle_id = fields.Many2one(
        'fleet.vehicle',
        string="Assigned Vehicle"
    )

    experience_years = fields.Integer(string="Experience Years")

    status = fields.Selection([
        ('active', 'Active'),
        ('leave', 'On Leave'),
        ('suspended', 'Suspended'),
        ('inactive', 'Inactive')
    ], string="Status", default='active')

    @api.model
    def create(self, vals):
        if vals.get('driver_code', 'New') == 'New':
            vals['driver_code'] = self.env['ir.sequence'].next_by_code('transport.driver') or 'New'
        return super(TransportDriver, self).create(vals)