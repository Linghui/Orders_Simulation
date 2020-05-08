#!/bin/python

# class for courier

import random

STATUS_READY = 1  # ready for assign
STATUS_ASSIGNED = 2  # assigned order
STATUS_DELIVERING = 3  # delivering


class Courier(object):
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.status = STATUS_READY
        self.deliver_in = 0
        self.order = None

    # once courier assign on order , random 2-6s to pick it up
    def assign_order(self, order):
        if self.status == STATUS_READY:
            self.order = order
            self.status = STATUS_ASSIGNED
            self.deliver_in = random.randint(2, 6)
            return True
        return False

    def pickup_order(self):
        if self.status == STATUS_ASSIGNED:
            self.status = STATUS_DELIVERING
            return True
        return False

    def deliver_order(self):
        if self.status == STATUS_DELIVERING:
            self.status = STATUS_READY
            self.order = None  # release order
            return True
        return False

    def ready_for_assign(self):
        return self.status == STATUS_READY
