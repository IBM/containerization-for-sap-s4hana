<!--
  ------------------------------------------------------------------------
  Copyright 2021 IBM Corp. All Rights Reserved.

  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
 -------------------------------------------------------------------------->

# Building Images and Starting Deployments from the Command Line

In the following we describe how to build the images and deploy
containers based on the images for running an SAP® system in a Red
Hat® OpenShift® Container Platform using the command line tools.

<!-- TOC-START -->

## Contents

<details>
  <summary>Table of Contents</summary>

- [Build LPARs](#build-lpars)
- [General Command Line Parameters](#general-command-line-parameters)
- [Building and Deploying Automatically](#building-and-deploying-automatically)
- [Building Manually](#building-manually)
  - [Creating a Snapshot Copy of the Reference Database](#creating-a-snapshot-copy-of-the-reference-database)
  - [Building the Container Images at Once](#building-the-container-images-at-once)
  - [Building the Container Images Separately](#building-the-container-images-separately)
- [Pushing the Images Manually](#pushing-the-images-manually)
- [Starting the Deployment Manually](#starting-the-deployment-manually)
  - [Creating a Database Overlay Share on the NFS Server](#creating-a-database-overlay-share-on-the-nfs-server)
  - [Generating a Deployment Description File](#generating-a-deployment-description-file)
  - [Starting the SAP system on Red Hat OpenShift Container Platform](#starting-the-sap-system-on-red-hat-openshift-container-platform)
- [Further steps](#further-steps)

</details>

<!-- TOC-END -->

## Build LPARs

We performed our tests both on the cluster helper node and on a
separate build LPAR. If you run the build on the cluster helper node,
you do not need to setup the connection to the cluster (i.e. you do
not have to perform the steps described in [Name Resolution for
OpenShift Container Platform
Services](PREREQUISITES.md#name-resolution-for-red-hat-openshift-container-platform-services)).
          

## General Command Line Parameters

The following optional command line parameters are available for all
tools in the `tools/` directory of your repository clone:

- The credentials  file to use (default: `./creds.yaml.gpg`):

  ```shell
  -q / --creds-file <credentials file>
  ```

- The configuration file to use (default: `./config.yaml`):

  ```shell
  -c / --config-file <configuration file>
  ```

- Write logging information to the user's terminal, not into logging
  files:

  ```shell
  -w / --log-to-terminal
  ```

- Write logging information to the specified directory:

  ```shell
  -g / --logfile-dir <logfile directory>
  ```

  The directory will be created if it does not exist. If `-g` is not
  specified, directory `./log/` is used to store logging
  information. If `-w` is specified, parameter `-g` is ignored.

- Specify the logging level:

   ```shell
   -v / --loglevel <logging level>
   ```

   where `<logging level>` is one of `critical`, `error` `warning`,
   `info`, `debug` or `notset`.

 - Dump the context in which the tool will execute:

   ```shell
   --dump-context
   ```

## Building and Deploying Automatically

> :warning: **Before invoking the tools, do not forget to [activate
> the virtual Python
> environment](./PREREQUISITES.md#activating-the-virtual-environment).**
                
> :warning: **You have to stop the reference database before starting
> the automated build!**

- Run

  ```shell
  $ tools/containerize -a
  ```

  from the root directory of your repository clone.

  The above command performs all necessary steps to get a running copy
  of your reference SAP system in your cluster. The whole process
  takes some time (about 30 minutes in our build setup).


## Building Manually

Manual build involves creating a snapshot copy of the `data/` and `log/`
directories of the reference database and building the three container
images. The three images can be built at once or individually.

### Creating a Snapshot Copy of the Reference Database

> :warning: **You have to stop the reference database before creating
> the snapshot!**

- Run

  ```shell
  $ tools/containerize -y
  ```

  or

  ```shell
  $ tools/nfs-hdb-copy
  ```

  to create a snapshot copy of the `data/` and `log/` directories of
  your database on the NFS server. Dependent on the size of the
  database this may take some time.

- The copy is performed via an SSH connection between the NFS server
  and the host on which the `data/` and `log/` directories of your
  reference database reside. Therefore the user which is specified as
  `nfs.user` in the `config.yaml` file must have an SSH key-pair
  installed which meets the following conditions:

  - the private key must not be protected by a passphrase
    (passphrase-less private key)

  - the public key must be installed in the `authorized_keys` file of
    the user which is specified as `flavor.hdb.user` in the
    `config.yaml` file.

### Building the Container Images at Once

- Run

  ```shell
  $ tools/containerize -b
  ```

  to build the three images

  ```shell
  localhost/soos-init:latest
  localhost/soos-<nws4-sid>:latest
  localhost/soos-<hdb-sid>:latest
  ```

  at once where

  - `<nws4-sid>` is the SAP system ID of your reference SAP NetWeaver®
    or SAP S/4HANA® system and

  - `<hdb-sid>` is the SAP system ID of your reference database
    system.

- Verify whether the images were correctly built by running

  ```shell
  $ podman images soos
  REPOSITORY                   TAG      IMAGE ID       CREATED          SIZE
  localhost/soos-<hdb-sid>     latest   c1e71ab460f2   28 seconds ago   10 GB
  localhost/soos-<nws4-sid>    latest   d09fdddabbbe   11 minutes ago   5.3 GB
  localhost/soos-init          latest   746eb831dc01   18 minutes ago   439 MB
  ```

### Building the Container Images Separately

- Run

  ```shell
  $ tools/image-build -f init
  ```

  from the root directory of your repository clone to build the image

  ```shell
  localhost/soos-init:latest
  ```

  Verify whether the image was correctly built by running

  ```shell
  $ podman images soos-init
  REPOSITORY            TAG      IMAGE ID       CREATED          SIZE
  localhost/soos-init   latest   746eb831dc01   18 minutes ago   439 MB
  ```

- Run

  ```shell
  $ tools/image-build -f nws4
  ```

  from the root directory of your repository clone to build the image

  ```shell
  localhost/soos-<nws4-sid>:latest
  ```

  where `<nws4-sid>` is the SAP system ID of your reference SAP NetWeaver or SAP S/4HANA system.

  Verify whether the image was correctly built by running

  ```shell
  $ podman images soos-<nws4-sid>
  REPOSITORY                  TAG      IMAGE ID       CREATED          SIZE
  localhost/soos-<nws4-sid>   latest   d09fdddabbbe   16 minutes ago   5.3 GB
  ```

- Run

  ```shell
  $ tools/image-build -f hdb
  ```

  from the root directory of your repository clone to build the image

  ```shell
  localhost/soos-<hdb-sid>:latest
  ```

  where `<hdb-sid>` is the SAP system ID of your reference database
  system.

  Verify whether the image was correctly built by running

  ```shell
  $ podman images soos-<hdb-sid>
  REPOSITORY                 TAG      IMAGE ID       CREATED         SIZE
  localhost/soos-<hdb-sid>   latest   c1e71ab460f2   5 minutes ago   10 GB
  ```

## Pushing the Images Manually

After image build, the three images are stored in the local *podman*
registry of your build LPAR. In order to make them usable in your
cluster you have to push them to the local cluster registry.

- Run

  ```shell
  $ tools/containerize -p
  ```

  to push the three images to the local cluster registry at once.

  Alternatively you can push the three images individually to the
  local cluster registry by running the three commands

  ```shell
  $ tools/image-push -f init
  $ tools/image-push -f hdb
  $ tools/image-push -f nws4
  ```

  Each push takes some time. In particular, pushing the
  `soos-<hdb-sid>` and the `soos-<nws4-sid>` images may take a few
  minutes each.

- Verify whether the images are available in the local cluster
  registry:

  ```shell
  $ oc get imagestream
  NAME               IMAGE REPOSITORY                                                                                        TAGS      UPDATED
  soos-init          default-route-openshift-image-registry.apps.<ocp-cluster-domain>/<ocp-project-name>/soos-init           latest    7 minutes ago
  soos-<nws4-sid>    default-route-openshift-image-registry.apps.<ocp-cluster-domain>/<ocp-project-name>/soos-<nws4-sid>     latest    7 minutes ago
  soos-<hdb-sid>     default-route-openshift-image-registry.apps.<ocp-cluster-domain>/<ocp-project-name>/soos-<hdb-sid>      latest    5 minutes ago
  ```

## Starting the Deployment Manually

Starting the SAP system on Red Hat OpenShift Container Platform involves
three steps:

- Creating a database overlay share on the NFS server which will be
  used by the SAP HANA container.

- Generating a deployment description file which describes the
  container setup and environment on your cluster.

- Starting the SAP system on the cluster.

### Creating a Database Overlay Share on the NFS Server

- Create a database overlay share on the NFS server by running

  ```shell
  $ tools/containerize -o
  ```

  or

  ```shell
  $ tools/nfs-overlay-setup
  ```

  The commands emit the unique ID

  ```shell
  <uuid>-<ocp-user-name>-<ocp-project-name>-<hdb-host>-<hdb-sid>
  ```

  of the freshly created overlay share. This unique ID is used when
  generating a deployment description file (see section [*Generating a
  Deployment Description
  File*](#generating-a-deployment-description-file)).

- You can list all existing NFS overlay shares including their date
  and time of creation by running

  ```shell
  $ tools/containerize -l
  ```

  or

  ```shell
  $ tools/nfs-overlay-list
  ```

  This returns a list of existing NFS overlay shares in the format

  ```shell
  ⋮
  <uuid>-<ocp-user-name>-<ocp-project-name>-<hdb-host>-<hdb-sid> (<date-of-creation> <time-of-creation>)
  ⋮
  ```

- You can tear down an existing NFS overlay share by running

  ```shell
  $ tools/containerize -t -u <uuid>-<ocp-user-name>-<ocp-project-name>-<hdb-host>-<hdb-sid>
  ```

  or

  ```shell
  $ tools/nfs-overlay-teardown -u <uuid>-<ocp-user-name>-<ocp-project-name>-<hdb-host>-<hdb-sid>
  ```

  Instead of specifying the complete unique ID it is sufficient to
  specify a prefix of the unique ID which is unique to the unique IDs
  of all other NFS overlay shares.

### Generating a Deployment Description File

- Generate a deployment description file by running

  ```shell
  $ tools/containerize -d -u <uuid>-<ocp-user-name>-<ocp-project-name>-<hdb-host>-<hdb-sid>
  ```

  or

  ```shell
  $ tools/ocp-deployment-gen -u <uuid>-<ocp-user-name>-<ocp-project-name>-<hdb-host>-<hdb-sid>
  ```

  where
  `<uuid>-<ocp-user-name>-<ocp-project-name>-<hdb-host>-<hdb-sid>` is
  the unique ID of the overlay share which was created in the previous
  step. Instead of specifying the complete unique ID it is sufficient
  to specify a prefix of the unique ID which is unique to the unique
  IDs of all other NFS overlay shares.

  Running one of the above mentioned commands generates a deployment
  description file

  ```shell
  <ocp-project-name>-deployment-<nws4-sid>-<hdb-sid>.yaml
  ```

  in the root directory of your repository clone.

### Starting the SAP system on Red Hat OpenShift Container Platform


- Start the SAP system on the cluster by running

  ```shell
  $ tools/containerize -s
  ```

## Further steps

For further steps see documentation [*Verifying and Managing the
Deployment*](VERIFYING-MANAGING.md).
