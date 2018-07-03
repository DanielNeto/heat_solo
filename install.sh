#!/bin/bash

mkdir -p /usr/local/lib/heat/solo/

cp resources/__init__.py /usr/local/lib/heat/solo/
cp resources/sdn_overlay.py /usr/local/lib/heat/solo/
cp resources/solo_clientv2.py /usr/local/lib/heat/solo/
