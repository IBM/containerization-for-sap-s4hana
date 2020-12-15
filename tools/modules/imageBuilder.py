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

""" Build container images from existing SAP Netweaver or SAP S/4 HANA system """

# Global modules

from   datetime import date
import logging
import sys
import tempfile
import types
import os

# Local modules

from modules.command    import (
    CmdShell,
    CmdSsh
)
from modules.remoteCopy import RemoteCopy
from modules.tools      import (
    genFileFromTemplate,
    pushd
)

# Classes


class BuilderFactory:
    """ Factory class for image builder objects """
    @classmethod
    def getBuilder(cls, flavor):
        """ Get image builder for specific flavor """
        if flavor == 'nws4':
            return BuilderNws4()
        if flavor == 'hdb':
            return BuilderHdb()
        # This should never be reached
        logging.error(f"Unknown flavor '{flavor}'")
        sys.exit(1)


class Builder():
    """ Build container images """

    def __init__(self):
        # pylint: disable=bad-whitespace
        self._host        = None
        self._user        = None
        self._cmdShell    = CmdShell()
        self._cmdSsh      = None
        self._remoteCopy  = None
        self._flavor      = None
        self._description = None

    def buildImage(self, sapsid, host, user, repoRoot, buildTmpRoot, buildDir, keepFiles):
        """ Build image """
        # pylint: disable=bad-whitespace,too-many-arguments,too-many-locals
        # Initialize ssh connection

        if not self._cmdSsh or host != self._host or user != self._user:
            # Initialize only if not yet initialized or if connection parameters have changed
            if self._cmdSsh:
                del self._cmdSsh
            self._cmdSsh = CmdSsh(host, user)

        # Initialize remote copy connection

        if not self._remoteCopy or host != self._host or user != self._user:
            # Initialize only if not yet initialized or if connection parameters have changed
            if self._remoteCopy:
                del self._remoteCopy
            self._remoteCopy = RemoteCopy(host, user)

        self._host = host
        self._user = user

        # System ID

        sid = types.SimpleNamespace(**{})
        sid.upper = sapsid.upper()
        sid.lower = sapsid.lower()

        logging.debug(f"sid: '{sid}'")

        # Directories

        dirs = types.SimpleNamespace(**{})
        dirs.repoRoot   = repoRoot
        if buildDir and len(buildDir) != 0:
            dirs.build  = buildDir
        else:
            self._cmdShell.run(f'mkdir -p "{buildTmpRoot}"')
            dirs.build  = self._cmdShell.run(f'mktemp -d -p "{buildTmpRoot}" '
                                             f'-t soos-build-{self._flavor}.XXXXXXXXXX').out
        dirs.usrSapReal = self._getUsrSapReal()
        dirs.sapmnt     = self._getSapmntDir(sid)

        self._setDirsFlavor(sid, dirs)

        logging.debug(f"dirs: '{dirs}'")

        # Image properties

        image = types.SimpleNamespace(**{})
        image.name        = f'localhost/soos-{sid.lower}'
        image.version     = 'latest'
        image.tag         = f'{image.name}:{image.version}'
        image.date        = date.today().strftime('%Y-%m-%d')
        image.description = self._description  # Must be set by derived class
        with pushd(dirs.repoRoot):
            image.commit  = self._cmdShell.run('git log --pretty="%H" -1').out
            image.branch  = self._cmdShell.run('git rev-parse --abbrev-ref HEAD').out

        logging.debug(f"image: '{image}'")

        # OS user properties

        (sapadm, sidadm, sapsysGid) = self._getOsUserProperties(sid)

        logging.debug(f"sapadm   : '{sapadm}'")
        logging.debug(f"sidadm   : '{sidadm}'")
        logging.debug(f"sapsysGid: '{sapsysGid}'")

        # Misc

        buildCmd = 'podman'
        remoteOs = 'linux' + self._cmdSsh.run('uname -m').out

        # Start build process

        with tempfile.TemporaryDirectory() as dirs.tmp:
            logging.debug(f"Created temporary directory '{dirs.tmp}'")
            self._cleanupAtStart(dirs, keepFiles)
            self._genBuildContext(sid, dirs, sapadm, sidadm, sapsysGid, host, remoteOs)
            containerfile = self._genContainerfile(sid, dirs, image, sapadm, sidadm, sapsysGid)
            self._buildImage(buildCmd, dirs, image, containerfile)
            self._cleanupAtEnd(dirs)

    def _getUsrSapReal(self):
        # Check whether /usr/sap is a real directory or a symlink to another directory
        usrSapReal = self._cmdSsh.run('readlink /usr/sap').out
        if len(usrSapReal) != 0:
            logging.info(f"Detected that '/usr/sap' is a symbolic link to '{usrSapReal}'")
        else:
            usrSapReal = '/usr/sap'
        logging.debug(f"usrSapReal: '{usrSapReal}'")
        return usrSapReal

    def _getSapmntDir(self, sid):
        # pylint: disable=bad-whitespace
        # Get path of SAP Mount Directory (nws4) or path to 'shared' directory (hdb)
        # XXX ASSUMES THAT ".../<SID>/SYS/profile" IS A SYMBOLIC LINK
        #     WHOSE TARGET PATH STARTS WITH THE WANTED DIRECTORY
        #     DOES THIS ALWAYS WORK?

        profilePath   = self._cmdSsh.run(f'find /usr/sap/ -type l -ipath '
                                         f'"*{sid.upper}/SYS/profile"').out
        profileTarget = self._cmdSsh.run(f'readlink "{profilePath}"').out
        sapmnt        = profileTarget[0:profileTarget.index(f'/{sid.upper}/profile')]

        logging.debug(f"profilePath  : '{profilePath}'")
        logging.debug(f"profileTarget: '{profileTarget}'")
        logging.debug(f"sapmnt       : '{sapmnt}'")

        return sapmnt

    def _setDirsFlavor(self, sid, dirs):
        # Flavor specific directories
        # pylint: disable=unused-argument
        logging.error('This function must be overwritten by derived flavor specific builder class.')
        sys.exit(1)

    def _getOsUserProperties(self, sid):
        # Get properties of sapadm and <sid>adm from remote host /etc/passwd
        #
        # XXX IN CASE THE SOURCE SYSTEM USES YP OR ANOTHER AUTHENTICATION
        #     SETUP THIS NEEDS TO BE DONE DIFFERENTLY!!!

        sapadm = types.SimpleNamespace(**{})
        (_d1,
         _d2,
         sapadm.uid,
         sapsysGid,
         sapadm.comment,
         sapadm.home,
         sapadm.shell
         ) = self._cmdSsh.run("grep '^sapadm:' /etc/passwd").out.split(':')

        sidadm = types.SimpleNamespace(**{})
        (_d1,
         _d2,
         sidadm.uid,
         _d4,
         sidadm.comment,
         sidadm.home,
         sidadm.shell
         ) = self._cmdSsh.run(f"grep '^{sid.lower}adm:' /etc/passwd").out.split(':')

        logging.debug(f'Returning {sapadm}, {sidadm}, {sapsysGid}')

        return (sapadm, sidadm, sapsysGid)

    def _cleanupAtStart(self, dirs, keepFiles):
        # Remove previously copied files if not explicitly asked to keep them
        if not keepFiles:
            logging.info(f"##### Cleaning up build directoy '{dirs.build}' #####")
            with pushd(dirs.build):
                self._cmdShell.run('rm -rf ..?* .[!.]* *')

    def _genBuildContext(self, sid, dirs, sapadm, sidadm, sapsysGid, host, remoteOs):
        # Generate podman build context
        # pylint: disable=too-many-arguments
        filterFilePath = f'{dirs.tmp}/rsync-filter'
        logging.debug(f"filterFilePath: {filterFilePath}")
        with open(filterFilePath, 'w') as fh:  # pylint: disable=invalid-name
            print(self._getRsyncFilter(sid, dirs, remoteOs), file=fh)
        self._genBuildContextFlavor(sid, dirs, sapadm, sidadm, sapsysGid, host, filterFilePath)

    def _getRsyncFilter(self, sid, dirs, remoteOs):
        # Get filter for selective copy depending on flavor
        # pylint: disable=unused-argument
        logging.error('This function must be overwritten by derived flavor specific builder class.')
        sys.exit(1)

    def _genBuildContextFlavor(self, sid, dirs, sapadm, sidadm, sapsysGid, host, filterFilePath):
        # Flavor dependend actions for build context generation
        # pylint: disable=unused-argument,too-many-arguments
        logging.error('This function must be overwritten by derived flavor specific builder class.')
        sys.exit(1)

    def _genContainerfile(self, sid, dirs, image, sapadm, sidadm, sapsysGid):
        # Generate containerfile from template depending on flavor
        # MUST RUN AFTER BUILD CONTEXT SETUP
        # pylint: disable=too-many-arguments
        logging.info("##### Generating Containerfile #####")
        # Common parameters
        if dirs.usrSapReal != '/usr/sap':
            usrSapLinkCmd = f'ln -s {dirs.usrSapReal} /usr/sap'
        else:
            usrSapLinkCmd = 'true'
        params = {
            'IMAGE_BRANCH':       image.branch,
            'IMAGE_COMMIT':       image.commit,
            'IMAGE_DATE':         image.date,
            'IMAGE_DESCRIPTION':  image.description,
            'IMAGE_VERSION':      image.version,
            'SAPADM_COMMENT':     sapadm.comment,
            'SAPADM_HOME':        sapadm.home,
            'SAPADM_SHELL':       sapadm.shell,
            'SAPADM_UID':         sapadm.uid,
            'SAPMNT':             dirs.sapmnt,
            'SAPSYS_GID':         sapsysGid,
            'sid':                sid.lower,
            'SID':                sid.upper,
            'SIDADM_COMMENT':     sidadm.comment,
            'SIDADM_HOME':        sidadm.home,
            'SIDADM_SHELL':       sidadm.shell,
            'SIDADM_UID':         sidadm.uid,
            'USR_SAP_REAL':       dirs.usrSapReal,
            'USR_SAP_LINK_CMD':   usrSapLinkCmd
        }

        copyLibCompat = ''
        installLibCompat = ''
        if os.path.exists(f'{dirs.build}/tmp/containerize'):
            # pylint: disable=bad-whitespace
            packageName = 'compat-sap-c++-9-9.1.1-2.2.el8.ppc64le.rpm'
            copyLibCompat = f'COPY ./tmp/containerize/{packageName} /'
            installLibCompat  = 'RUN dnf install -y libgomp && \\'+'\n'
            installLibCompat += f'    rpm -i /{packageName} && \\'+'\n'
            installLibCompat += f'    rm     /{packageName}'

        params.update({'COPY_LIB_COMPAT': f'{copyLibCompat}'})
        params.update({'INSTALL_LIB_COMPAT': f'{installLibCompat}'})

        params.update(self._getContainerfileParams(sid, dirs))
        containerfile = f'{dirs.tmp}/containerfile'
        genFileFromTemplate(f'{dirs.repoRoot}/flavors/{self._flavor}/containerfile.template',
                            containerfile, params)
        logging.debug(f"Contents of '{containerfile}': >>>\n{open(containerfile).read()}<<<")
        return containerfile

    def _getContainerfileParams(self, sid, dirs):
        # Non-common containerfile template parameters depending on flavor
        # pylint: disable=unused-argument
        logging.error('This function must be overwritten by derived flavor specific builder class.')
        sys.exit(1)

    def _buildImage(self, buildCmd, dirs, image, containerfile):
        # Build image
        # MUST RUN AFTER BUILD CONTEXT SETUP
        # pylint: disable=no-self-use
        logging.info("##### Building image #####")
        with pushd(dirs.build):
            self._cmdShell.run(f'{buildCmd} build -t {image.tag} -f "{containerfile}" .')

    def _cleanupAtEnd(self, dirs):
        # Cleanup after image build
        with pushd(dirs.repoRoot):
            # self._cmdShell.run(f'\\rm -rf {dirs.build}')
            pass

