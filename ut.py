import unittest
from Order import Order
from Courier import Courier
import time


class MyTest(unittest.TestCase):
    def test_order(self):
        print("test_order start")
        # mockup an order
        order_obj = {
            "id": "a8cfcb76-7f24-4420-a5ba-d46dd77bdffd",
            "name": "Banana Split",
            "temp": "frozen",
            "shelfLife": 20,
            "decayRate": 0.63
        }
        order = Order(order_obj)
        # for init shelf_decay_modifier not set yet, default 0
        self.assertEqual(0, order.shelf_decay_modifier)
        # for init, not put on shelf yet, so no decay
        self.assertEqual(1, order.value())

        order.put_on('frozen')
        # put order on the shelf with same temp, shelf_decay_modifier is 1
        self.assertEqual(1, order.shelf_decay_modifier)

        order.put_on('any')
        # put order on the any shelf , shelf_decay_modifier is 2
        self.assertEqual(2, order.shelf_decay_modifier)

        # no assigned courier, in waiting status
        self.assertTrue(order.is_waiting())

        # no assigned courier, so not deliverable
        self.assertFalse(order.is_deliverable())

        # __eq__ overwrite test
        self.assertTrue(order == order)

        # __lt__ overwrite test
        self.assertFalse(order < order)

        # __str__ overwrite test
        self.assertIsNotNone(str(order))

        self.assertIsNone(order.comment)  # no reason setup yet
        order.waste("test reason")
        self.assertEqual(-1, order.status)  # waste status setup ok
        self.assertEqual("test reason", order.comment)  # reason setup ok

        print("test_order end")

    def test_courier(self):
        print("test_courier start")
        courier = Courier(1, "runner")

        self.assertTrue(courier.is_ready_for_assign())
        self.assertFalse(courier.assign_order(None))

        self.assertFalse(courier.pickup_order())
        self.assertFalse(courier.deliver_order())

        self.assertIsNotNone(str(courier))
        print("test_courier end")

    def test_deliver(self):
        print("test_deliver start")
        order_obj = {
            "id": "66a2611c-9a93-4ccd-bb85-98f423247bf9",
            "name": "Cottage Cheese",
            "temp": "cold",
            "shelfLife": 251,
            "decayRate": 0.22
        }

        order = Order(order_obj)
        order.put_on('cold')

        courier = Courier(2, "fast runner")
        self.assertEqual(1, courier.status)  # status ready

        self.assertTrue(courier.assign_order(order))
        self.assertFalse(order.assign_courier(None))
        self.assertTrue(order.assign_courier(courier))

        self.assertFalse(order.is_deliverable())
        print("sleep for 6s to wait order ready to deliver")
        time.sleep(6)
        self.assertTrue(order.is_deliverable())

        self.assertEqual(2, courier.status)  # status assigned
        self.assertTrue(courier.pickup_order())
        self.assertEqual(3, courier.status)  # status delivering
        self.assertTrue(courier.deliver_order())

        self.assertTrue(order.deliver())

        courier.reset_to_ready()
        self.assertEqual(1, courier.status)  # status back to ready
        print("test_deliver end")


if __name__ == '__main__':
    unittest.main()  # 运行所有的测试用例
