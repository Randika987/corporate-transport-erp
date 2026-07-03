from odoo import models, fields, api


class TransportDashboard(models.Model):
    _name = 'transport.dashboard'
    _description = 'Transport Dashboard'

    name = fields.Char(default="Corporate Transport Dashboard")

    total_vehicles = fields.Integer(compute='_compute_dashboard_data')
    available_vehicles = fields.Integer(compute='_compute_dashboard_data')
    vehicles_on_trip = fields.Integer(compute='_compute_dashboard_data')
    vehicles_maintenance = fields.Integer(compute='_compute_dashboard_data')

    total_drivers = fields.Integer(compute='_compute_dashboard_data')
    total_trips = fields.Integer(compute='_compute_dashboard_data')

    total_fuel_cost = fields.Float(compute='_compute_dashboard_data')
    total_maintenance_cost = fields.Float(compute='_compute_dashboard_data')

    @api.depends()
    def _compute_dashboard_data(self):
        Vehicle = self.env['fleet.vehicle']
        Driver = self.env['transport.driver']
        Trip = self.env['transport.trip']
        Operation = self.env['transport.fleet.operation']

        for record in self:
            record.total_vehicles = Vehicle.search_count([])
            record.available_vehicles = Vehicle.search_count([
                ('transport_status', '=', 'available')
            ])
            record.vehicles_on_trip = Vehicle.search_count([
                ('transport_status', '=', 'on_trip')
            ])
            record.vehicles_maintenance = Vehicle.search_count([
                ('transport_status', '=', 'maintenance')
            ])

            record.total_drivers = Driver.search_count([])
            record.total_trips = Trip.search_count([])

            fuel_records = Operation.search([
                ('operation_type', '=', 'fuel')
            ])
            maintenance_records = Operation.search([
                ('operation_type', '=', 'maintenance')
            ])

            record.total_fuel_cost = sum(fuel_records.mapped('fuel_amount'))
            record.total_maintenance_cost = sum(
                maintenance_records.mapped('maintenance_cost')
            )

    @api.model
    def open_dashboard(self):
        dashboard = self.search([], limit=1)
        if not dashboard:
            dashboard = self.create({
                'name': 'Corporate Transport Dashboard'
            })

        return {
            'type': 'ir.actions.act_window',
            'name': 'Dashboard',
            'res_model': 'transport.dashboard',
            'view_mode': 'form',
            'res_id': dashboard.id,
            'target': 'current',
        }