from odoo import models, fields, api
from odoo.exceptions import ValidationError


class TransportVehicleAssignment(models.Model):
    _name = 'transport.vehicle.assignment'
    _description = 'Vehicle Assignment'
    _rec_name = 'assignment_code'
    _order = 'assigned_date desc'

    assignment_code = fields.Char(
        string="Assignment ID",
        default="New",
        readonly=True,
        copy=False
    )

    driver_id = fields.Many2one(
        'transport.driver',
        string="Driver",
        required=True,
        domain="[('status', '=', 'active')]"
    )

    vehicle_id = fields.Many2one(
        'fleet.vehicle',
        string="Vehicle",
        required=True,
        domain="[('transport_status', '=', 'available')]"
    )

    assigned_date = fields.Date(
        string="Assigned Date",
        default=fields.Date.today,
        required=True
    )

    released_date = fields.Date(string="Released Date")

    status = fields.Selection([
        ('assigned', 'Assigned'),
        ('released', 'Released')
    ], string="Status", default='assigned', required=True)

    notes = fields.Text(string="Notes")

    @api.model
    def create(self, vals):
        if vals.get('assignment_code', 'New') == 'New':
            vals['assignment_code'] = self.env['ir.sequence'].next_by_code(
                'transport.vehicle.assignment'
            ) or 'New'

        record = super().create(vals)

        if record.status == 'assigned':
            record.vehicle_id.write({
                'transport_status': 'assigned',
                'assigned_driver_id': record.driver_id.id,
            })

        return record

    def write(self, vals):
        result = super().write(vals)

        for record in self:
            if record.status == 'assigned':
                record.vehicle_id.write({
                    'transport_status': 'assigned',
                    'assigned_driver_id': record.driver_id.id,
                })

            elif record.status == 'released':
                record.vehicle_id.write({
                    'transport_status': 'available',
                    'assigned_driver_id': False,
                })

        return result

    @api.constrains('driver_id', 'vehicle_id', 'status')
    def _check_active_assignment(self):
        for record in self:
            if record.status != 'assigned':
                continue

            driver_exists = self.search([
                ('driver_id', '=', record.driver_id.id),
                ('status', '=', 'assigned'),
                ('id', '!=', record.id),
            ], limit=1)

            if driver_exists:
                raise ValidationError(
                    "This driver is already assigned to another vehicle."
                )

            vehicle_exists = self.search([
                ('vehicle_id', '=', record.vehicle_id.id),
                ('status', '=', 'assigned'),
                ('id', '!=', record.id),
            ], limit=1)

            if vehicle_exists:
                raise ValidationError(
                    "This vehicle is already assigned to another driver."
                )

    @api.constrains('assigned_date', 'released_date')
    def _check_dates(self):
        for record in self:
            if record.released_date and record.released_date < record.assigned_date:
                raise ValidationError(
                    "Released Date cannot be before Assigned Date."
                )