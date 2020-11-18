# Order Delivering System

This is a simple model for delivering order
Cloud Kitchen面试题

## Install

requirements: python3 enviroment

    pip3 install -r requirements.txt

## Usage

python order_sys.py $file $order_num $courier_num

-   file: order data file, must be in json list format, required \*
-   order_num: order number processing number, must in int number , not required , default as 2
-   courier_num: total courier number for delivering order , not required , default as 10

for example:

    python order_sys.py orders.json
    python order_sys.py orders.json 5
    python order_sys.py orders.json 5 10

Warning: courier_num should not small than order_num, because it will waste too much

## Run Tests

    coverage run ut.py

## Coverage Report

generate simple report

    coverage report

generate html report, then find detail reports on htmlcov/index.html, there are links to detail page like htmlcov/Order_py.html

    coverage html
