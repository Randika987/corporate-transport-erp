from odoo import models, fields, api


class TransportFleetOperation(models.Model):
    _name = 'transport.fleet.operation'
    _description = 'Fleet Operation'
    _rec_name = 'operation_code'
    _order = 'operation_date desc'

    operation_code = fields.Char(string="Operation ID", default="New", readonly=True, copy=False)

    trip_id = fields.Many2one(
        'transport.trip',
        string="Trip",
        required=True,
        domain="[('status', '=', 'completed')]"
    )

    vehicle_id = fields.Many2one(related='trip_id.vehicle_id', string="Vehicle", store=True, readonly=True)
    driver_id = fields.Many2one(related='trip_id.driver_id', string="Driver", store=True, readonly=True)

    operation_type = fields.Selection([
        ('fuel', 'Fuel'),
        ('maintenance', 'Maintenance')
    ], string="Operation Type", required=True)

    operation_date = fields.Date(string="Date", default=fields.Date.today, required=True)

    current_odometer = fields.Float(
        string="Current Odometer",
        compute="_compute_trip_values",
        store=True,
        readonly=True
    )

    trip_distance = fields.Float(
        string="Trip Distance (KM)",
        compute="_compute_trip_values",
        store=True,
        readonly=True
    )

    fuel_amount = fields.Float(string="Fuel Amount")
    fuel_price_per_liter = fields.Float(string="Price Per Liter")

    fuel_liters = fields.Float(
        string="Fuel Liters",
        compute="_compute_fuel_liters",
        store=True
    )

    fuel_efficiency = fields.Float(
        string="Fuel Efficiency (KM/L)",
        compute="_compute_fuel_statistics",
        store=True
    )

    cost_per_km = fields.Float(
        string="Cost Per KM",
        compute="_compute_fuel_statistics",
        store=True
    )

    service_type = fields.Selection([
        ('oil_change', 'Oil Change'),
        ('tire_service', 'Tire Service'),
        ('engine_repair', 'Engine Repair'),
        ('brake_service', 'Brake Service'),
        ('general_service', 'General Service'),
        ('other', 'Other')
    ], string="Service Type")

    workshop_name = fields.Char(string="Workshop")
    maintenance_cost = fields.Float(string="Maintenance Cost")
    next_service_odometer = fields.Float(string="Next Service Odometer")

    maintenance_status = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed')
    ], string="Maintenance Status", default='draft')

    service_due = fields.Boolean(
        string="Service Due",
        compute="_compute_service_due",
        store=True
    )

    notes = fields.Text(string="Notes")

    @api.model
    def create(self, vals):
        if vals.get('operation_code', 'New') == 'New':
            vals['operation_code'] = self.env['ir.sequence'].next_by_code(
                'transport.fleet.operation'
            ) or 'New'
        return super().create(vals)

    @api.depends('trip_id', 'trip_id.distance_km', 'trip_id.vehicle_id.current_odometer')
    def _compute_trip_values(self):
        for record in self:
            record.trip_distance = record.trip_id.distance_km if record.trip_id else 0.0
            record.current_odometer = (
                record.trip_id.vehicle_id.current_odometer
                if record.trip_id and record.trip_id.vehicle_id
                else 0.0
            )

    @api.depends('fuel_amount', 'fuel_price_per_liter')
    def _compute_fuel_liters(self):
        for record in self:
            if record.fuel_amount > 0 and record.fuel_price_per_liter > 0:
                record.fuel_liters = record.fuel_amount / record.fuel_price_per_liter
            else:
                record.fuel_liters = 0.0

    @api.depends('trip_distance', 'fuel_amount', 'fuel_liters')
    def _compute_fuel_statistics(self):
        for record in self:
            record.fuel_efficiency = 0.0
            record.cost_per_km = 0.0

            if record.trip_distance > 0:
                if record.fuel_liters > 0:
                    record.fuel_efficiency = record.trip_distance / record.fuel_liters
                if record.fuel_amount > 0:
                    record.cost_per_km = record.fuel_amount / record.trip_distance

    @api.onchange('service_type', 'current_odometer')
    def _onchange_service_type(self):
        service_intervals = {
            'oil_change': 5000,
            'tire_service': 10000,
            'brake_service': 15000,
            'engine_repair': 20000,
            'general_service': 10000,
            'other': 5000,
        }

        for record in self:
            if record.operation_type == 'maintenance' and record.service_type:
                interval = service_intervals.get(record.service_type, 5000)
                record.next_service_odometer = record.current_odometer + interval

    @api.depends('current_odometer', 'next_service_odometer')
    def _compute_service_due(self):
        for record in self:
            record.service_due = (
                record.next_service_odometer > 0 and
                record.current_odometer >= record.next_service_odometer
            )

    def action_start_maintenance(self):
        for record in self:
            record.maintenance_status = 'in_progress'
            if record.vehicle_id:
                record.vehicle_id.transport_status = 'maintenance'

    def action_complete_maintenance(self):
        for record in self:
            record.maintenance_status = 'completed'
            if record.vehicle_id:
                record.vehicle_id.transport_status = 'assigned'
                if record.next_service_odometer:
                    record.vehicle_id.next_service_odometer = record.next_service_odometer