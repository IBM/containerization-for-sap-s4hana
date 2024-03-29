# ------------------------------------------------------------------------
# Copyright 2020, 2022 IBM Corp. All Rights Reserved.
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
import pathlib
import socket
import time
import yaml


# Local modules

from modules.command    import CmdSsh
from modules.configbase import ConfigBase
from modules.fail       import fail, warn
from modules.messages   import getMessage
from modules.nestedns   import objToNestedNs
from modules.tools      import (
    getSpsLevelHdb,
    isRepoAccessible,
    getSAPPfparValue
)


# Classes

class _DiscoveryError(Exception):
    pass


class Config(ConfigBase):
    """ Configuration management """

    def __init__(self, ctx, create=False, failOnDiscoveryError=True):
        configFile = ctx.ar.config_file

        self._noFileMsg = f"Configuration file '{configFile}' does not exist"

        self._cmdSshNws4 = None  # Set in _discoverNws4()
        self._cmdSshHdb  = None  # Set in _discoverHdb()

        super().__init__(ctx, './config.yaml.template', configFile, create)

        if create:
            return

        configCacheFile    = f'{configFile}.cache'
        configCacheTimeout = 600  # seconds

        configMtime      = self._getMtime(configFile)  # seconds since the Epoch
        configCacheMtime = self._getMtime(configCacheFile)

        # self._config = ConfigBase.cleanup(self._getConfigFromFile(configFile))
        self._config = self.getObj()
        configCached = self._read(configCacheFile)

        if not configCached:
            # Config cache file does not exist -> discover
            logging.debug(f"Config cache file '{configCacheFile}' does not exist")
            self._discoverAndCache(configCacheFile, configCacheTimeout,
                                   failOnDiscoveryError)

        elif self._referenceSystemChanged(configCached):
            # Reference SAP system changed
            self._discoverAndCache(configCacheFile, configCacheTimeout,
                                   failOnDiscoveryError)

        elif configMtime > configCacheMtime:
            # Original config was changed after config was cached
            logging.debug(f"Configuration file '{configFile}' is newer"
                          f" than cached configuration '{configCacheFile}'")
            self._discoverAndCache(configCacheFile, configCacheTimeout,
                                   failOnDiscoveryError)

        elif float(configCached['expiryTime']) < self._getCurrentTime():
            # Cached config is expired
            logging.debug('Cached configuration is expired')
            self._discoverAndCache(configCacheFile, configCacheTimeout,
                                   failOnDiscoveryError)

        else:
            logging.debug(f"Using cached configuration from '{configCacheFile}'")
            self._config = configCached

        logging.debug(f'self._config >>>{self._config}<<<')

    # Public methods

    def getFull(self):
        """ Get full configuration (inlcuding discovered parts) as nested namespace """
        logging.debug(f'self._config >>>{self._config}<<<')
        cleaned = ConfigBase.cleanup(self._config)
        logging.debug(f'cleaned >>>{cleaned}<<<')
        # return objToNestedNs(ConfigBase.cleanup(self._config))
        return objToNestedNs(self._config)

    def getImageFlavors(self):
        """ Get image flavors """
        return list(self._config['images'].keys())

    def getContainerFlavors(self):
        """ Get image flavors """
        return list(self._config['ocp']['containers'].keys())

    # Private methods

    def _getCurrentTime(self, ):
        return time.time()

    def _getMtime(self, file):
        mtime = -1
        if pathlib.Path(file).exists():
            mtime = pathlib.Path(file).stat().st_mtime
        return mtime

    def _referenceSystemChanged(self, configCached):
        """ Check whether configured reference system differs from cached reference system """

        configuredHost = self._config['refsys']['nws4']['host']['name']
        configuredSid  = self._config['refsys']['nws4']['sid'].upper()
        cachedHost = configCached['refsys']['nws4']['host']['name']
        cachedSid  = configCached['refsys']['nws4']['sidU']

        systemChanged = False
        systemChanged = systemChanged or configuredHost != cachedHost
        systemChanged = systemChanged or configuredSid != cachedSid

        if systemChanged:
            logging.debug(f"Configured reference system '{configuredSid}@{configuredHost}'"
                          f" differs from cached reference system '{cachedSid}@{cachedHost}'")

        return systemChanged

    def _discoverAndCache(self, configCacheFile, configCacheTimeout, failOnDiscoveryError):
        logging.debug('Running configuration discovery')

        # self._checkRequiredOptional()

        try:
            self._discover()
            self._config['expiryTime'] = str(self._getCurrentTime()+configCacheTimeout)

            logging.debug(f"Writing config to cache file '{configCacheFile}'")

            # pylint: disable=unspecified-encoding
            with open(configCacheFile, 'w') as ccfh:
                yaml.dump(self._config, stream=ccfh)
        except _DiscoveryError as derr:
            message  =  '\nThe following problem occured during configuration discovery:\n\n'
            message += f"{'-'*65}\n"
            message += f'{derr}\n'
            message += f"{'-'*65}\n"
            if failOnDiscoveryError:
                fail(message)
            else:
                message += '\nThe configuration cache file was not written. Proceeding with\n'
                message += 'possibly incomplete configuration. This may lead to runtime\n'
                message += 'errors. Check your configuration file\n\n'
                message += f"    {self._instanceFile }\n\n"
                message += 'and correct the error.\n\n'
                warn(message)

    def _discover(self):
        self._config['images'] = {}
        self._discoverNfs()
        self._discoverInit()
        self._discoverNws4()
        self._discoverHdb()
        self._discoverOcp()

    def _getInstno(self, cmdSsh, sidU, instPrefix, host):
        cmd = f'grep -E "SAPSYSTEM +" /usr/sap/{sidU}/SYS/profile/{sidU}_{instPrefix}*_{host}'
        result = cmdSsh.run(cmd)
        if result.rc > 0:
            raise _DiscoveryError(
                f"Could not discover instance number of {sidU} on host {host}\n"
                f"The profile"
                f" /usr/sap/{sidU}/SYS/profile/{sidU}_{instPrefix}*_{host}"
                f" might not exist.\n"
                f"Check if the parameters you specified for your SAP reference"
                f" system are valid."
            )

        return result.out.split('\n')[0].split()[2]

    def _getTimeZone(self, cmdSsh):
        return cmdSsh.run('timedatectl | grep  Time | cut -d ":" -f2 | cut -d " " -f2').out

    def _getHostByName(self, host):
        try:
            ipAddr = socket.gethostbyname(host)
        except Exception as nameResolutionError:
            raise _DiscoveryError(
                f"Cannot resolve IP address for '{host}'\n"
                f"Ensure that hostname '{host}' is correct,\n"
                f"and check the name resolution record of it."
            ) from nameResolutionError
        return ipAddr

    def _getImageNames(self, flavor):
        if flavor == 'init':
            short = 'soos-init'
        else:
            short = f'soos-{self._config["refsys"][flavor]["sidL"]}'

        local = f'localhost/{short}:latest'

        ocp   = f'default-route-openshift-image-registry.apps.{self._config["ocp"]["domain"]}'
        ocp  += f'/{self._config["ocp"]["project"]}/{short}:latest'

        return {
            'short': short,
            'local': local,
            'ocp':   ocp
        }

    def _getContainerName(self, containerFlavor):
        if containerFlavor in ['init', 'hdb']:
            shortName = self._config['images'][containerFlavor]['names']['short']

        elif containerFlavor in ['di', 'ascs']:
            shortName = f"{self._config['images']['nws4']['names']['short']}-{containerFlavor}"

        else:
            raise _DiscoveryError(f"Unknown container flavor '{containerFlavor}'")

        return shortName

    def _discoverInit(self):
        # Image names

        self._config['images']['init'] = {'names': self._getImageNames('init')}

    def _discoverNws4(self):

        # Host and <sid>adm user

        host = self._config['refsys']['nws4']['host']['name']
        sidL = self._config['refsys']['nws4']['sid'].lower()
        sidU = self._config['refsys']['nws4']['sid'].upper()

        self._config['refsys']['nws4']['sidL'] = sidL
        self._config['refsys']['nws4']['sidU'] = sidU
        del self._config['refsys']['nws4']['sid']

        user = self._ctx.cr.refsys.nws4.sidadm
        if user.name != f'{sidL}adm':
            raise _DiscoveryError(
                f"Mismatch between credentials file nws4 user name '{user.name}'\n"
                f"and derived configuration file nws4 user name '{sidL}adm.'\n"
                f"Check credentials file parameter 'refsys.nws4.sidadm.name' and\n"
                f"configuration file parameter 'refsys.nws4.sid' and correct the\n"
                f"wrong value."
            )

        self._config['refsys']['nws4']['host']['ip'] = self._getHostByName(host)

        self._cmdSshNws4 = CmdSsh(self._ctx, host, user, check=False)
        if self._cmdSshNws4.passwordNeeded():
            print(f"Enter password for user {user.name} running on {host}")
        res = self._cmdSshNws4.run('true')

        if res.rc != 0:
            msg = self._cmdSshNws4.formatSshError(res, host, user)
            raise _DiscoveryError(
                f"{msg}\n\n"
                "In addition neither the\n"
                "   - SAP SID of the HANA instance\n"
                "nor the\n"
                "   - the hostname on which the HANA instance is running\n"
                "can be discovered\n"
            )

        # User and group ID of <sid>adm

        (uid, gid) = self._cmdSshNws4.run(f'grep "{user.name}" /etc/passwd').out.split(':')[2:4]
        self._config['refsys']['nws4']['sidadm'] = {'uid': uid, 'gid': gid}

        # Time zone

        self._config['refsys']['nws4']['timezone'] = self._getTimeZone(self._cmdSshNws4)

        # sapmnt base directory

        self._config['refsys']['nws4']['base'] = {}
        self._config['refsys']['nws4']['base']['sapmnt'] = self._getSapmntDir(sidU)

        # SAPFQDN
        defaultProfile = self._getDefaultProfile(sidU)
        result = self._cmdSshNws4.run(
            f'grep "^SAPFQDN" {defaultProfile}'
        )

        if result.rc > 0:
            logging.warning("Could not discover SAPFQDN "
                            f"from {defaultProfile}")
            self._config['refsys']['nws4']['sapfqdn'] = ""
        else:
            self._config['refsys']['nws4']['sapfqdn'] = result.out.split('\n')[0].split()[2]

        # Instance specific parameters

        ascsInstno = self._getInstno(self._cmdSshNws4, sidU, 'ASCS', host)
        diInstno   = self._getInstno(self._cmdSshNws4, sidU, 'D', host)

        self._config['refsys']['nws4']['ascs'] = {
            # Instance number
            'instno': ascsInstno,

            # Default profile name
            'profile': f'{sidU}_ASCS{ascsInstno}_{host}'
        }

        self._config['refsys']['nws4']['di'] = {
            # Instance number
            'instno': diInstno,

            # Default profile name
            'profile': f'{sidU}_D{diInstno}_{host}'
        }

        # Image names

        self._config['images']['nws4'] = {'names': self._getImageNames('nws4')}

        # Set optional package names to be installed

        self._config['images']['nws4']['packages'] = []

    def _discoverHdb(self):
        self._config['refsys']['hdb'] = {}

        host = self._discoverHdbHost()
        sid  = self._discoverHdbSid()
        sidL = sid.lower()
        sidU = sid.upper()

        # self._config['refsys']['hdb']['sid']  = sid
        self._config['refsys']['hdb']['sidL'] = sidL
        self._config['refsys']['hdb']['sidU'] = sidU

        user = self._ctx.cr.refsys.hdb.sidadm
        if user.name != f'{sidL}adm':
            raise _DiscoveryError(
                f"Mismatch between credentials file hdb user name '{user.name}'\n"
                f"and derived configuration file hdb user name '{sidL}adm.'\n"
                f"Check credentials file parameter 'refsys.hdb.sidadm.name' and\n"
                f"configuration file parameter 'refsys.hdb.sid' and correct the\n"
                f"wrong value."
            )

        self._config['refsys']['hdb']['host'] = {
            'name': host,
            'ip':   self._getHostByName(host)
        }

        self._cmdSshHdb = CmdSsh(self._ctx, host, user, check=False)
        if self._cmdSshHdb.passwordNeeded():
            print(f"Enter password for user {user.name} running on {host}")
        res = self._cmdSshHdb.run('true')

        if res.rc != 0:
            msg = self._cmdSshHdb.formatSshError(res, host, user)
            raise _DiscoveryError(
                f"{msg}\n\n"
            )

        # User and group ID of <sid>adm
        # Must be performed on HDB host!

        result = self._cmdSshHdb.run(f'grep "{user.name}" /etc/passwd')
        if result.rc > 0:
            raise _DiscoveryError(f"Could not discover uid and gid for user {user.name}.")
        (uid, gid) = result.out.split(':')[2:4]
        self._config['refsys']['hdb']['sidadm'] = {'uid': uid, 'gid': gid}

        # Time zone

        self._config['refsys']['hdb']['timezone'] = self._getTimeZone(self._cmdSshHdb)

        # Instance specific parameters
        # Must be performed on HDB host!

        # Instance number

        self._config['refsys']['hdb']['instno'] = self._getInstno(self._cmdSshHdb,
                                                                  sidU, 'HDB', host)

        # HDB host rename

        nws4HostName = self._config['refsys']['nws4']['host']['name']
        hdbHostName  = self._config['refsys']['hdb']['host']['name']

        if nws4HostName == hdbHostName:
            self._config['refsys']['hdb']['rename'] = 'no'
        else:
            self._config['refsys']['hdb']['rename'] = 'yes'

        # HDB base directories

        self._config['refsys']['hdb']['base'] = {}
        self._config['refsys']['hdb']['base']['shared'] = self._discoverHdbBaseShared(sidU)
        self._config['refsys']['hdb']['base']['data']   = self._discoverHdbBaseData(sidU)
        self._config['refsys']['hdb']['base']['log']    = self._discoverHdbBaseLog(sidU)

        # Image names

        self._config['images']['hdb'] = {'names': self._getImageNames('hdb')}

        # Set optional packages
        packages = self._discoverHdbOptPkgs()
        logging.debug(f'Optional packages for hdb: {packages}')
        self._config['images']['hdb']['packages'] = packages

    def _discoverNfs(self):
        if not self._config['nfs']['host']['name']:
            self._config['nfs']['host']['name'] = self._config['ocp']['helper']['host']['name']

        hostIp = self._getHostByName(self._config['nfs']['host']['name'])
        self._config['nfs']['host']['ip'] = hostIp

    def _discoverOcp(self):
        project = self._config['ocp']['project']

        hostIp = self._getHostByName(self._config['ocp']['helper']['host']['name'])
        self._config['ocp']['helper']['host']['ip'] = hostIp

        self._config['ocp']['sa'] = {
            'name':     f'{project}-sa',
            'file': f'{project}-service-account.yaml'
        }

        # Containers

        self._config['ocp']['containers']['init'] = {}

        self._config['ocp']['containers']['init']['name'] = self._getContainerName('init')
        self._config['ocp']['containers']['hdb']['name']  = self._getContainerName('hdb')
        self._config['ocp']['containers']['ascs']['name'] = self._getContainerName('ascs')
        self._config['ocp']['containers']['di']['name']   = self._getContainerName('di')

        # Set requested resources for containers

        logging.debug(f'config >>>{yaml.dump(self._config)}<<<')

        # Memory for HDB container
        #
        # discovered size for HDB container:
        # size of the HANA filesystem
        # Value for both limits and requests are set to discovered size
        # if no value specified in configuration

        hdbMinMem  =  f'{self._discoverHdbSizeGiB()}Gi'

        logging.debug(f'config >>>{yaml.dump(self._config)}<<<')
        for kind in ('requests', 'limits'):
            res = self._config['ocp']['containers']['hdb']['resources'][kind]
            if not res['memory']:
                res['memory'] = hdbMinMem
                logging.warning(getMessage("msgL001", kind, "HDB", hdbMinMem))

        # Memory for NWS4 Dialog Instance container
        #
        # discovered size for NWS4 DI container:
        # PHYS_MEMSIZE if available in Instance Profile
        # or 10 percent of physical memory size of reference system, at least 32GiB
        # Value for both limits and requests are set to discovered size
        # if no value specified in configuration

        diMinMem  =  f'{self._discoverDiSizeGiB()}Gi'

        logging.debug(f'config >>>{yaml.dump(self._config)}<<<')
        for kind in ('requests', 'limits'):
            res = self._config['ocp']['containers']['di']['resources'][kind]
            if not res['memory']:
                res['memory'] = diMinMem
                logging.warning(getMessage("msgL001", kind, "Dialog Instance", diMinMem))

    def _discoverHdbSid(self):
        defaultProfile = self._getDefaultProfile(self._config['refsys']['nws4']['sidU'])
        cmd = f'grep dbs/hdb/dbname {defaultProfile}'
        result = self._cmdSshNws4.run(cmd)
        if result.rc > 0:
            raise _DiscoveryError(f"Could not discover HANA SID from {defaultProfile}")
        return result.out.split('=')[1].strip()

    def _discoverHdbHost(self):
        defaultProfile = self._getDefaultProfile(self._config['refsys']['nws4']['sidU'])
        cmd = f'grep SAPDBHOST {defaultProfile}'
        result = self._cmdSshNws4.run(cmd)
        if result.rc > 0:
            raise _DiscoveryError(f"Could not discover SAPDBHOST from {defaultProfile}")
        return result.out.split('=')[1].strip()

    def _discoverHdbBaseShared(self, sidU):
        profile   = f'/usr/sap/{sidU}/SYS/profile'
        out       = self._cmdSshHdb.run(f'readlink {profile}').out
        # example for out:
        # /hana/shared/SID/profile
        # after splitting it:
        # ['','hana','shared','SID','profile']
        # We ignore the last three components
        return '/'.join(out.split('/')[:-3])

    def _discoverHdbBaseData(self, sidU):
        return self._getBasePathFromGlobalIni(sidU, 'data')

    def _discoverHdbBaseLog(self, sidU):
        return self._getBasePathFromGlobalIni(sidU, 'log')

    def _discoverHdbSizeGiB(self):
        """ Discover storage in GiB needed for HDB content """
        sidU    = self._config['refsys']['hdb']['sidU']
        dataDir = f"{self._config['refsys']['hdb']['base']['data']}/data/{sidU}"
        out = self._cmdSshHdb.run(f'du -s -B 1G {dataDir} | cut -f1').out
        return int(out) + self._ctx.cs.additionalFreeSpaceHdbGiB

    def _discoverHdbOptPkgs(self):
        # to get the version of the HANA DB, we need the path to the instance directory
        sidU   = self._config['refsys']['hdb']['sidU']
        instno = self._config['refsys']['hdb']['instno']
        spsLevel = getSpsLevelHdb(self._cmdSshHdb, sidU, instno)
        logging.debug(f'HANA DB SPS Level: {spsLevel}')

        optionalHdbPkgs = []
        for pkg in self._ctx.cs.optionalHdbPkgs:
            if pkg.minSpsLevel <= spsLevel < pkg.maxSpsLevel:
                logging.debug(f'Optional package to be installed: {pkg.packageName}')
                logging.debug(f'enabling repository: {pkg.repository}')
                pkg.dnfInstallable  = isRepoAccessible(pkg.repository)
                optionalHdbPkgs.append(pkg)
        return optionalHdbPkgs

    def _discoverDiSizeGiB(self):
        """ Discover storage in GiB needed for Dialog Instance """
        memsize = self._discoverDiSizeFromInstProfileGiB()
        if memsize > 0:
            return memsize
        return max(self._discoverDiSizeFromRefHostGiB(), self._ctx.cs.minMemSizeDIGiB)

    def _discoverDiSizeFromInstProfileGiB(self):
        profile      = self._getInstanceProfile()
        memsizeInMiB = self._cmdSshNws4.run(f'grep PHYS_MEMSIZE {profile} | cut -d = -f2').out
        if not memsizeInMiB:
            return 0
        return int(memsizeInMiB) // 1024

    def _discoverDiSizeFromRefHostGiB(self):
        # Output of 'grep MemTotal /proc/meminfo' looks like:
        # MemTotal:       64819648 kB
        #
        cmd  = "grep MemTotal /proc/meminfo "
        cmd += "| cut -d : -f2 "
        memsizeInKb  = int(self._cmdSshNws4.run(cmd).out.split()[0])
        memsizeInGiB = memsizeInKb // 1024 // 1024

        # The size is set to 10% of MemTotal (according to SAP Settings)
        return memsizeInGiB // 10

    def _getSapmntDir(self, sidU):
        profilePath   = self._cmdSshNws4.run(f'find /usr/sap/ -type l -ipath '
                                             f'"*{sidU}/SYS/profile"').out
        profileTarget = self._cmdSshNws4.run(f'readlink "{profilePath}"').out
        return profileTarget[0:profileTarget.index(f'/{sidU}/profile')]

    def _getInstanceProfile(self):
        sidU     = self._config['refsys']['nws4']['sidU']
        profile  = f'/usr/sap/{sidU}/SYS/profile/'
        profile += self._config['refsys']['nws4']['di']['profile']
        return profile

    def _getDefaultProfile(self, sidU):
        return f'/usr/sap/{sidU}/SYS/profile/DEFAULT.PFL'

    def _getBasePathFromGlobalIni(self, sidU, baseType):
        if baseType not in ['data', 'log']:
            raise _DiscoveryError(
                "Internal error: wrong baseType specified"
            )
        # There exist more than on location of the global.ini
        # They are ordered in different layers:
        # Default
        # System
        # Database
        # Host
        # The parameters are taken from top to bottom.
        # https://help.sap.com/viewer/6b94445c94ae495c83a19646e7c3fd56/2.0.04/en-US/3f1a6a7dc31049409e1a9f9108d73d51.html

        instno   = self._config['refsys']['hdb']['instno']
        hostname = self._config['refsys']['hdb']['host']['name']
        sapmnt   = self._config['refsys']['hdb']['base']['shared']

        locationlist = [
            f"/usr/sap/{sidU}/HDB{instno}/exe/config",
            f"{sapmnt}/{sidU}/SYS/global/hdb/custom/config",
            f"/usr/sap/{sidU}/SYS/global/hdb/custom/config",
            f"{sapmnt}/{sidU}/SYS/global/hdb/custom/config/DB_{sidU}",
            f"/usr/sap/{sidU}/SYS/global/hdb/custom/config/DB_{sidU}",
            f"/usr/sap/{sidU}/HDB{instno}/{hostname}"
        ]

        for location in locationlist:
            basepath = f"basepath_{baseType}volumes"
            cmd = f'grep "{basepath}[= ]" {location}/global.ini'
            result = self._cmdSshHdb.run(cmd)
            if result.rc == 0:
                # Example for result.out
                # basepath_datavolumes = /sapmnt/hana/data/HD1
                # We need the basepath, which means:
                # /sapmnt/hana

                # Get first the complete path itself
                tempPath = result.out.split('=')[1].strip()

                # Then the basepath itself
                path = '/'.join(tempPath.split('/')[:-2])

        # It might happen that the path contains a SAP profile/environment variable
        # such as $(DIR_GLOBAL). This must be replaced.
        # The parameter value can be got from call sappfpar
        path = self._replaceSAPPfpar(sidU, path)
        if not path:
            raise _DiscoveryError(
                f"Could not get the base path for {basepath} from one of the global.ini files"
            )
        return path

    def _replaceSAPPfpar(self, sidU, path):
        if "$(" not in path:
            return path

        subDirs = path.split('/')
        for subDir in subDirs:
            if "$(" in subDir:
                sappfpar = subDir
                value = getSAPPfparValue(self._cmdSshHdb, sidU, "hdb", sappfpar)
                if not value:
                    raise _DiscoveryError(
                        f"Could not get value for {sappfpar} from sappfpar call"
                    )
                subDirs[subDirs.index(sappfpar)] = value
                break
        return '/'.join(subDirs)
