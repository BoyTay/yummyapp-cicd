import unittest
from unittest.mock import patch

from yummy_app import YummyApp
import gps_service


# ================================================================
# CAP DO 1: Bo test co ban cho san (Moi chi dat ~35% Coverage)
# ================================================================
class TestEasyLevel(unittest.TestCase):
    """Kiem thu chuc nang co ban tinh tien don hang"""

    def setUp(self):
        self.app = YummyApp()

    def test_calculate_total_for_single_item(self):
        cart = {"pho": 2}
        self.assertEqual(self.app.calculate_order_total(cart), 100000)

    def test_calculate_total_for_multiple_items(self):
        cart = {"pho": 1, "bun": 1}
        self.assertEqual(self.app.calculate_order_total(cart), 95000)

    def test_calculate_total_for_empty_cart(self):
        self.assertEqual(self.app.calculate_order_total({}), 0.0)

    def test_calculate_total_with_zero_quantity(self):
        cart = {"pho": 0}
        self.assertEqual(self.app.calculate_order_total(cart), 0.0)


# ================================================================
# CAP DO 2 (TIET 3): 4 test case cho apply_promo_code
# ================================================================
class TestMediumLevel(unittest.TestCase):
    """Kiem thu apply_promo_code theo trang thai mang va phien ban HDH"""

    def test_promo_online_valid(self):
        # App online, OS 15, ma GIAM10 giam 10% -> 100000 con 90000
        app = YummyApp(network_status="online", os_version=15)
        self.assertAlmostEqual(app.apply_promo_code(100000, "GIAM10"), 90000)

    def test_promo_offline(self):
        # Mat mang -> ham phai nem ConnectionError
        app = YummyApp(network_status="offline", os_version=15)
        with self.assertRaises(ConnectionError):
            app.apply_promo_code(100000, "GIAM10")

    def test_special_code_os_15(self):
        # Ma NEW_OS_ONLY can OS >= 15, giam 20% -> 100000 con 80000
        app = YummyApp(network_status="online", os_version=15)
        self.assertAlmostEqual(app.apply_promo_code(100000, "NEW_OS_ONLY"), 80000)

    def test_special_code_os_14(self):
        # OS 14 < 15 -> ham phai nem ValueError
        app = YummyApp(network_status="online", os_version=14)
        with self.assertRaises(ValueError):
            app.apply_promo_code(100000, "NEW_OS_ONLY")


# ================================================================
# CAP DO 2 (TIET 3): 3 test case Mocking GPS cho get_nearby_restaurants
# ================================================================
class TestHardLevel(unittest.TestCase):
    """Kiem thu get_nearby_restaurants voi phan cung GPS bi dong the (mock)"""

    def setUp(self):
        self.app = YummyApp()

    @patch('yummy_app.gps_service.get_current_location')
    def test_gps_in_zone(self, mock_gps):
        # GPS tra ve toa do trong vung -> co 2 nha hang
        mock_gps.return_value = (10.0, 105.0)
        result = self.app.get_nearby_restaurants()
        self.assertEqual(
            result, ["Nha hang Pho Ly Quoc Su", "Bun cha Huong Lien"]
        )
        mock_gps.assert_called_once()

    @patch('yummy_app.gps_service.get_current_location')
    def test_gps_out_of_zone(self, mock_gps):
        # GPS tra ve toa do ngoai vung -> danh sach rong
        mock_gps.return_value = (20.0, 110.0)
        self.assertEqual(self.app.get_nearby_restaurants(), [])

    @patch('yummy_app.gps_service.get_current_location')
    def test_gps_signal_lost(self, mock_gps):
        # GPS mat tin hieu -> ham bat loi va tra ve chuoi bao loi
        mock_gps.side_effect = gps_service.GPSSignalLostError()
        self.assertEqual(
            self.app.get_nearby_restaurants(), "Khong the xac dinh vi tri."
        )


if __name__ == '__main__':
    unittest.main()
