#!/bin/python

import sys
import queue
import os
import json
import time
import threading
import math
import random
import copy
import logging
import logging.config

from Order import Order
from Courier import Courier

TOOL_NAME = sys.argv[0]  # script name , use for usage

# configuration
DEFAULT_ORDER_PER_SEC = 2  # default value for order deliver number per second
order_per_sec = DEFAULT_ORDER_PER_SEC

COURIER_QUEUE_NUMBER = 10  # total courier number

buffer_shelf_name = 'any'
shelf_config = {'hot': 10, 'cold': 10,
                'frozen': 10, buffer_shelf_name: 15}

# configuration done

# init
order_q = queue.Queue()  # queue for order

shelf_container = {}

delivered_order_list = []
wasted_order_list = []

courier_ready_queue = []

# init shelf
for temp in shelf_config:
    shelf_container[temp] = []

# init couriers
for i in range(COURIER_QUEUE_NUMBER):
    courier_ready_queue.append(Courier(i, str(i)))

logging.config.fileConfig('logging.conf')
root_logger = logging.getLogger('root')


class Order_deal_thread (threading.Thread):
    def __init__(self, thread_id, name):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.name = name

    def run(self):
        print("Start")
        while deliver_order_on_shelf():

            while not order_q.empty():
                order = order_q.get()

                put_on_shelf(order)

            time.sleep(1)

        print("End")


def usage():
    print("Usage: python %s ORDER_JSON_FILE [ORDER_NUM_PER_SEC]" % TOOL_NAME)
    exit(1)


def put_on_shelf(order):
    global shelf_container
    if len(shelf_container[order.temp]) < shelf_config[order.temp]:
        order.put_on(order.temp)
        shelf_container[order.temp].append(order)
    elif len(shelf_container[buffer_shelf_name]) < shelf_config[buffer_shelf_name]:
        order.put_on(buffer_shelf_name)
        shelf_container[buffer_shelf_name].append(order)

    else:
        clean_buffer_shelf(order.temp)
        put_on_shelf(order)


# clean up one place for order in temp-put-in at least
def clean_buffer_shelf(temp):
    global shelf_container
    if len(shelf_container[buffer_shelf_name]) < shelf_config[buffer_shelf_name]:
        return
    for order in shelf_container[buffer_shelf_name]:
        if order.temp == temp:
            continue

        if len(shelf_container[order.temp]) < shelf_config[order.temp]:
            shelf_container[buffer_shelf_name].remove(order)
            shelf_container[order.temp].append(order)
            return
        pass
    pass
    order_to_waste = shelf_container[buffer_shelf_name].pop(
        random.randint(0, shelf_config[buffer_shelf_name] - 1))
    order_to_waste.waste()
    wasted_order_list.append(order_to_waste)


def deliver_order_on_shelf():
    global all_to_deliver
    global shelf_container

    new_trans_shelf_container = {}
    for temp in shelf_config:
        new_trans_shelf_container[temp] = []

    order_list_for_sort = []

    for temp in shelf_container:
        trans_list = []
        for order in shelf_container[temp]:
            if order.is_deliverable():
                order.courier.pickup_order()
                order.courier.deliver_order()
                order.deliver()
                courier_ready_queue.append(order.courier)
                delivered_order_list.append(order)
            else:
                if order.value() <= 0:
                    order.waste()
                    wasted_order_list.append(order)
                else:
                    order_list_for_sort.append(order)

    sorted_list = sorted(order_list_for_sort)

    for sorted_order in sorted_list:
        if sorted_order.is_waiting():
            if len(courier_ready_queue) > 0:
                courier = courier_ready_queue.pop(0)
                courier.assign_order(sorted_order)
                sorted_order.assign_courier(courier)

        new_trans_shelf_container[sorted_order.shelf].append(sorted_order)

    shelf_container = new_trans_shelf_container

    print("delivered count %s" % len(delivered_order_list))
    print("courier ready count %s" % len(courier_ready_queue))
    for one in shelf_container:
        print("left %s %s" % (one, len(shelf_container[one])))
    print("waste %s" % len(wasted_order_list))
    print("============")
    if len(delivered_order_list) + len(wasted_order_list) == all_to_deliver:
        return False

    return True

# start process


if len(sys.argv) <= 1:
    usage()

if len(sys.argv) >= 3:
    tmp = int(sys.argv[2])
    if tmp <= 0 or tmp > 50:
        print("Error: input number should between [1-50]")
        usage()
    order_per_sec = tmp

# read data from file
FILE_NAME = sys.argv[1]
if not os.path.isfile(FILE_NAME):
    print("ERROR: %s is not file" % FILE_NAME)
    usage()

fo = open(FILE_NAME, "r")
lines = fo.read()
fo.close()

try:
    order_list = json.loads(lines)
except Exception as e:
    print("ERROR: format in %s is not in json list" % FILE_NAME)
    exit(2)

all_to_deliver = len(order_list)
counted_in_queue = 0

root_logger.info("total %s" % all_to_deliver)

thread = Order_deal_thread(1, "Order_deal_thread")
thread.start()

for one in order_list:
    order = Order(one)
    order_q.put(order)
    counted_in_queue += 1
    if counted_in_queue >= order_per_sec:
        counted_in_queue = 0
        time.sleep(1)