# -------------------------------------------------------------------------


class BuilderNws4(Builder):
    """ Build container images of flavor 'nws4' """

    def __init__(self):
        super().__init__()
        self._flavor = 'nws4'
        self._description = 'Container for SAP S/4HANA'

    def _setDirsFlavor(self, sid, dirs):
        # Flavor specific directories of flavor 'nws4'
        pass  # currently none

    def _getRsyncFilter(self, sid, dirs, remoteOs):
        rsFilter = ''
        rsFilter += f"include {dirs.usrSapReal}/trans\n"
        rsFilter += f"include {dirs.usrSapReal}/{sid.upper}\n"
        rsFilter += f"exclude **.zip\n"
        rsFilter += f"exclude **.old\n"
        rsFilter += f"exclude **.log\n"
        rsFilter += f"exclude **.trc\n"
        rsFilter += f"exclude **.tar.gz\n"
        rsFilter += f"exclude **DEFAULT.*.PFL\n"
        rsFilter += f"exclude **log_backup**\n"
        # rsFilter += f"exclude **.SAR\n"
        rsFilter += f"exclude {dirs.usrSapReal}/trans/log/*\n"
        rsFilter += f"exclude {dirs.usrSapReal}/trans/cofiles/*\n"
        rsFilter += f"exclude {dirs.usrSapReal}/trans/data/*\n"
        rsFilter += f"exclude {dirs.usrSapReal}/trans/tmp/*\n"
        rsFilter += f"exclude {dirs.usrSapReal}/trans/actlog/*\n"
        rsFilter += f"exclude {dirs.usrSapReal}/trans/EPS/*/*\n"
        rsFilter += f"exclude {dirs.usrSapReal}/{sid.upper}/*/work/*\n"
        rsFilter += f"include {dirs.usrSapReal}/{sid.upper}/exe\n"
        rsFilter += f"include {dirs.usrSapReal}/{sid.upper}/exe/uc\n"
        rsFilter += f"include {dirs.usrSapReal}/{sid.upper}/exe/uc/{remoteOs}\n"
        rsFilter += f"include {dirs.usrSapReal}/{sid.upper}/exe/uc/{remoteOs}/**\n"
        rsFilter += f"include {dirs.usrSapReal}/{sid.upper}/D[0-9][0-9]\n"
        rsFilter += f"include {dirs.usrSapReal}/{sid.upper}/D[0-9][0-9]/data\n"
        rsFilter += f"include {dirs.usrSapReal}/{sid.upper}/D[0-9][0-9]/data/icmandir\n"
        rsFilter += f"include {dirs.usrSapReal}/{sid.upper}/D[0-9][0-9]/data/icmandir/**\n"
        rsFilter += f"include {dirs.usrSapReal}/{sid.upper}/D[0-9][0-9]/data/cache\n"
        rsFilter += f"include {dirs.usrSapReal}/{sid.upper}/D[0-9][0-9]/data/cache/**\n"
        rsFilter += f"include {dirs.usrSapReal}/{sid.upper}/D[0-9][0-9]/data/cache/**\n"
        rsFilter += f"exclude {dirs.usrSapReal}/{sid.upper}/D[0-9][0-9]/data/**\n"
        rsFilter += f"exclude {dirs.usrSapReal}/{sid.upper}/D[0-9][0-9]/exe/**\n"
        rsFilter += f"exclude {dirs.usrSapReal}/{sid.upper}/ASCS[0-9][0-9]/exe/**\n"
        rsFilter += f"exclude {dirs.usrSapReal}/{sid.upper}/exe/**\n"
        rsFilter += f"include {dirs.usrSapReal}/trans/**\n"
        rsFilter += f"include {dirs.usrSapReal}/{sid.upper}/**\n"

        return rsFilter

    def _genBuildContextFlavor(self, sid, dirs, sapadm, sidadm, sapsysGid, host, filterFilePath):
        # Flavor 'nws4' dependend actions for build context generation
        # pylint: disable=too-many-arguments
        logging.info('##### Copying build context to temporary build directory #####')

        with pushd(dirs.build):
            self._remoteCopy.copy(f'/usr/sap/{sid.upper}', filterFilePath)  # also copies /sapmnt
            self._remoteCopy.copy(f'/usr/sap/trans', filterFilePath)
            # SAP host agent
            # self._remoteCopy.copy(f'/usr/sap/hostctrl', filterFilePath)
            # self._remoteCopy.copy(f'{sapadm.home}', filterFilePath)
            self._remoteCopy.copy(f'{sidadm.home}', filterFilePath)

            with open(f'.{dirs.usrSapReal}/sapservices', 'w') as fh:  # pylint: disable=invalid-name
                print(self._cmdSsh.run(f'grep {sid.upper} /usr/sap/sapservices').out, file=fh)
            with open('./etc_services_sap', 'w') as fh:  # pylint: disable=invalid-name
                print(self._cmdSsh.run("grep '^sap' /etc/services").out, file=fh)

            with open('./etc_security_limits.conf', 'w') as fh:  # pylint: disable=invalid-name
                print(self._cmdSsh.run("grep '@sapsys'   /etc/security/limits.conf").out, file=fh)
                print(self._cmdSsh.run("grep '@dba'      /etc/security/limits.conf").out, file=fh)
                print(self._cmdSsh.run(f"grep '{sid}adm' /etc/security/limits.conf").out, file=fh)

            self._cmdShell.run(f'cp -af'
                               f' "{dirs.repoRoot}/flavors/nws4/image-content/soos.service"  ./')
            self._cmdShell.run(f'cp -af'
                               f' "{dirs.repoRoot}/flavors/nws4/image-content/soos-start.sh" ./')
            self._cmdShell.run(f'cp -af'
                               f' "{dirs.repoRoot}/flavors/nws4/image-content/soos-stop.sh"  ./')

    def _getContainerfileParams(self, sid, dirs):
        # Non-common containerfile template parameters for flavor 'nws4'
        return {
            # Currently none
        }

