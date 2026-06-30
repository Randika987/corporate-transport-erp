from odoo import models, fields, api
from odoo.exceptions import ValidationError


class TransportTrip(models.Model):
    _name = 'transport.trip'
    _description = 'Transport Trip'
    _rec_name = 'trip_code'
    _order = 'start_datetime desc'

    trip_code = fields.Char(
        string="Trip ID",
        default="New",
        readonly=True,
        copy=False
    )

    assignment_id = fields.Many2one(
        'transport.vehicle.assignment',
        string="Vehicle Assignment",
        required=True,
        domain="[('status', '=', 'assigned')]"
    )

    driver_id = fields.Many2one(
        related='assignment_id.driver_id',
        string="Driver",
        store=True,
        readonly=True
    )

    vehicle_id = fields.Many2one(
        related='assignment_id.vehicle_id',
        string="Vehicle",
        store=True,
        readonly=True
    )

    start_location = fields.Char(string="Start Location", required=True)
    destination = fields.Char(string="Destination", required=True)

    start_datetime = fields.Datetime(
        string="Start Date & Time",
        default=fields.Datetime.now,
        required=True
    )

    end_datetime = fields.Datetime(string="End Date & Time")

    start_odometer = fields.Float(string="Start Odometer")
    distance_km = fields.Float(string="Distance (KM)")
    end_odometer = fields.Float(string="End Odometer")

    trip_duration = fields.Float(
        string="Trip Duration (Hours)",
        compute="_compute_trip_duration"
    )

    purpose = fields.Char(string="Purpose")
    notes = fields.Text(string="Notes")

    status = fields.Selection([
        ('draft', 'Draft'),
        ('started', 'Started'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string="Trip Status", default='draft', required=True)

    @api.model
    def create(self, vals):
        if vals.get('trip_code', 'New') == 'New':
            vals['trip_code'] = self.env['ir.sequence'].next_by_code(
                'transport.trip'
            ) or 'New'

        record = super().create(vals)

        if record.assignment_id and record.assignment_id.vehicle_id and not record.start_odometer:
            record.start_odometer = record.assignment_id.vehicle_id.current_odometer

        return record

    @api.onchange('assignment_id')
    def _onchange_assignment_id(self):
        for record in self:
            if record.assignment_id and record.assignment_id.vehicle_id:
                record.start_odometer = record.assignment_id.vehicle_id.current_odometer

    @api.onchange('distance_km')
    def _onchange_distance_km(self):
        for record in self:
            if record.distance_km >= 0:
                record.end_odometer = record.start_odometer + record.distance_km

    def action_start_trip(self):
        for record in self:
            if not record.assignment_id:
                raise ValidationError(
                    "Please select a Vehicle Assignment before starting the trip."
                )

            record.status = 'started'
            record.vehicle_id.transport_status = 'on_trip'

    def action_complete_trip(self):
        for record in self:
            if record.distance_km <= 0:
                raise ValidationError(
                    "Please enter trip distance before completing the trip."
                )

            if not record.end_datetime:
                record.end_datetime = fields.Datetime.now()

            record.end_odometer = record.start_odometer + record.distance_km

            record.status = 'completed'
            record.vehicle_id.write({
                'transport_status': 'assigned',
                'current_odometer': record.end_odometer,
            })

    def action_cancel_trip(self):
        for record in self:
            record.status = 'cancelled'

    @api.depends('start_datetime', 'end_datetime')
    def _compute_trip_duration(self):
        for record in self:
            record.trip_duration = 0.0
            if record.start_datetime and record.end_datetime:
                duration = record.end_datetime - record.start_datetime
                record.trip_duration = duration.total_seconds() / 3600

    @api.constrains('start_datetime', 'end_datetime')
    def _check_trip_dates(self):
        for record in self:
            if record.end_datetime and record.end_datetime < record.start_datetime:
                raise ValidationError(
                    "End Date & Time cannot be before Start Date & Time."
                )

    @api.constrains('distance_km')
    def _check_distance(self):
        for record in self:
            if record.distance_km < 0:
                raise ValidationError("Distance cannot be negative.")

    @api.constrains('assignment_id', 'status')
    def _check_active_trip(self):
        for record in self:
            if record.status != 'started':
                continue

            existing_trip = self.search([
                ('assignment_id', '=', record.assignment_id.id),
                ('status', '=', 'started'),
                ('id', '!=', record.id),
            ], limit=1)

            if existing_trip:
                raise ValidationError(
                    "This vehicle already has an active trip."
                )