#!/bin/bash

mkdir -p /usr/local/lib/heat/solo/

cp resources/__init__.py /usr/local/lib/heat/solo/
cp resources/sdn_overlay.py /usr/local/lib/heat/solo/
cp resources/solo_client.py /usr/local/lib/heat/solo/
