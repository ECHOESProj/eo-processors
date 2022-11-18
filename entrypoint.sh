#!/bin/sh
# Used in Docker file for ENTRYPOINT

echo "$@"
envsubst < /root/config_eo_service.yml | tee /root/config_eo_service.yml
python3 -W ignore -m eo_custom_scripts "$@"
