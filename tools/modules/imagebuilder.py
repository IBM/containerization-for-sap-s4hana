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

""" Build container images from existing SAP Netweaver or SAP S/4HANA system """


# Global modules

from   datetime import date
import logging
import tempfile
import types


# Local modules

from modules.command    import (
    CmdShell,
    CmdSsh
)
from modules.fail       import fail
from modules.exceptions import RpmFileNotFoundException
from modules.remotecopy import RemoteCopy
from modules.tools      import (
    genFileFromTemplate,
    getRpmFileForPackage,
    pushd
)

from modules.constants  import getConstants


# Functions

def getBuilder(ctx):  # pylint: disable=inconsistent-return-statements
    """ Get image builder for specific image flavor """

    if ctx.ar.image_flavor == 'nws4':
        return BuilderNws4(ctx)
    if ctx.ar.image_flavor == 'hdb':
        return BuilderHdb(ctx)

    # This should never be reached

    fail(f"Unknown image flavor '{ctx.ar.image_flavor}'")


# Classes

class Builder():
    """ Build container images """

    # pylint: disable=too-many-instance-attributes

    def __init__(self, ctx):
        self._ctx         = ctx
        self._host        = None
        self._user        = None
        self._cmdShell    = CmdShell()
        self._cmdSsh      = None
        self._remoteCopy  = None
        self._flavor      = None
        self._description = None

    def buildImage(self, sidU, host, user):
        """ Build image """

        # pylint: disable=too-many-locals,too-many-statements

        repoRoot     = self._ctx.cf.build.repo.root
        buildTmpRoot = self._ctx.ar.temp_root
        buildDir     = self._ctx.ar.build_directory
        keepFiles    = self._ctx.ar.keep_files

        # Initialize ssh connection

        if not self._cmdSsh or host != self._host or user != self._user:
            # Initialize only if not yet initialized or if connection parameters have changed
            if self._cmdSsh:
                del self._cmdSsh
            self._cmdSsh = CmdSsh(self._ctx, host, user)

        # Initialize remote copy connection

        if not self._remoteCopy or host != self._host or user != self._user:
            # Initialize only if not yet initialized or if connection parameters have changed
            if self._remoteCopy:
                del self._remoteCopy
            self._remoteCopy = RemoteCopy(self._ctx, host, user)

        self._host = host
        self._user = user

        # System ID

        sidL = sidU.lower()

        logging.debug(f"sidU: '{sidU}'")
        logging.debug(f"sidL: '{sidL}'")

        # Directories

        dirs = types.SimpleNamespace()
        dirs.repoRoot   = repoRoot
        if buildDir and len(buildDir) != 0:
            dirs.build  = buildDir
        else:
            self._cmdShell.run(f'mkdir -p "{buildTmpRoot}"')
            dirs.build  = self._cmdShell.run(f'mktemp -d -p "{buildTmpRoot}" '
                                             f'-t soos-build-{self._flavor}.XXXXXXXXXX').out
        dirs.usrSapReal = self._getUsrSapReal()
        dirs.sapmnt     = self._getSapmntDir(sidU)

        self._setDirsFlavor(sidU, dirs)

        logging.debug(f"dirs: '{dirs}'")

        # Image properties

        image = types.SimpleNamespace()
        image.name        = f'localhost/soos-{sidL}'
        image.version     = 'latest'
        image.tag         = f'{image.name}:{image.version}'
        image.date        = date.today().strftime('%Y-%m-%d')
        image.description = self._description  # Must be set by derived class
        with pushd(dirs.repoRoot):
            image.commit  = self._cmdShell.run('git log --pretty="%H" -1').out
            image.branch  = self._cmdShell.run('git rev-parse --abbrev-ref HEAD').out

        logging.debug(f"image: '{image}'")

        # OS user properties

        (sapadm, sidadm, sapsysGid) = self._getOsUserProperties(sidL)

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
            self._genBuildContext(sidU, dirs, sapadm, sidadm, sapsysGid, host, remoteOs)
            containerfile = self._genContainerfile(sidU, dirs, image, sapadm, sidadm, sapsysGid)
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

    def _getSapmntDir(self, sidU):
        # Get path of SAP Mount Directory (nws4) or path to 'shared' directory (hdb)
        # XXX ASSUMES THAT ".../<SID>/SYS/profile" IS A SYMBOLIC LINK
        #     WHOSE TARGET PATH STARTS WITH THE WANTED DIRECTORY
        #     DOES THIS ALWAYS WORK?

        profilePath   = self._cmdSsh.run(f'find /usr/sap/ -type l -ipath '
                                         f'"*{sidU}/SYS/profile"').out
        profileTarget = self._cmdSsh.run(f'readlink "{profilePath}"').out
        sapmnt        = profileTarget[0:profileTarget.index(f'/{sidU}/profile')]

        logging.debug(f"profilePath  : '{profilePath}'")
        logging.debug(f"profileTarget: '{profileTarget}'")
        logging.debug(f"sapmnt       : '{sapmnt}'")

        return sapmnt

    def _setDirsFlavor(self, sidU, dirs):
        # Flavor specific directories
        # pylint: disable=unused-argument
        fail('This function must be overwritten by derived flavor specific builder class.')

    def _getOsUserProperties(self, sidL):
        # Get properties of sapadm and <sid>adm from remote host /etc/passwd
        #
        # XXX IN CASE THE SOURCE SYSTEM USES YP OR ANOTHER AUTHENTICATION
        #     SETUP THIS NEEDS TO BE DONE DIFFERENTLY!!!

        sapadm = types.SimpleNamespace()
        (_d1,
         _d2,
         sapadm.uid,
         sapsysGid,
         sapadm.comment,
         sapadm.home,
         sapadm.shell
         ) = self._cmdSsh.run('grep "^sapadm:" /etc/passwd').out.split(':')

        sidadm = types.SimpleNamespace()
        (_d1,
         _d2,
         sidadm.uid,
         _d4,
         sidadm.comment,
         sidadm.home,
         sidadm.shell
         ) = self._cmdSsh.run(f'grep "^{sidL}adm:" /etc/passwd').out.split(':')

        logging.debug(f'Returning {sapadm}, {sidadm}, {sapsysGid}')

        return (sapadm, sidadm, sapsysGid)

    def _cleanupAtStart(self, dirs, keepFiles):
        # Remove previously copied files if not explicitly asked to keep them
        if not keepFiles:
            logging.info(f"##### Cleaning up build directoy '{dirs.build}' #####")
            with pushd(dirs.build):
                self._cmdShell.run('rm -rf ..?* .[!.]* *')

    def _genBuildContext(self, sidU, dirs, sapadm, sidadm, sapsysGid, host, remoteOs):
        # Generate podman build context
        # pylint: disable=too-many-arguments
        filterFilePath = f'{dirs.tmp}/rsync-filter'
        logging.debug(f"filterFilePath: {filterFilePath}")
        with open(filterFilePath, 'w') as fh:  # pylint: disable=invalid-name
            print(self._getRsyncFilter(sidU, dirs, remoteOs), file=fh)
        self._genBuildContextFlavor(sidU, dirs, sapadm, sidadm, sapsysGid, host, filterFilePath)

    def _getRsyncFilter(self, sidU, dirs, remoteOs):
        # Get filter for selective copy depending on flavor
        # pylint: disable=unused-argument
        fail('This function must be overwritten by derived flavor specific builder class.')

    def _genBuildContextFlavor(self, sidU, dirs, sapadm, sidadm, sapsysGid, host, filterFilePath):
        # Flavor dependent actions for build context generation
        # pylint: disable=unused-argument,too-many-arguments
        fail('This function must be overwritten by derived flavor specific builder class.')

    def _genContainerfile(self, sidU, dirs, image, sapadm, sidadm, sapsysGid):
        # Generate containerfile from template depending on flavor
        # MUST RUN AFTER BUILD CONTEXT SETUP
        # pylint: disable=too-many-arguments
        logging.info("##### Generating Containerfile #####")

        sidL = sidU.lower()

        # Common parameters
        if dirs.usrSapReal != '/usr/sap':
            usrSapLinkCmd = f'ln -s {dirs.usrSapReal} /usr/sap'
        else:
            usrSapLinkCmd = 'true'

        # get optional packages
        packages = getattr(self._ctx.cf.images, self._flavor).packages
        pkgParams = self._getOptionalPackageParams(packages, dirs)

        params = {
            'IMAGE_BRANCH':              image.branch,
            'IMAGE_COMMIT':              image.commit,
            'IMAGE_DATE':                image.date,
            'IMAGE_DESCRIPTION':         image.description,
            'IMAGE_VERSION':             image.version,
            'SAPADM_COMMENT':            sapadm.comment,
            'SAPADM_HOME':               sapadm.home,
            'SAPADM_SHELL':              sapadm.shell,
            'SAPADM_UID':                sapadm.uid,
            'SAPMNT':                    dirs.sapmnt,
            'SAPSYS_GID':                sapsysGid,
            'sid':                       sidL,
            'SID':                       sidU,
            'SIDADM_COMMENT':            sidadm.comment,
            'SIDADM_HOME':               sidadm.home,
            'SIDADM_SHELL':              sidadm.shell,
            'SIDADM_UID':                sidadm.uid,
            'USR_SAP_REAL':              dirs.usrSapReal,
            'USR_SAP_LINK_CMD':          usrSapLinkCmd,
            'INSTALL_OPT_PACKAGES':      pkgParams.installOptPackagesDnf,
            'COPY_OPT_PACKAGE_FILES':    pkgParams.copyOptPackageFiles,
            'INSTALL_OPT_PACKAGE_FILES': pkgParams.installOptPackageFiles
        }

        params.update(self._getContainerfileParams(sidU, dirs))
        containerfile = f'{dirs.tmp}/containerfile'
        template      = f'{dirs.repoRoot}/openshift/images/{self._flavor}/containerfile.template'
        genFileFromTemplate(template, containerfile, params)
        with open(containerfile) as fh:  # pylint: disable=invalid-name
            logging.debug(f"Contents of '{containerfile}': >>>\n{fh.read()}<<<")
        return containerfile

    def _getContainerfileParams(self, sidU, dirs):
        # Non-common containerfile template parameters depending on flavor
        # pylint: disable=unused-argument
        fail('This function must be overwritten by derived flavor specific builder class.')

    def _buildImage(self, buildCmd, dirs, image, containerfile):
        # Build image
        # MUST RUN AFTER BUILD CONTEXT SETUP
        # pylint: disable=no-self-use
        logging.info("##### Building image #####")
        with pushd(dirs.build):
            self._cmdShell.run(f'{buildCmd} build -t {image.tag} -f "{containerfile}" .')

    def _getOptionalPackageParams(self, packages, dirs):
        # Check if optional packages must be installed
        # and set them
        pkgParams = types.SimpleNamespace()
        pkgParams.installOptPackagesDnf  = ''
        pkgParams.copyOptPackageFiles    = ''
        pkgParams.installOptPackageFiles = ''

        if len(packages) > 0:
            self._addDependencies(packages, pkgParams)
            self._addDnfInstallablePackages(packages, pkgParams)
            self._addRpmPackages(packages, pkgParams, dirs)
        return pkgParams

    def _addDependencies(self, packages, pkgParams):
        # Set dependencies for optional packages
        firstRun = pkgParams.installOptPackagesDnf == ""

        for package in packages:
            if len(package.dependencies) > 0:
                if firstRun:
                    pkgParams.installOptPackagesDnf = 'RUN  dnf -y install'
                    firstRun = False
                else:
                    pkgParams.installOptPackagesDnf += ' && \\' + '\n'
                    pkgParams.installOptPackagesDnf += '     dnf -y install'

                for dependency in package.dependencies:
                    logging.debug(f"Adding dependency '{dependency}' " +
                                  f"for package '{package.packageName}'")
                    pkgParams.installOptPackagesDnf += f' {dependency}'

    def _addDnfInstallablePackages(self, packages, pkgParams):
        # set all packages to be installed using dnf
        firstRun = pkgParams.installOptPackagesDnf == ""
        for package in packages:
            if package.dnfInstallable:
                logging.debug(f'package {package.packageName} installable via dnf install')

                if firstRun:
                    pkgParams.installOptPackagesDnf = 'RUN  dnf -y install'
                    firstRun = False
                else:
                    pkgParams.installOptPackagesDnf += ' && \\' + '\n'
                    pkgParams.installOptPackagesDnf += '     dnf -y install'
                if package.repository != "":
                    pkgParams.installOptPackagesDnf += f' --enablerepo={package.repository}'
                    logging.debug(f'enabling repository    : {package.repository}')
                pkgParams.installOptPackagesDnf += f' {package.packageName}'

    def _addRpmPackages(self, packages, pkgParams, dirs):
        # set all packages which must be copied and installed using rpm
        firstRun = pkgParams.copyOptPackageFiles == ""
        for package in packages:
            if not package.dnfInstallable:
                logging.debug(f'package {package.packageName} must be installed via rpm')
                if firstRun:
                    pkgParams.copyOptPackageFiles    = 'COPY '
                    pkgParams.installOptPackageFiles = 'RUN  '
                    firstRun = False
                else:
                    pkgParams.copyOptPackageFiles    += ' && \\' + '\n' + '     '
                    pkgParams.installOptPackageFiles += ' && \\' + '\n' + '     '

                try:
                    rpmFileName = getRpmFileForPackage(package.packageName, dirs.defaultPackagesDir)
                    pkgParams.copyOptPackageFiles    += f'{dirs.defaultPackagesDir}'
                    pkgParams.copyOptPackageFiles    += f'/{rpmFileName} / '
                    pkgParams.installOptPackageFiles += f'rpm -i /{rpmFileName} && \\' + '\n'
                    pkgParams.installOptPackageFiles += f'     rm /{rpmFileName}'
                except RpmFileNotFoundException as exp:
                    fail(exp.errorText)

    def _cleanupAtEnd(self, dirs):
        # Cleanup after image build
        with pushd(dirs.repoRoot):
            # self._cmdShell.run(f'\\rm -rf {dirs.build}')
            pass


