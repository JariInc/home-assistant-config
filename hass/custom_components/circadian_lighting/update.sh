#!/bin/bash

declare -A files

files[__init__.py]="https://raw.githubusercontent.com/claytonjn/hass-circadian_lighting/master/custom_components/circadian_lighting/__init__.py"
files[sensor.py]="https://raw.githubusercontent.com/claytonjn/hass-circadian_lighting/master/custom_components/circadian_lighting/sensor.py"
files[switch.py]="https://raw.githubusercontent.com/claytonjn/hass-circadian_lighting/master/custom_components/circadian_lighting/switch.py"
files[manifest.json]="https://raw.githubusercontent.com/claytonjn/hass-circadian_lighting/master/custom_components/circadian_lighting/manifest.json"
files[services.yaml]="https://raw.githubusercontent.com/claytonjn/hass-circadian_lighting/master/custom_components/circadian_lighting/services.yaml"

for i in "${!files[@]}"
do
    curl -o ./$i ${files[$i]}
done
