#!/bin/bash

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
# SOOS_NWS4_HOST and SOOS_NWS4_DOMAIN must be set as environment variables in
# the deployment yaml file.
#
# XXX THIS NEEDS TO BE DONE ONLY ONCE IF THE APPSERVER AND THE HDB
#     CONTAINER RUN IN THE SAME POD SINCE /etc/hosts IS SHARED
#     AMONG THE CONTAINERS OF A POD (PROBABLY BY THE HDB STARTUP
#     SINCE THIS HAPPENS BEFORE THE APPSERVER STARTUP).

SOOS_NWS4_HOST_FQDN="${SOOS_NWS4_HOST}.${SOOS_NWS4_DOMAIN}"
if ! grep ${SOOS_NWS4_HOST_FQDN} /etc/hosts; then
    echo "Adding '${SOOS_NWS4_HOST_FQDN}' to /etc/hosts"
    sed -e "s/\(.*${SOOS_NWS4_HOST}.*\)/\1 ${SOOS_NWS4_HOST_FQDN}/g" /etc/hosts > /etc/hosts.new
    cat /etc/hosts.new > /etc/hosts
fi

# Set Timezone
#
# Must be the same for all containers to avoid time sync errors
# in SAP work processes.
#
# SOOS_GLOBAL_TIMEZONE must be set as environment variable in the deployment
# yaml file.

echo "Setting Timezone to '${SOOS_GLOBAL_TIMEZONE}'"
#rm /etc/localtime
#ln -s /usr/share/zoneinfo/${SOOS_GLOBAL_TIMEZONE} /etc/localtime
timedatectl set-timezone ${SOOS_GLOBAL_TIMEZONE} # requires running systemd

# Start uuidd - leads to errors in SAP system if not started

# uuidd # Started by systemd in ubi8-init image

# Setting command line arguments 

#SAPDBHOST=
#DBUSER_PWD=
#CHANGE_HANA_CONNECT=false

# Copy Services depending on profile

echo "Copying services"

grep $SOOS_NWS4_PROFILE /usr/sap/sapservices.orig > /usr/sap/sapservices

# Copy executables to instance directories

echo "Copying executables to instance directories"

while read line; do
  array=($line)
  profile=${array[4]}
  SYS_EXE_PATH=/usr/sap/$SOOS_NWS4_SID/SYS/exe/run
  LD_LIBRARY_PATH=$SYS_EXE_PATH:$LD_LIBRARY_PATH; export LD_LIBRARY_PATH; $SYS_EXE_PATH/sapcpe $profile
done </usr/sap/sapservices

# adapt hdbuserstore and DEFAULT.PFL for HANADB connect
# CHANGE_HANA_CONNECT is set during image build!
#if [ $CHANGE_HANA_CONNECT = true ]; then
#	echo "Adapting hdbuserstore and DEFAULT.PFL for HANADB running on " $SAPDBHOST
#        /root/soos-hana-connect.sh $CHANGE_HANA_CONNECT $SAPDBHOST $DBUSER_PWD
#fi

# Start Instance Services

echo "Starting SAP Instance Services"
sh /usr/sap/sapservices
sleep 2 # Wait for SAP Instance Services finished starting

# Wait for HDB start
#
# SOOS_NWS4_SID must be set as environment variable in the deployment yaml file.
# 
# Only in case of DI!

if [ $SOOS_NWS4_INSTTYPE = "DI" ]; then
  echo "Waiting for DB"
  while ! su - ${SOOS_NWS4_SID,,}adm -c "R3trans -d"; do
     sleep 2
  done
fi

# Start Instance

# INSTNO=$(su - ${SOOS_NWS4_SID,,}adm -c "/usr/sap/$SOOS_NWS4_SID/SYS/exe/run/sapcontrol -function ListInstances" | cut -d- -f2 | head -1)
# SAPSYSTEM=$(grep -w SAPSYSTEM $profile)
# array=($SAPSYSTEM)
# INSTNO=${array[2]}
su - ${SOOS_NWS4_SID,,}adm -c "/usr/sap/$SOOS_NWS4_SID/SYS/exe/run/sapcontrol -nr "${SOOS_NWS4_INSTNO}" -function Start"
