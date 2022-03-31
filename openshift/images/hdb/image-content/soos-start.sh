#!/bin/sh

# ------------------------------------------------------------------------
# Copyright 2020, 2021 IBM Corp. All Rights Reserved.
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

# Replacing patterns in hdblcm configfile

SOOS_GLOBAL_HDB_RENAME=${SOOS_GLOBAL_HDB_RENAME:0:1}

if [ ! -e /root/soos-hdblcm.cfg ]; then
    echo "Replacing patterns in hdblcm configfile"
    sed \
        -e "s|{{SOOS_HDB_BASE_DIR}}|${SOOS_HDB_BASE_DIR}|g" \
        -e "s|{{SOOS_HDB_BASE_DATA_DIR}}|${SOOS_HDB_BASE_DATA_DIR}|g" \
        -e "s|{{SOOS_HDB_BASE_LOG_DIR}}|${SOOS_HDB_BASE_LOG_DIR}|g" \
        -e "s|{{SOOS_HDB_HOST}}|${SOOS_HDB_HOST}|g" \
        -e "s|{{SOOS_HDB_RENAME}}|${SOOS_GLOBAL_HDB_RENAME}|g" \
        /root/soos-hdblcm.tmp > /root/soos-hdblcm.cfg

    PERSISTENCE=/persistence/${SOOS_HDB_SID}

    if [ ${SOOS_GLOBAL_HDB_RENAME} = "n" ]; then
        # Start up scenario for standard system as reference system
        # SOOS_GLOBAL_HDB_RENAME = y triggers hdblcm to start the HANA Database instance
        if [ ! -e $PERSISTENCE/${SOOS_HDB_HOST} ]; then
            HDB_SHARED_INSTDIR=${SOOS_HDB_BASE_DIR}/shared/${SOOS_HDB_SID}/HDB${SOOS_HDB_INSTNO}
            su - ${SOOS_HDB_SID,,}adm -c "mv $HDB_SHARED_INSTDIR/${SOOS_HDB_HOST} $PERSISTENCE/${SOOS_HDB_HOST}"
            su - ${SOOS_HDB_SID,,}adm -c "chmod -R 2775 $PERSISTENCE/${SOOS_HDB_HOST}"
            su - ${SOOS_HDB_SID,,}adm -c "ln -s $PERSISTENCE/${SOOS_HDB_HOST} $HDB_SHARED_INSTDIR/${SOOS_HDB_HOST}"
        fi

        ${SOOS_HDB_BASE_DIR}/shared/${SOOS_HDB_SID}/hdblcm/hdblcm --configfile=/root/soos-hdblcm.cfg --batch
    else
        # Start up scenario for distributed system as reference system in one pod
        echo "Renaming HDB hostname to '${SOOS_HDB_HOST}'"

        HDB_SHARED_INSTDIR=${SOOS_HDB_BASE_DIR}/shared/${SOOS_HDB_SID}/HDB${SOOS_HDB_INSTNO}

        if [ ! -e $PERSISTENCE/${SOOS_HDB_HOST} ]; then
            echo "Create '$HDB_SHARED_INSTDIR/${SOOS_HDB_HOST}' on NFS share"
            HDB_SHARED_INSTDIR=${SOOS_HDB_BASE_DIR}/shared/${SOOS_HDB_SID}/HDB${SOOS_HDB_INSTNO}
            su - ${SOOS_HDB_SID,,}adm -c "cp -r $HDB_SHARED_INSTDIR/${SOOS_HDB_SOURCE_HOST} $PERSISTENCE/${SOOS_HDB_HOST}"
            su - ${SOOS_HDB_SID,,}adm -c "chmod -R 2775 $PERSISTENCE/${SOOS_HDB_HOST}"
        fi

        echo "Use '$PERSISTENCE/${SOOS_HDB_HOST}' as '$HDB_SHARED_INSTDIR/${SOOS_HDB_HOST}'"
        su - ${SOOS_HDB_SID,,}adm -c "ln -s $PERSISTENCE/${SOOS_HDB_HOST} $HDB_SHARED_INSTDIR/${SOOS_HDB_HOST}"

        SAPSYS_GID=$(id -G ${SOOS_HDB_SID,,}adm | cut -d ' ' -f1)
        echo "Creating temporary root user hdbroot with gid '$SAPSYS_GID'"
        useradd -o -u 0 -g $SAPSYS_GID hdbroot

        # Create instance directory /usr/sap/${SOOS_HDB_SID}
        echo "Executing hdblcm tool to generate instance directory"
        su - hdbroot -c "${SOOS_HDB_BASE_DIR}/shared/${SOOS_HDB_SID}/hdblcm/hdblcm --configfile=/root/soos-hdblcm.cfg --batch"

        # Delete hdbroot
        userdel -f hdbroot

        # Caution: the ${SOOS_HDB_HOST} directory cannot be copied before running the hdblcm command as it must be executed as root
        if [ ! -e $PERSISTENCE/${SOOS_HDB_HOST} ]; then
            echo "Moving '$HDB_SHARED_INSTDIR/${SOOS_HDB_HOST}' to '$PERSISTENCE'"
            su - ${SOOS_HDB_SID,,}adm -c "mv $HDB_SHARED_INSTDIR/${SOOS_HDB_HOST} $PERSISTENCE"
        else
            su - ${SOOS_HDB_SID,,}adm -c "rm -r $HDB_SHARED_INSTDIR/${SOOS_HDB_HOST}"
        fi
        su - ${SOOS_HDB_SID,,}adm -c "ln -s $PERSISTENCE/${SOOS_HDB_HOST} $HDB_SHARED_INSTDIR/${SOOS_HDB_HOST}"

        # Remove source host directory
        su - ${SOOS_HDB_SID,,}adm -c "rm -r $HDB_SHARED_INSTDIR/${SOOS_HDB_SOURCE_HOST}"

        NAMESERVER_INI=${SOOS_HDB_BASE_DIR}/shared/${SOOS_HDB_SID}/global/hdb/custom/config/nameserver.ini

        if [ -e $PERSISTENCE/nameserver.ini ]; then
            echo "Using nameserver.ini from '$PERSISTENCE/nameserver.ini'"
            su - ${SOOS_HDB_SID,,}adm -c "mv $NAMESERVER_INI $NAMESERVER_INI.bak"
            su - ${SOOS_HDB_SID,,}adm -c "ln -s $PERSISTENCE/nameserver.ini $NAMESERVER_INI"
        else
            # Adapting database content
            echo "Adapting database content"
            su - ${SOOS_HDB_SID,,}adm -c "hdbnsutil -convertTopology --oldHost=${SOOS_HDB_SOURCE_HOST} --newHost=${SOOS_HDB_HOST}"

            echo "Make nameserver.ini persistent"
            su - ${SOOS_HDB_SID,,}adm -c "cp $NAMESERVER_INI $NAMESERVER_INI.bak"
            su - ${SOOS_HDB_SID,,}adm -c "mv $NAMESERVER_INI $PERSISTENCE/nameserver.ini"
            su - ${SOOS_HDB_SID,,}adm -c "ln -s $PERSISTENCE/nameserver.ini $NAMESERVER_INI"
        fi

        # In case of Renaming the Database Host the Start of the Instance must not be done during the hdblcm.
        echo "Starting HANA Database"
        su - ${SOOS_HDB_SID,,}adm -c "HDB start"
    fi
fi
