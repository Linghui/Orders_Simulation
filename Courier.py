#!/bin/python
# By Kevin Li
# At 2020/5/9
# v 0.1

# class for courier

import random
import logging

STATUS_READY = 1  # ready for assign
STATUS_ASSIGNED = 2  # assigned order
STATUS_DELIVERING = 3  # delivering

logger = logging.getLogger('main.couri')


class Courier(object):
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.status = STATUS_READY
        self.deliver_in = 0
        self.order = None

    # once courier assign on order , random 2-6s to pick it up
    def assign_order(self, order):
        if self.status == STATUS_READY and order != None:

            self.order = order
            self.status = STATUS_ASSIGNED
            self.deliver_in = random.randint(2, 6)
            logger.info("courier %s assigned order %s, will pickup in %s s" % (
                self.id, order.id, self.deliver_in))
            return True
        return False

    def pickup_order(self):
        if self.status == STATUS_ASSIGNED:
            logger.info("courier %s pickup order %s" %
                        (self.id, self.order.id))
            self.status = STATUS_DELIVERING
            return True
        return False

    def deliver_order(self):
        if self.status == STATUS_DELIVERING:
            logger.info("courier %s deliver_order order %s" %
                        (self.id, self.order.id))
            self.status = STATUS_READY
            return True
        return False

    def is_ready_for_assign(self):
        return self.status == STATUS_READY

    def reset_to_ready(self):
        self.status = STATUS_READY

    def __str__(self):
        return str(self.id) + " " + str(self.status) + " " + str(self.order)
