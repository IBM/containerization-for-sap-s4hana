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

# Write env-file with variables for all instances
env | grep SOOS_GLOBAL | sort > /root/global-env

# Write env-file for both ASCS and DI instance
env | grep SOOS_NWS4 | sort > /root/nws4-env

# Write env-file for ASCS instance
env | grep SOOS_ASCS | sort > /root/ascs-env

sed -e "s/SOOS_ASCS_PROFILE/SOOS_NWS4_PROFILE/g" \
    -e "s/SOOS_ASCS_INSTNO/SOOS_NWS4_INSTNO/g" \
    -e "1iSOOS_NWS4_INSTTYPE=ASCS" \
         /root/ascs-env > /root/ascs-env-mod

cat /root/global-env /root/nws4-env /root/ascs-env-mod > /envdir-ascs/soos-env

# Write env-file for DI instance
env | grep SOOS_DI | sort > /root/di-env

sed -e "s/SOOS_DI_PROFILE/SOOS_NWS4_PROFILE/g" \
    -e "s/SOOS_DI_INSTNO/SOOS_NWS4_INSTNO/g" \
    -e "1iSOOS_NWS4_INSTTYPE=DI" \
         /root/di-env > /root/di-env-mod

cat /root/global-env /root/nws4-env /root/di-env-mod > /envdir-di/soos-env

# Write env-file for HDB instance
env | grep SOOS_HDB | sort > /root/hdb-env
cat /root/global-env /root/hdb-env > /envdir-hdb/soos-env