# -------------------------------------------------------------------------

class BuilderNws4(Builder):
    """ Build container images of flavor 'nws4' """

    def __init__(self, ctx):
        super().__init__(ctx)
        self._flavor = 'nws4'
        self._description = 'Container for SAP S/4HANA'

    def _setDirsFlavor(self, sidU, dirs):
        # Flavor specific directories of flavor 'nws4'
        pass  # currently none

    def _getRsyncFilter(self, sidU, dirs, remoteOs):
        rsFilter = ''
        rsFilter += f"include {dirs.usrSapReal}/trans\n"
        rsFilter += f"include {dirs.usrSapReal}/{sidU}\n"
        rsFilter +=  "exclude **.zip\n"
        rsFilter +=  "exclude **.old\n"
        rsFilter +=  "exclude **.log\n"
        rsFilter +=  "exclude **.trc\n"
        rsFilter +=  "exclude **.tar.gz\n"
        rsFilter +=  "exclude **DEFAULT.*.PFL\n"
        rsFilter +=  "exclude **log_backup**\n"
        # rsFilter +=  "exclude **.SAR\n"
        rsFilter += f"exclude {dirs.usrSapReal}/trans/log/*\n"
        rsFilter += f"exclude {dirs.usrSapReal}/trans/cofiles/*\n"
        rsFilter += f"exclude {dirs.usrSapReal}/trans/data/*\n"
        rsFilter += f"exclude {dirs.usrSapReal}/trans/tmp/*\n"
        rsFilter += f"exclude {dirs.usrSapReal}/trans/actlog/*\n"
        rsFilter += f"exclude {dirs.usrSapReal}/trans/EPS/*/*\n"
        rsFilter += f"exclude {dirs.usrSapReal}/{sidU}/*/work/*\n"
        rsFilter += f"include {dirs.usrSapReal}/{sidU}/exe\n"
        rsFilter += f"include {dirs.usrSapReal}/{sidU}/exe/uc\n"
        rsFilter += f"include {dirs.usrSapReal}/{sidU}/exe/uc/{remoteOs}\n"
        rsFilter += f"include {dirs.usrSapReal}/{sidU}/exe/uc/{remoteOs}/**\n"
        rsFilter += f"include {dirs.usrSapReal}/{sidU}/D[0-9][0-9]\n"
        rsFilter += f"include {dirs.usrSapReal}/{sidU}/D[0-9][0-9]/data\n"
        rsFilter += f"include {dirs.usrSapReal}/{sidU}/D[0-9][0-9]/data/icmandir\n"
        rsFilter += f"include {dirs.usrSapReal}/{sidU}/D[0-9][0-9]/data/icmandir/**\n"
        rsFilter += f"include {dirs.usrSapReal}/{sidU}/D[0-9][0-9]/data/cache\n"
        rsFilter += f"include {dirs.usrSapReal}/{sidU}/D[0-9][0-9]/data/cache/**\n"
        rsFilter += f"include {dirs.usrSapReal}/{sidU}/D[0-9][0-9]/data/cache/**\n"
        rsFilter += f"exclude {dirs.usrSapReal}/{sidU}/D[0-9][0-9]/data/**\n"
        rsFilter += f"exclude {dirs.usrSapReal}/{sidU}/D[0-9][0-9]/exe/**\n"
        rsFilter += f"exclude {dirs.usrSapReal}/{sidU}/ASCS[0-9][0-9]/exe/**\n"
        rsFilter += f"exclude {dirs.usrSapReal}/{sidU}/exe/**\n"
        rsFilter += f"include {dirs.usrSapReal}/trans/**\n"
        rsFilter += f"include {dirs.usrSapReal}/{sidU}/**\n"

        return rsFilter

    def _genBuildContextFlavor(self, sidU, dirs, sapadm, sidadm, sapsysGid, host, filterFilePath):
        # Flavor 'nws4' dependent actions for build context generation
        # pylint: disable=too-many-arguments
        logging.info('##### Copying build context to temporary build directory #####')

        sidL = sidU.lower()

        with pushd(dirs.build):
            self._remoteCopy.copy(f'/usr/sap/{sidU}', filterFilePath)  # also copies /sapmnt
            self._remoteCopy.copy('/usr/sap/trans', filterFilePath)
            # SAP host agent
            # self._remoteCopy.copy(f'/usr/sap/hostctrl', filterFilePath)
            # self._remoteCopy.copy(f'{sapadm.home}', filterFilePath)
            self._remoteCopy.copy(f'{sidadm.home}', filterFilePath)

            with open(f'.{dirs.usrSapReal}/sapservices', 'w') as fh:  # pylint: disable=invalid-name
                print(self._cmdSsh.run(f'grep {sidU} /usr/sap/sapservices').out, file=fh)
            with open('./etc_services_sap', 'w') as fh:  # pylint: disable=invalid-name
                print(self._cmdSsh.run('grep "^sap" /etc/services').out, file=fh)

            with open('./etc_security_limits.conf', 'w') as fh:  # pylint: disable=invalid-name
                print(self._cmdSsh.run('grep "@sapsys"         /etc/security/limits.conf').out,
                      file=fh)
                print(self._cmdSsh.run('grep "@dba"            /etc/security/limits.conf').out,
                      file=fh)
                print(self._cmdSsh.run(f'grep "{sidL}adm" /etc/security/limits.conf').out,
                      file=fh)

            contentBase = f'{dirs.repoRoot}/openshift/images/nws4/image-content'

            self._cmdShell.run(f'cp -af "{contentBase}/soos.service"  ./')
            self._cmdShell.run(f'cp -af "{contentBase}/soos-start.sh" ./')
            self._cmdShell.run(f'cp -af "{contentBase}/soos-stop.sh"  ./')

    def _getContainerfileParams(self, sidU, dirs):
        # Non-common containerfile template parameters for flavor 'nws4'
        return {
            # Currently none
        }


