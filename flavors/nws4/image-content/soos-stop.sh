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

# Stop Instances

# for i in $(/usr/sap/hostctrl/exe/saphostctrl -function ListInstances | cut -d- -f2); do
    echo "Stopping instance $i"
    # /usr/sap/hostctrl/exe/sapcontrol -nr "$i" -function Stop
  su - ${SOOS_NWS4_SID,,}adm -c "/usr/sap/$SOOS_NWS4_SID/SYS/exe/run/sapcontrol -nr "${SOOS_NWS4_INSTNO}" -function Stop"
# done
