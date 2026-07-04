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

    service_due_count = fields.Integer(
        string="Service Due Vehicles",
        compute="_compute_dashboard_data"
    )

    license_due_count = fields.Integer(
        string="License Due Drivers",
        compute="_compute_dashboard_data"
    )

    @api.depends()
    def _compute_dashboard_data(self):
        Vehicle = self.env['fleet.vehicle']
        Driver = self.env['transport.driver']
        Trip = self.env['transport.trip']
        Operation = self.env['transport.fleet.operation']

        today = fields.Date.today()

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

            service_count = 0
            vehicles = Vehicle.search([])

            for vehicle in vehicles:
                if (
                    vehicle.next_service_odometer > 0 and
                    vehicle.current_odometer >= vehicle.next_service_odometer
                ):
                    service_count += 1

            record.service_due_count = service_count

            license_count = 0
            drivers = Driver.search([])

            for driver in drivers:
                if driver.license_expiry:
                    days_left = (driver.license_expiry - today).days
                    if days_left <= 30:
                        license_count += 1

            record.license_due_count = license_count

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
    
    def action_open_service_due_vehicles(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Service Due Vehicles',
            'res_model': 'fleet.vehicle',
            'view_mode': 'kanban,tree,form',
            'domain': [('service_due_warning', '=', True)],
            'target': 'current',
        }

    def action_open_license_due_drivers(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'License Due Drivers',
            'res_model': 'transport.driver',
            'view_mode': 'tree,form',
            'domain': [('license_expiry_warning', '=', True)],
            'target': 'current',
        }

    def action_open_trips(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Trips',
            'res_model': 'transport.trip',
            'view_mode': 'tree,form',
            'target': 'current',
        }

    def action_open_fleet_operations(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Fleet Operations',
            'res_model': 'transport.fleet.operation',
            'view_mode': 'tree,form',
            'target': 'current',
        }

    def action_open_available_vehicles(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Available Vehicles',
            'res_model': 'fleet.vehicle',
            'view_mode': 'kanban,tree,form',
            'domain': [('transport_status', '=', 'available')],
            'target': 'current',
        }

    def action_open_maintenance(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Vehicles In Maintenance',
            'res_model': 'fleet.vehicle',
            'view_mode': 'kanban,tree,form',
            'domain': [('transport_status', '=', 'maintenance')],
            'target': 'current',
        }