# -------------------------------------------------------------------------


class BuilderHdb(Builder):
    """ Build container images of flavor 'hdb' """

    def __init__(self):
        # pylint: disable=bad-whitespace
        super().__init__()
        self._flavor      = 'hdb'
        self._description = 'Container for SAP HANA'

    def _setDirsFlavor(self, sid, dirs):
        # Flavor specific directories of flavor 'hdb'
        # pylint: disable=bad-whitespace
        targetMountdir     = dirs.sapmnt[0:dirs.sapmnt.rindex('/')]  # cut off trailing '/shared'
        dirs.hanaSharedSid = f'{targetMountdir}/shared/{sid.upper}'
        logging.debug(f"dirs.hanaSharedSid: '{dirs.hanaSharedSid}'")

    def _getRsyncFilter(self, sid, dirs, remoteOs):
        rsFilter = ''
        rsFilter += f'exclude **.zip\n'
        rsFilter += f'exclude **.old\n'
        rsFilter += f'exclude **.log\n'
        rsFilter += f'exclude **.trc\n'
        rsFilter += f'exclude **.tar.gz\n'
        rsFilter += f'exclude **DEFAULT.*.PFL\n'
        rsFilter += f'exclude **log_backup**\n'
        rsFilter += f'include {dirs.hanaSharedSid}/**\n'
        rsFilter += f'include /tmp/containerize/**\n'

        return rsFilter

    def _genBuildContextFlavor(self, sid, dirs, sapadm, sidadm, sapsysGid, host, filterFilePath):
        # Flavor 'hdb' dependend actions for build context generation
        # pylint: disable=too-many-arguments

        logging.info('##### Copying build context to temporary build directory #####')

        with pushd(dirs.build):
            self._remoteCopy.copy(dirs.hanaSharedSid, filterFilePath)
            self._remoteCopy.copy('/etc/sysctl.conf', filterFilePath)
            self._remoteCopy.copy('/etc/pam.d/sapstartsrv', filterFilePath)
            self._remoteCopy.copy('/etc/rc.d/init.d/sapinit', filterFilePath)
            self._remoteCopy.copy('/etc/security/limits.d/99-sapsys.conf', filterFilePath)

            with open(f'.{dirs.usrSapReal}/sapservices', 'w') as fh:  # pylint: disable=invalid-name
                print(self._cmdSsh.run(f'grep {sid.upper} /usr/sap/sapservices').out, file=fh)
            with open('./etc_services_sap', 'w') as fh:  # pylint: disable=invalid-name
                print(self._cmdSsh.run("grep '^sap' /etc/services").out, file=fh)
            with open('./etc_security_limits.conf', 'w') as fh:  # pylint: disable=invalid-name
                print(self._cmdSsh.run("grep '@sapsys'   /etc/security/limits.conf").out, file=fh)
                print(self._cmdSsh.run("grep '@dba'      /etc/security/limits.conf").out, file=fh)
                print(self._cmdSsh.run(f"grep '{sid}adm' /etc/security/limits.conf").out, file=fh)

            self._copyPackage(dirs, filterFilePath, 'compat-sap-c++-9')
            self._cmdShell.run(f'cp -af {dirs.repoRoot}/flavors/hdb/image-content/soos.service  ./')
            self._cmdShell.run(f'cp -af {dirs.repoRoot}/flavors/hdb/image-content/soos-start.sh ./')
            self._cmdShell.run(f'cp -af {dirs.repoRoot}/flavors/hdb/image-content/soos-stop.sh  ./')

        self._genHdblcmConfigfile(sid, dirs, sidadm, sapsysGid, host)

    def _genHdblcmConfigfile(self, sid, dirs, sidadm, sapsysGid, host):
        # Generate hdblcm configfile from template
        # pylint: disable=too-many-arguments
        logging.info("##### Generating hdblcm configfile #####")
        instNo = self._cmdSsh.run(f'grep -E "SAPSYSTEM += +" '
                                  f'/hana/shared/{sid.upper}/profile/{sid.upper}*'
                                  ).out.split(' ')[2]
        params = {
            'SAPSYS_GID':   sapsysGid,
            'SRC_HOST':     host,
            'SID':          sid.upper,
            'INST_NO':      instNo,
            'SIDADM_HOME':  sidadm.home,
            'SIDADM_SHELL': sidadm.shell,
            'SIDADM_UID':   sidadm.uid
        }

        with pushd(dirs.build):
            genFileFromTemplate(f'{dirs.repoRoot}/flavors/hdb/image-content/hdblcm-config.template',
                                './soos-hdblcm.tmp', params)

    def _getContainerfileParams(self, sid, dirs):
        # Non-common containerfile template parameters for flavor 'hdb'
        return {
            'HANA_SHARED_SID': dirs.hanaSharedSid,
            'VAR_LIB_HDB_SID': f'/var/lib/hdb/{sid.upper}'
        }

    def _copyPackage(self, dirs, filterFilePath, package):
        if self._cmdSsh.run(f'rpm -qi {package}'):
            # create temp dir on hdb host
            self._cmdSsh.run(f'mkdir -p /tmp/containerize')
            # download package
            self._cmdSsh.run(f'dnf download --downloaddir=/tmp/containerize -y {package}')
            # copy package to local build dir
            with pushd(dirs.build):
                self._remoteCopy.copy(f'/tmp/containerize/*', filterFilePath)
