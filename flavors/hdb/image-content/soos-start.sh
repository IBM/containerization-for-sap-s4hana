#!/bin/sh

# ------------------------------------------------------------------------
# Copyright 2020 IBM Corp. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------

# Add fully qualified domain name of original server to /etc/hosts.
# (If not added the dw-processes will not start)
#
# Hostname without domain is added by Openshift from the "hostname"
# tag in the deployment yaml file.
#
# Since /etc/hosts is managed by Openshift sed inline editing does
# not work for some strange reason -> do "two stage approach"
#
# SOOS_HDB_HOST and SOOS_HDB_DOMAIN must be set as environment variables in
# the deployment yaml file.
#
# XXX THIS NEEDS TO BE DONE ONLY ONCE IF THE APPSERVER AND THE HDB
#     CONTAINER RUN IN THE SAME POD SINCE /etc/hosts IS SHARED
#     AMONG THE CONTAINERS OF A POD (PROBABLY BY THE HDB STARTUP
#     SINCE THIS HAPPENS BEFORE THE APPSERVER STARTUP).

#SOOS_HDB_HOST_FQDN="${SOOS_HDB_HOST}.${SOOS_HDB_DOMAIN}"
#if ! grep ${SOOS_HDB_HOST_FQDN} /etc/hosts; then
#    echo "Adding '${SOOS_HDB_HOST_FQDN}' to /etc/hosts"
#    sed -e "s/\(.*${SOOS_HDB_HOST}.*\)/\1 ${SOOS_HDB_HOST_FQDN}/g" /etc/hosts > /etc/hosts.new
#    cat /etc/hosts.new > /etc/hosts
#fi

# Set Timezone
#
# Must be the same for all containers to avoid time sync errors
# in SAP work processes.
#
# SOOS_GLOBAL_TIMZONE must be set as environment variable in the deployment
# yaml file.

echo "Setting Timezone to '${SOOS_GLOBAL_TIMEZONE}'"
#rm /etc/localtime
#ln -s /usr/share/zoneinfo/${SOOS_GLOBAL_TIMEZONE} /etc/localtime
timedatectl set-timezone ${SOOS_GLOBAL_TIMEZONE} # requires running systemd

# Start uuidd - leads to errors in SAP system if not started

# uuidd # Started by systemd in ubi8-init image

# Extract "shared" directory 
#
# SOOS_HDB_BASE_DIR and SOOS_HDB_SID must be set as environment variables
# in the deployment yaml file.

#if [ ! -e ${SOOS_HDB_BASE_DIR}/shared/${SOOS_HDB_SID}/profile ]; then
#    tar -xf /root/shared.tar -C ${SOOS_HDB_BASE_DIR}/shared/${SOOS_HDB_SID}
#fi

# Replacing patterns in hdblcm configfile

if [ ! -e /root/soos-hdblcm.cfg ]; then
    sed \
        -e "s|{{SOOS_HDB_BASE_DIR}}|${SOOS_HDB_BASE_DIR}|g" \
        -e "s|{{SOOS_HDB_HOST}}|${SOOS_HDB_HOST}|g" \
        /root/soos-hdblcm.tmp > /root/soos-hdblcm.cfg

    /hana/shared/${SOOS_HDB_SID}/hdblcm/hdblcm --configfile=/root/soos-hdblcm.cfg --batch
fi

# Starting HDB
#su - ${SOOS_HDB_SID,,}adm -c "HDB start"
#/hana/shared/${SOOS_HDB_SID}/hdblcm/hdblcm --configfile=/root/soos-hdblcm.cfg --batch
