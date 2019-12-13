# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import pytest
from odoo.tests import common
from odoo.exceptions import ValidationError


class TestDistances(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.warehouse_a = cls.env['stock.warehouse'].create({
            'name': 'Warehouse A',
            'code': 'WHA',
        })

        cls.warehouse_b = cls.env['stock.warehouse'].create({
            'name': 'Warehouse B',
            'code': 'WHB',
        })

        cls.warehouse_c = cls.env['stock.warehouse'].create({
            'name': 'Warehouse C',
            'code': 'WHC',
        })

    def make_distance(self, warehouse_1, warehouse_2, distance):
        return self.env['stock.warehouse.distance'].create({
            'warehouse_1_id': warehouse_1.id,
            'warehouse_2_id': warehouse_2.id,
            'distance': distance,
        })

    def test_no_duplicate_distances(self):
        self.make_distance(self.warehouse_a, self.warehouse_b, 1)

        with pytest.raises(ValidationError):
            self.make_distance(self.warehouse_a, self.warehouse_b, 1)

    def test_no_duplicate_distances__reverse_order(self):
        self.make_distance(self.warehouse_a, self.warehouse_b, 1)

        with pytest.raises(ValidationError):
            self.make_distance(self.warehouse_b, self.warehouse_a, 1)

    def test_warehouse_1_and_warehouse_2_must_be_different(self):
        with pytest.raises(ValidationError):
            self.make_distance(self.warehouse_a, self.warehouse_a, 1)

    def test_compute_distance_between_warehouses(self):
        distance = 100
        self.make_distance(self.warehouse_a, self.warehouse_b, distance)
        assert self.warehouse_a.distance_from(self.warehouse_b) == distance
        assert self.warehouse_b.distance_from(self.warehouse_a) == distance

    def test_if_no_distance_between_warehouses__error_raised(self):
        with pytest.raises(ValidationError):
            self.warehouse_a.distance_from(self.warehouse_b)

    def test_if_no_distance_between_warehouses__and_not_raise__result_is_none(self):
        assert self.warehouse_a.distance_from(self.warehouse_b, raise_=False) is None
