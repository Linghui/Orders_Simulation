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

MAX_ORDER_PER_SEC = 20

DEFAULT_COURIER_QUEUE_NUMBER = 10  # total courier number

buffer_shelf_name = 'any'
shelf_config = {'hot': 10, 'cold': 10,
                'frozen': 10, buffer_shelf_name: 15}

temp_name_list = shelf_config.keys()

# configuration done

WASTE_REASON_NO_ROOM = "no room left on shelf"
WASTE_REASON_DECAIED = "decaied"

# init
order_q = queue.Queue()  # queue for order, thread safe

shelf_container = {}

delivered_order_list = []
wasted_order_list = []

courier_ready_queue = []
all_courier = []

# init shelf
for temp in shelf_config:
    shelf_container[temp] = []


logging.config.fileConfig('logging.conf')
root_logger = logging.getLogger('root')


class Order_deal_thread (threading.Thread):
    def __init__(self, thread_id, name):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.name = name

    def run(self):
        root_logger.info("Start")

        # a better design might be make deliver_order_on_shelf() and put_on_shelf() parallel in different thread
        # but for time limit and thread safe
        while deliver_order_on_shelf():

            while not order_q.empty():
                order = order_q.get()
                put_on_shelf(order)

            time.sleep(1)

        root_logger.info("End")


def usage():
    print("usage: python %s order_json_file [order_num_per_sec]" % TOOL_NAME)


def usage_n_e():
    usage()
    exit(1)

# put order on shelf


def put_on_shelf(order):
    global shelf_container

    # in case there is temp of order out of shelf temp range
    if not order.temp in temp_name_list:
        root_logger.error("no shelf find for temp '%s'" % order.temp)
        return False

    # there is room for temp of order, put on it
    if len(shelf_container[order.temp]) < shelf_config[order.temp]:
        order.put_on(order.temp)
        shelf_container[order.temp].append(order)
    # there is room on buffer shelf, put on it
    elif len(shelf_container[buffer_shelf_name]) < shelf_config[buffer_shelf_name]:
        order.put_on(buffer_shelf_name)
        shelf_container[buffer_shelf_name].append(order)

    else:
        # both temp shelf for order and buffer shelf are full
        # clean at least one room on any to put order on
        clean_buffer_shelf(order.temp)
        put_on_shelf(order)

    return True

# clean up one room for order in temp-put-in at least


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

    # random an order on buffer shelf to waste
    order_to_waste = shelf_container[buffer_shelf_name].pop(
        random.randint(0, shelf_config[buffer_shelf_name] - 1))

    # in case the random order is assigned courier, reset the courier
    # not best solution but workaround for now
    if order_to_waste.courier != None:
        order_to_waste.courier.reset_to_ready()
        courier_ready_queue.append(order_to_waste.courier)

    order_to_waste.waste(WASTE_REASON_NO_ROOM)

    wasted_order_list.append(order_to_waste)  # record it


def deliver_order_on_shelf():
    global all_to_deliver
    global shelf_container

    new_trans_shelf_container = {}
    for temp in shelf_config:
        new_trans_shelf_container[temp] = []

    order_list_for_sort = []

    for temp in shelf_container:
        for order in shelf_container[temp]:
            if order.is_deliverable():
                order.courier.pickup_order()
                order.courier.deliver_order()
                order.deliver()
                courier_ready_queue.append(order.courier)
                delivered_order_list.append(order)
            else:
                if order.value() <= 0:
                    order.waste(WASTE_REASON_DECAIED)
                    wasted_order_list.append(order)
                else:
                    order_list_for_sort.append(order)

    for sorted_order in sorted(order_list_for_sort):
        if sorted_order.is_waiting():
            if len(courier_ready_queue) > 0:
                courier = courier_ready_queue.pop(0)
                courier.assign_order(sorted_order)
                sorted_order.assign_courier(courier)

        new_trans_shelf_container[sorted_order.shelf].append(sorted_order)

    shelf_container = new_trans_shelf_container

    root_logger.info("delivered count %s" % len(delivered_order_list))
    root_logger.info("courier ready count %s" % len(courier_ready_queue))
    for one in shelf_container:
        root_logger.info("left %s %s" % (one, len(shelf_container[one])))
    root_logger.info("waste %s" % len(wasted_order_list))
    root_logger.info("============")
    if len(delivered_order_list) + len(wasted_order_list) == all_to_deliver:
        return False

    return True

# start process


if len(sys.argv) <= 1:
    usage_n_e()


FILE_NAME = sys.argv[1]
if not os.path.isfile(FILE_NAME):
    print("ERROR: %s is not file" % FILE_NAME, file=sys.stderr)
    usage_n_e()

# assign default value
order_per_sec = DEFAULT_ORDER_PER_SEC

if len(sys.argv) >= 3:
    tmp = int(sys.argv[2])
    if tmp < DEFAULT_ORDER_PER_SEC or tmp > MAX_ORDER_PER_SEC:
        print(
            "Error: input order_per_sec number should between [%s-%s]" % (DEFAULT_ORDER_PER_SEC, MAX_ORDER_PER_SEC), file=sys.stderr)
        usage_n_e()
    order_per_sec = tmp

# assign default value
courier_queue_number = DEFAULT_COURIER_QUEUE_NUMBER

if len(sys.argv) >= 4:
    tmp = int(sys.argv[3])
    if tmp < 2:
        print(
            "Error: input number must bigger than 2", file=sys.stderr)
        usage_n_e()
    courier_queue_number = tmp

# init couriers
for i in range(courier_queue_number):
    courier = Courier(i, str(i))
    courier_ready_queue.append(courier)
    all_courier.append(courier)

# read data from file
fo = open(FILE_NAME, "r")
lines = fo.read()
fo.close()

try:
    order_list = json.loads(lines)
except Exception as e:
    print("ERROR: data format in %s is not in json list" %
          FILE_NAME, file=sys.stderr)
    exit(2)

all_to_deliver = len(order_list)
counted_in_queue = 0

root_logger.info("total order number %s" % all_to_deliver)

thread = Order_deal_thread(1, "Order_deal_thread")
thread.start()

for one in order_list:
    order = Order(one)
    order_q.put(order)
    counted_in_queue += 1
    if counted_in_queue >= order_per_sec:
        counted_in_queue = 0
        time.sleep(1)
