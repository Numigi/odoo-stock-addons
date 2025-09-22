# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.tools import float_compare, float_is_zero
from datetime import datetime, time
from dateutil.relativedelta import relativedelta
from odoo.addons.stock.models.stock_rule import ProcurementException
from odoo.tools import split_every
from odoo.exceptions import UserError
from psycopg2 import OperationalError
from odoo import registry

import logging

_logger = logging.getLogger(__name__)


class StockWarehouseOrderpoint(models.Model):
    _inherit = 'stock.warehouse.orderpoint'

     ## Core fields from 'stock' module ##
    visibility_days = fields.Float(compute='_compute_visibility_days',
        inverse='_set_visibility_days', string="Visibility Days", readonly=False,
        store=True,
        help="Consider the forecasted stock for this many days in the future when replenishing. Set to 0 for just-in-time.")
    lead_days_date = fields.Date(compute='_compute_lead_days')
    days_to_order = fields.Float(compute='_compute_days_to_order',
        help="Safety days to create replenishment demands in advance.")
    

     ## Fields added by 'purchase_stock' ##
    purchase_visibility_days = fields.Float(default=0.0,
        help="Visibility Days applied on the purchase routes.")
    

     ## Fields added by 'mrp' ##
    manufacturing_visibility_days = fields.Float(default=0.0,
        help="Visibility Days applied on the manufacturing routes.")

    

     ## Compute and Inverse Methods ##
    @api.depends('route_id', 'purchase_visibility_days',
        'manufacturing_visibility_days')
    def _compute_visibility_days(self):
        for orderpoint in self:
            if 'buy' in orderpoint.rule_ids.mapped('action'):
                orderpoint.visibility_days = orderpoint.purchase_visibility_days
            elif 'manufacture' in orderpoint.rule_ids.mapped('action'):
                orderpoint.visibility_days = orderpoint.manufacturing_visibility_days
            else:
                orderpoint.visibility_days = 0.0

    def _set_visibility_days(self):
        for orderpoint in self:
            if 'buy' in orderpoint.rule_ids.mapped('action'):
                orderpoint.purchase_visibility_days = orderpoint.visibility_days
            elif 'manufacture' in orderpoint.rule_ids.mapped('action'):
                orderpoint.manufacturing_visibility_days = orderpoint.visibility_days

    @api.depends('route_id')
    def _compute_days_to_order(self):
        for orderpoint in self:
            if 'buy' in orderpoint.rule_ids.mapped('action'):
                orderpoint.days_to_order = orderpoint.company_id.days_to_purchase
            elif 'manufacture' in orderpoint.rule_ids.mapped('action'):
                orderpoint.days_to_order = orderpoint.product_id.produce_delay
            else:
                orderpoint.days_to_order = 0.0

    # --- DEBUT DE LA FONCTION ALIGNÉE SUR LA V14 ---
    @api.depends('rule_ids', 'product_id.seller_ids', 'product_id.seller_ids.delay')
    def _compute_lead_days(self):
        """
        Computes the expected delivery date based on lead times.
        This version is aligned with Odoo V14's core structure.
        """
        for orderpoint in self.with_context(bypass_delay_description=True):
            if not orderpoint.product_id or not orderpoint.location_id:
                orderpoint.lead_days_date = False
                continue
            # Appel direct sans `_get_lead_days_values` pour la compatibilité V14
            lead_days, dummy = orderpoint.rule_ids._get_lead_days(orderpoint.product_id)
            lead_days_date = fields.Date.today() + relativedelta(days=lead_days)
            orderpoint.lead_days_date = lead_days_date

    # --- FIN DE LA FONCTION ALIGNÉE SUR LA V14 ---

    @api.depends('qty_multiple', 'product_min_qty', 'product_max_qty',
        'visibility_days', 'product_id', 'location_id', 'qty_forecast')
    def _compute_qty_to_order(self):
        for orderpoint in self:
            if not orderpoint.product_id or not orderpoint.location_id:
                orderpoint.qty_to_order = 0.0
                continue

            qty_to_order = 0.0
            rounding = orderpoint.product_uom.rounding

            if float_compare(orderpoint.qty_forecast, orderpoint.product_min_qty,
                    precision_rounding=rounding) < 0:
                product_context = orderpoint._get_product_context(
                    visibility_days=orderpoint.visibility_days)

                qty_forecast_with_visibility = orderpoint.product_id.with_context(
                    **product_context).virtual_available
                # Note: `_get_quantity_in_progress` is not a standard method on orderpoint in V14.
                # Assuming this logic is handled elsewhere or by `virtual_available` context.

                qty_to_order = max(orderpoint.product_min_qty,
                    orderpoint.product_max_qty) - qty_forecast_with_visibility

                if float_compare(qty_to_order, 0.0, precision_rounding=rounding) < 0:
                    qty_to_order = 0.0

                if orderpoint.qty_multiple > 0 and not float_is_zero(
                        orderpoint.qty_multiple, precision_rounding=rounding):
                    remainder = qty_to_order % orderpoint.qty_multiple
                    if not float_is_zero(remainder, precision_rounding=rounding):
                        qty_to_order += orderpoint.qty_multiple - remainder

            orderpoint.qty_to_order = qty_to_order

    def _get_product_context(self, visibility_days=0):
        self.ensure_one()
        if not self.lead_days_date:
            self._compute_lead_days()
        to_date = self.lead_days_date + relativedelta(days=visibility_days)
        return {'location': self.location_id.id,
            'to_date': datetime.combine(to_date, time.max)}

    

     ## Procurement Trigger Logic (Aligned with V14) ##

    def _procure_orderpoint_confirm(self, use_new_cursor=False, company_id=None,
                                    raise_user_error=True):
        self = self.with_company(company_id)
        orderpoints_noprefetch = self.read(['id'])
        orderpoints_noprefetch = [orderpoint['id'] for orderpoint in
                                  orderpoints_noprefetch]
        for orderpoints_batch in split_every(1000, orderpoints_noprefetch):
            if use_new_cursor:
                cr = registry(self._cr.dbname).cursor()
                self = self.with_env(self.env(cr=cr))
            try:
                orderpoints_batch_records = self.env[
                    'stock.warehouse.orderpoint'].browse(orderpoints_batch)
                orderpoints_exceptions = []
                while orderpoints_batch_records:
                    procurements = []
                    for orderpoint in orderpoints_batch_records:
                        origins = orderpoint.env.context.get('origins', {}).get(
                            orderpoint.id, False)
                        if origins:
                            origin = '%s - %s' % (orderpoint.display_name,
                                                  ','.join(origins))
                        else:
                            origin = orderpoint.name

                        if float_compare(orderpoint.qty_to_order, 0.0,
                                precision_rounding=orderpoint.product_uom.rounding) == 1:
                            date = datetime.combine(orderpoint.lead_days_date, time.min)

                            # --- V16 Logic Integration ---
                            global_visibility_days = self.env[
                                'ir.config_parameter'].sudo().get_param(
                                'stock.visibility_days', '0.0')
                            if float(global_visibility_days) > 0:
                                date -= relativedelta.relativedelta(
                                    days=int(global_visibility_days))
                            # --- End of V16 Logic Integration ---

                            values = orderpoint._prepare_procurement_values(date=date)
                            procurements.append(
                                self.env['procurement.group'].Procurement(
                                    orderpoint.product_id, orderpoint.qty_to_order,
                                    orderpoint.product_uom, orderpoint.location_id,
                                    orderpoint.name, origin, orderpoint.company_id,
                                    values))
                    try:
                        with self.env.cr.savepoint():
                            self.env['procurement.group'].with_context(
                                from_orderpoint=True).run(procurements,
                                raise_user_error=raise_user_error)
                    except ProcurementException as errors:
                        for procurement, error_msg in errors.procurement_exceptions:
                            orderpoints_exceptions += [
                                (procurement.values.get('orderpoint_id'), error_msg)]
                        failed_orderpoints = self.env[
                            'stock.warehouse.orderpoint'].concat(
                            *[o[0] for o in orderpoints_exceptions])
                        if not failed_orderpoints:
                            _logger.error('Unable to process orderpoints')
                            break
                        orderpoints_batch_records -= failed_orderpoints
                    except OperationalError:
                        if use_new_cursor:
                            cr.rollback()
                            continue
                        else:
                            raise
                    else:
                        if hasattr(orderpoints_batch_records,
                                '_post_process_scheduler'):
                            orderpoints_batch_records._post_process_scheduler()
                        break

                for orderpoint, error_msg in orderpoints_exceptions:
                    existing_activity = self.env['mail.activity'].search(
                        [('res_id', '=', orderpoint.product_id.product_tmpl_id.id),
                            ('res_model_id', '=',
                             self.env.ref('product.model_product_template').id),
                            ('note', '=', error_msg)])
                    if not existing_activity:
                        orderpoint.product_id.product_tmpl_id.activity_schedule(
                            'mail.mail_activity_data_warning', note=error_msg,
                            user_id=orderpoint.product_id.responsible_id.id or SUPERUSER_ID, )
            finally:
                if use_new_cursor:
                    try:
                        cr.commit()
                    finally:
                        cr.close()
        return {}  