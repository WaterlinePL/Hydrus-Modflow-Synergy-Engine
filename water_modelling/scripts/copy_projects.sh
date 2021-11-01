#!/bin/bash
# Scripts is meant to be used inside water_modeling_agh or water_modeling_agh/scripts 

if [ ! -e scripts/ ]
then
    cd ..
fi

mkdir tests -p && cp -r sample/* tests/