# -------------------------------------------------------------------------

class BuilderHdb(Builder):
    """ Build container images of flavor 'hdb' """

    def __init__(self, ctx):
        super().__init__(ctx)
        self._flavor      = 'hdb'
        self._description = 'Container for SAP HANA'

    def _setDirsFlavor(self, sidU, dirs):
        # Flavor specific directories of flavor 'hdb'
        targetMountdir     = dirs.sapmnt[0:dirs.sapmnt.rindex('/')]  # cut off trailing '/shared'
        dirs.hanaSharedSid = f'{targetMountdir}/shared/{sidU}'
        logging.debug(f"dirs.hanaSharedSid: '{dirs.hanaSharedSid}'")
        dirs.defaultPackagesDir = getConstants().defaultPackagesDir

    def _getRsyncFilter(self, sidU, dirs, remoteOs):
        rsFilter = ''
        rsFilter +=  'exclude **.zip\n'
        rsFilter +=  'exclude **.old\n'
        rsFilter +=  'exclude **.log\n'
        rsFilter +=  'exclude **.trc\n'
        rsFilter +=  'exclude **.tar.gz\n'
        rsFilter +=  'exclude **DEFAULT.*.PFL\n'
        rsFilter +=  'exclude **log_backup**\n'
        rsFilter += f'include {dirs.hanaSharedSid}/**\n'
        rsFilter +=  'include /tmp/containerize/**\n'

        return rsFilter

    def _genBuildContextFlavor(self, sidU, dirs, sapadm, sidadm, sapsysGid, host, filterFilePath):
        # Flavor 'hdb' dependent actions for build context generation
        # pylint: disable=too-many-arguments

        logging.info('##### Copying build context to temporary build directory #####')

        sidL = sidU.lower()

        # copy default packages dir to build dir
        self._cmdShell.run(f'mkdir -p {dirs.build}{dirs.defaultPackagesDir}')
        self._cmdShell.run(f'cp -af {dirs.defaultPackagesDir}/* '
                           f'{dirs.build}{dirs.defaultPackagesDir}')

        with pushd(dirs.build):
            self._remoteCopy.copy(dirs.hanaSharedSid, filterFilePath)
            self._remoteCopy.copy('/etc/sysctl.conf', filterFilePath)
            self._remoteCopy.copy('/etc/pam.d/sapstartsrv', filterFilePath)
            self._remoteCopy.copy('/etc/security/limits.d/99-sapsys.conf', filterFilePath)

            with open(f'.{dirs.usrSapReal}/sapservices', 'w') as fh:  # pylint: disable=invalid-name
                print(self._cmdSsh.run(f'grep {sidU} /usr/sap/sapservices').out, file=fh)
            with open('./etc_services_sap', 'w') as fh:  # pylint: disable=invalid-name
                print(self._cmdSsh.run('grep "^sap" /etc/services').out, file=fh)
            with open('./etc_security_limits.conf', 'w') as fh:  # pylint: disable=invalid-name
                print(self._cmdSsh.run('grep "@sapsys"         /etc/security/limits.conf').out,
                      file=fh)
                print(self._cmdSsh.run('grep "@dba"            /etc/security/limits.conf').out,
                      file=fh)
                print(self._cmdSsh.run(f'grep "{sidL}adm" /etc/security/limits.conf').out,
                      file=fh)

            contentBase = f'{dirs.repoRoot}/openshift/images/hdb/image-content'

            self._cmdShell.run(f'cp -af {contentBase}/soos.service  ./')
            self._cmdShell.run(f'cp -af {contentBase}/soos-start.sh ./')
            self._cmdShell.run(f'cp -af {contentBase}/soos-stop.sh  ./')

        self._genHdblcmConfigfile(sidU, dirs, sidadm, sapsysGid, host)

    def _genHdblcmConfigfile(self, sidU, dirs, sidadm, sapsysGid, host):
        # Generate hdblcm configfile from template
        # pylint: disable=too-many-arguments
        logging.info("##### Generating hdblcm configfile #####")
        instno = self._cmdSsh.run(f'grep -E "SAPSYSTEM += +" '
                                  f'/hana/shared/{sidU}/profile/{sidU}*'
                                  ).out.split(' ')[2]
        params = {
            'SAPSYS_GID':   sapsysGid,
            'SRC_HOST':     host,
            'SID':          sidU,
            'INST_NO':      instno,
            'SIDADM_HOME':  sidadm.home,
            'SIDADM_SHELL': sidadm.shell,
            'SIDADM_UID':   sidadm.uid
        }

        with pushd(dirs.build):
            template = f'{dirs.repoRoot}/openshift/images/hdb/image-content/hdblcm-config.template'
            genFileFromTemplate(template, './soos-hdblcm.tmp', params)

    def _getContainerfileParams(self, sidU, dirs):
        # Non-common containerfile template parameters for flavor 'hdb'
        return {
            'HANA_SHARED_SID': dirs.hanaSharedSid,
            'VAR_LIB_HDB_SID': f'/var/lib/hdb/{sidU}'
        }
