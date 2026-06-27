from odoo import models, fields, api


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    _sql_constraints = [
        (
            'unique_license_plate',
            'unique(license_plate)',
            'License Plate must be unique!'
        ),
    ]


    transport_vehicle_code = fields.Char(
        string="Vehicle Code",
        default="New",
        readonly=True,
        copy=False
    )

    seating_capacity = fields.Integer(string="Seating Capacity")
    current_odometer = fields.Float(string="Current Odometer")

    transport_vehicle_type = fields.Selection([
        ('car', 'Car'),
        ('van', 'Van'),
        ('bus', 'Bus'),
        ('lorry', 'Lorry'),
        ('bike', 'Bike'),
    ], string="Transport Vehicle Type")

    transport_status = fields.Selection([
        ('available', 'Available'),
        ('assigned', 'Assigned'),
        ('on_trip', 'On Trip'),
        ('maintenance', 'Maintenance'),
        ('inactive', 'Inactive'),
    ], string="Transport Status", default='available')

    assigned_driver_id = fields.Many2one(
    'transport.driver',
    string="Assigned Driver",
    domain="[('status', '=', 'active')]"
       )
    
    
    @api.model
    def create(self, vals):
        if vals.get('transport_vehicle_code', 'New') == 'New':
            vals['transport_vehicle_code'] = self.env['ir.sequence'].next_by_code(
                'transport.vehicle'
            ) or 'New'
        return super().create(vals)