#!/bin/python
# By Kevin Li
# At 2020/5/9
# v 0.1

import time
import math
import logging


# class for order

STATUS_WAITING = 1
STATUS_ASSIGNED = 2
STATUS_DELIVERED = 3
STATUS_WASTE = -1

logger = logging.getLogger('main.order')


class Order(object):
    def __init__(self, order_obj):
        self.id = order_obj['id']
        self.name = order_obj['name']
        self.temp = order_obj['temp']
        self.shelf_life = order_obj['shelfLife']
        self.decay_rate = order_obj['decayRate']
        # the timestamp that the order made
        self.timestamp = math.floor(time.time())
        self.status = STATUS_WAITING
        # this is not beautiful design, but work for now
        self.delivered_timestamp = 0
        self.shelf = None
        self.courier = None
        self.comment = None
        self.shelf_decay_modifier = 0
        return

    def put_on(self, shelf):
        self.shelf = shelf
        self.shelf_decay_modifier = 1 if self.temp == self.shelf else 2

    # value left
    def value(self):
        if not self.shelf:
            return 1  # not put on shelf yet
        current = math.floor(time.time())
        return (self.shelf_life - self.decay_rate * (current - self.timestamp) * self.shelf_decay_modifier) / self.shelf_life

    def is_waiting(self):
        return self.status == STATUS_WAITING

    def assign_courier(self, courier):
        if self.status == STATUS_WAITING and courier != None:
            logger.info("assign_courier %s courier %s" % (self.id, courier.id))
            self.status = STATUS_ASSIGNED
            self.courier = courier
            return True
        return False

    def is_deliverable(self):

        if self.status == STATUS_ASSIGNED and self.courier != None:
            current = math.floor(time.time())
            is_deliverable = True if (
                current - self.timestamp) >= self.courier.deliver_in else False
            return is_deliverable

        return False

    def deliver(self):
        if self.is_deliverable():
            logger.info("order delivered %s value:%f courier %s is free" %
                        (self.id, self.value(), self.courier.id))
            self.delivered_timestamp = math.floor(
                time.time())  # mark the deliver time
            self.status = STATUS_DELIVERED
            return True
        return False

    # mark order as waste
    def waste(self, reason):
        self.status = STATUS_WASTE
        self.comment = reason
        logger.warning("order %s wasted for reason %s" %
                       (self.id, reason))

    # for sort
    def __lt__(self, other):
        if other != None:
            return self.value() < other.value()
        return False

    def __eq__(self, other):
        if other != None:
            return self.value() == other.value()
        return False

    # for debug
    def __str__(self):
        return "id:%s name:%s shelf_decay_modifier:%s temp:%s %s" % (self.id, self.name, self.shelf_decay_modifier, self.temp, self.is_deliverable())
