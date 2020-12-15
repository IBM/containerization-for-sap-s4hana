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

""" Configuration file handling """

# Global modules

import logging
import pprint
import socket
import yaml

# Local modules

from modules.command import CmdSsh
from modules.tools   import nestedNamespace


# Functions


def getConfig(configFile, discover=False):
    """ Get configuration from configuartion file """
    config = yaml.load(open(configFile, 'r'), Loader=yaml.Loader)
    logging.debug(f'Before discovery >>>\n{pprint.pformat(config)}\n<<<')
    if discover:
        _discover(config)
        logging.debug(f'After discovery >>>\n{pprint.pformat(config)}\n<<<')
    config = nestedNamespace(config)
    logging.debug(f'Returning >>>\n{pprint.pformat(config)}\n<<<')
    return config


def getFlavors(config):
    """ Get image flavors """
    return list(vars(config.flavor).keys())

# Private functions


def _discover(config):
    _discoverNfs(config)
    _discoverInit(config)
    _discoverNws4(config)
    _discoverHdb(config)
    _discoverOcp(config)


def _getInstNo(cmdSsh, sid, instPrefix, host):
    cmd = f'grep -E "SAPSYSTEM +" /usr/sap/{sid}/SYS/profile/{sid}_{instPrefix}*_{host}'
    return cmdSsh.run(cmd).out.split('\n')[0].split()[2]


def _getTimeZone(cmdSsh):
    return cmdSsh.run('timedatectl show | grep -i timezone').out.split('=')[1]


def _getImageNames(config, flavor):
    if flavor == 'init':
        short = 'soos-init'
    else:
        short = f'soos-{config["flavor"][flavor]["sid"].lower()}'
    # pylint: disable=bad-whitespace
    local = f'localhost/{short}:latest'
    ocp   = f'default-route-openshift-image-registry.apps.{config["ocp"]["domain"]}'
    ocp  += f'/{config["ocp"]["project"]}/{short}:latest'
    return {
        'short': short,
        'local': local,
        'ocp':   ocp
    }


def _getContainerName(config, flavor):
    shortName = config["flavor"][flavor]["imageNames"]["short"]
    if flavor == 'nws4':  # pylint: disable=R1705
        shortName = {
            'ascs': f'{shortName}-ascs',
            'di':   f'{shortName}-di'
        }
    return shortName


def _discoverInit(config):
    config['flavor']['init'] = {}

    # Image names

    config['flavor']['init']['imageNames'] = _getImageNames(config, 'init')

    # Container name

    config['flavor']['init']['containerName'] = _getContainerName(config, 'init')


def _discoverNws4(config):
    # pylint: disable=bad-whitespace
    sid  = config['flavor']['nws4']['sid'].upper()
    host = config['flavor']['nws4']['host']
    user = config['flavor']['nws4']['user']

    cmdSsh = CmdSsh(host, user)

    # Initialize instance specific dictionaries

    config['flavor']['nws4']['ascs'] = {}
    config['flavor']['nws4']['di']   = {}

    # Time zone

    config['flavor']['nws4']['timezone'] = _getTimeZone(cmdSsh)

    # Instance numbers

    ascsInstNo = _getInstNo(cmdSsh, sid, 'ASCS', host)
    diInstNo   = _getInstNo(cmdSsh, sid, 'D', host)

    config['flavor']['nws4']['ascs']['instNo'] = ascsInstNo
    config['flavor']['nws4']['di']['instNo']   = diInstNo

    # Image names

    config['flavor']['nws4']['imageNames'] = _getImageNames(config, 'nws4')

    # Container names

    config['flavor']['nws4']['ascs']['containerName'] = _getContainerName(config, 'nws4')['ascs']
    config['flavor']['nws4']['di']['containerName']   = _getContainerName(config, 'nws4')['di']

    # SAPFQDN

    config['flavor']['nws4']['sapfqdn'] = cmdSsh.run(
        f'grep "^SAPFQDN" /usr/sap/{sid}/SYS/profile/DEFAULT.PFL').out.split('\n')[0].split()[2]

    # Default profile names

    config['flavor']['nws4']['ascs']['profileName'] = f'{sid}_ASCS{ascsInstNo}_{host}'
    config['flavor']['nws4']['di']['profileName']   = f'{sid}_D{diInstNo}_{host}'

    del cmdSsh


def _discoverHdb(config):
    # pylint: disable=bad-whitespace
    config['flavor']['hdb'] = {}
    cmdSsh = CmdSsh(config['flavor']['nws4']['host'], config['flavor']['nws4']['user'])

    host = _discoverHdbHost(cmdSsh, config)
    user = _discoverHdbUser(config)
    sid  = _discoverHdbSid(cmdSsh, config)
    base = _discoverHdbBase(sid, host, user)

    config['flavor']['hdb']['host'] = host
    config['flavor']['hdb']['user'] = user
    config['flavor']['hdb']['sid']  = sid
    config['flavor']['hdb']['base'] = base

    # Time zone

    config['flavor']['hdb']['timezone'] = _getTimeZone(cmdSsh)

    # Instance numbers

    config['flavor']['hdb']['instNo'] = _getInstNo(cmdSsh, sid, 'HDB', host)

    # Image name

    config['flavor']['hdb']['imageNames'] = _getImageNames(config, 'hdb')

    # Container name

    config['flavor']['hdb']['containerName'] = _getContainerName(config, 'hdb')

    del cmdSsh


def _discoverNfs(config):
    config['nfs']['ip'] = socket.gethostbyname(config['nfs']['host'])


def _discoverOcp(config):
    # pylint: disable=bad-whitespace
    project = config['ocp']['project']
    nws4Sid = config['flavor']['nws4']['sid'].lower()
    hdbSid  = config['flavor']['hdb']['sid'].lower()

    config['ocp']['helperHost']             = f'api.{config["ocp"]["domain"]}'
    config['ocp']['serviceAccountName']     = f'{project}-sa'
    config['ocp']['serviceAccountFileName'] = f'{project}-service-account.yaml'
    config['ocp']['deploymentFileName']     = f'{project}-deployment-{nws4Sid}-{hdbSid}.yaml'


def _discoverHdbSid(cmdSsh, config):
    return cmdSsh.run(f'grep dbs/hdb/dbname {_getDefaultPfl(config)}').out.split('=')[1].strip()


def _discoverHdbHost(cmdSsh, config):
    return cmdSsh.run(f'grep SAPDBHOST {_getDefaultPfl(config)}').out.split('=')[1].strip()


def _discoverHdbUser(config):
    # TODO when we support Distributed and/or HA user must be part of config.yaml!
    return config['flavor']['nws4']['user']


def _discoverHdbBase(sid, host, user):
    # pylint: disable=bad-whitespace
    hdbCmdSsh = CmdSsh(host, user)
    profile   = f'/usr/sap/{sid}/SYS/profile'
    out       = hdbCmdSsh.run(f'readlink {profile}').out
    # example for out:
    # /hana/shared/SID/profile
    # after splitting it:
    # ['','hana','shared','SID','profile']
    # We ignore the last three components
    del hdbCmdSsh
    return '/'.join(out.split('/')[:-3])


def _getDefaultPfl(config):
    sid = config['flavor']['nws4']['sid']
    return f'/usr/sap/{sid}/SYS/profile/DEFAULT.PFL'
