# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    # Custom fields for metre reading functionality
    x_previous_reading = fields.Float(
        string="Previous Reading",
        compute='_compute_previous_reading',
        store=True,
        readonly=False,  # Allow manual override if needed
        help="Metre reading from the client's previous invoice for this product."
    )

    x_new_reading = fields.Float(
        string="New Reading",
        help="Enter the new metre reading for this billing period."
    )

    x_actual_consumption = fields.Float(
        string="Actual Consumption",
        compute='_compute_actual_consumption',
        store=True,
        help="Calculated difference between the new and previous metre readings."
    )

    @api.depends('move_id.partner_id', 'product_id', 'move_id.invoice_date', 'move_id.state')
    def _compute_previous_reading(self):
        """
        Compute the 'Previous Reading' by searching for the most recent posted invoice
        for the same partner and product, ordered by invoice date descending.
        
        Odoo 17 Note: Removed order parameter from search to avoid the property field error.
        """
        for line in self:
            previous_reading = 0.0
            
            # Only search if we have both partner and product
            if line.move_id.partner_id and line.product_id:
                # Get the current invoice date or use today's date as fallback
                current_invoice_date = line.move_id.invoice_date or fields.Date.today()
                
                # Search for previous invoice line with metre reading
                # Domain explanation:
                # - Same partner
                # - Same product  
                # - Invoice is posted (validated)
                # - Invoice date is before current invoice
                # - Has a valid new reading (> 0)
                previous_lines = self.env['account.move.line'].search([
                    ('move_id.partner_id', '=', line.move_id.partner_id.id),
                    ('product_id', '=', line.product_id.id),
                    ('move_id.state', '=', 'posted'),
                    ('move_id.invoice_date', '<', current_invoice_date),
                    ('x_new_reading', '>', 0),
                ])  # REMOVED: order='move_id.invoice_date DESC, id DESC', limit=1
                
                if previous_lines:
                    # Sort manually in Python to get the most recent
                    sorted_lines = sorted(
                        previous_lines,
                        key=lambda l: (l.move_id.invoice_date, l.id),
                        reverse=True
                    )
                    previous_reading = sorted_lines[0].x_new_reading

            line.x_previous_reading = previous_reading

    @api.depends('x_new_reading', 'x_previous_reading')
    def _compute_actual_consumption(self):
        """
        Compute the actual consumption by subtracting previous reading from new reading.
        Also automatically updates the invoice line quantity with this value.
        
        Odoo 17 Note: The compute method works identically to version 16.
        """
        for line in self:
            actual = line.x_new_reading - line.x_previous_reading
            # Prevent negative consumption values
            line.x_actual_consumption = actual if actual > 0 else 0.0
            # Automatically sync quantity with actual consumption
            if line.x_actual_consumption != line.quantity:
                line.quantity = line.x_actual_consumption

    @api.onchange('x_new_reading')
    def _onchange_x_new_reading(self):
        """
        Real-time UI update when user changes the new reading value.
        Triggers the actual consumption computation immediately.
        
        Odoo 17 Note: @api.onchange still works the same way in version 17.
        """
        if self.x_new_reading:
            self._compute_actual_consumption()