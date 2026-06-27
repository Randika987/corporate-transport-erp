from odoo import models, fields, api
from odoo.exceptions import ValidationError


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

    transport_vehicle_type = fields.Selection([
        ('car', 'Car'),
        ('van', 'Van'),
        ('bus', 'Bus'),
        ('lorry', 'Lorry'),
        ('bike', 'Bike'),
    ], string="Transport Vehicle Type", required=True)

    seating_capacity = fields.Integer(
        string="Seating Capacity",
        required=True
    )

    current_odometer = fields.Float(
        string="Current Odometer",
        default=0.0
    )

    transport_status = fields.Selection([
        ('available', 'Available'),
        ('assigned', 'Assigned'),
        ('on_trip', 'On Trip'),
        ('maintenance', 'Maintenance'),
        ('inactive', 'Inactive'),
    ], string="Transport Status", default='available', required=True)

    assigned_driver_id = fields.Many2one(
        'transport.driver',
        string="Assigned Driver",
        required=True,
        domain="[('status', '=', 'active')]"
    )

    @api.model
    def create(self, vals):
        if vals.get('transport_vehicle_code', 'New') == 'New':
            vals['transport_vehicle_code'] = self.env['ir.sequence'].next_by_code(
                'transport.vehicle'
            ) or 'New'
        return super().create(vals)

    @api.onchange('transport_vehicle_type')
    def _onchange_transport_vehicle_type(self):
        seat_map = {
            'car': 5,
            'van': 12,
            'bus': 45,
            'lorry': 2,
            'bike': 2,
        }
        self.seating_capacity = seat_map.get(self.transport_vehicle_type, 0)

    @api.constrains('seating_capacity')
    def _check_seating_capacity(self):
        for record in self:
            if record.seating_capacity <= 0:
                raise ValidationError("Seating Capacity must be greater than zero.")

    @api.constrains('current_odometer')
    def _check_current_odometer(self):
        for record in self:
            if record.current_odometer < 0:
                raise ValidationError("Current Odometer cannot be negative.")