# -*- coding: utf-8 -*-

from odoo.tests import TransactionCase
from odoo.exceptions import ValidationError


class TestCommunicationCodes(TransactionCase):
    """Communication Codes Module Tests"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee = cls.env['hr.employee'].create({
            'name': 'Test Employee',
        })
        cls.Code = cls.env['communication.codes']
        cls.test_vals = {
            'employee_id': cls.employee.id,
            'code_number': '091-123-4567',
            'code_system': 'prepaid',
            'monthly_balance': 50.0,
            'code_status': 'in_stock',
        }

    def test_create_code(self):
        """Test code creation"""
        code = self.Code.create(self.test_vals.copy())
        self.assertTrue(code.id)
        self.assertEqual(code.code_status, 'in_stock')
        self.assertEqual(code.code_system, 'prepaid')

    def test_valid_code_format(self):
        """Test valid code number format"""
        code = self.Code.new(self.test_vals.copy())
        code.code_number = '091-123-4567'
        code._validate_code_number()
        self.assertTrue(True)

    def test_invalid_code_format(self):
        """Test invalid code number format"""
        code = self.Code.new(self.test_vals.copy())
        code.code_number = 'invalid'
        with self.assertRaises(ValidationError):
            code._validate_code_number()

    def test_duplicate_code_number(self):
        """Test duplicate code number constraint"""
        vals = self.test_vals.copy()
        vals['code_number'] = '091-999-8888'
        self.Code.create(vals)
        with self.assertRaises(ValidationError):
            self.Code.create(vals.copy())

    def test_negative_balance(self):
        """Test negative monthly balance validation"""
        code = self.Code.new(self.test_vals.copy())
        code.monthly_balance = -100
        with self.assertRaises(ValidationError):
            code._validate_monthly_balance()

    def test_action_deliver(self):
        """Test deliver action"""
        code = self.Code.create(self.test_vals.copy())
        code.action_deliver()
        self.assertEqual(code.code_status, 'delivered')
        self.assertTrue(code.delivery_date)

    def test_action_suspend(self):
        """Test suspend action"""
        code = self.Code.create(self.test_vals.copy())
        code.action_suspend()
        self.assertEqual(code.code_status, 'suspended')

    def test_action_cancel(self):
        """Test cancel action"""
        code = self.Code.create(self.test_vals.copy())
        code.action_cancel()
        self.assertEqual(code.code_status, 'cancelled')

    def test_action_return_to_stock(self):
        """Test return to stock action"""
        code = self.Code.create(self.test_vals.copy())
        code.action_deliver()
        code.action_return_to_stock()
        self.assertEqual(code.code_status, 'in_stock')
        self.assertFalse(code.delivery_date)

    def test_name_search(self):
        """Test name search functionality"""
        code = self.Code.create(self.test_vals.copy())
        results = self.Code._name_search('091-123')
        self.assertTrue(len(results) > 0)

    def test_get_dashboard_stats(self):
        """Test dashboard statistics"""
        self.Code.create(self.test_vals.copy())
        stats = self.Code.get_dashboard_stats()
        self.assertIn('total_count', stats)
        self.assertIn('status_counts', stats)
        self.assertIn('system_counts', stats)
        self.assertGreaterEqual(stats['total_count'], 1)

    def test_copy_code(self):
        """Test code copy functionality"""
        code = self.Code.create(self.test_vals.copy())
        copied = code.copy()
        self.assertNotEqual(code.code_number, copied.code_number)
        self.assertEqual(copied.code_status, 'in_stock')

    def test_active_toggle(self):
        """Test active field toggle"""
        code = self.Code.create(self.test_vals.copy())
        self.assertTrue(code.active)
        code.write({'active': False})
        self.assertFalse(code.active)
