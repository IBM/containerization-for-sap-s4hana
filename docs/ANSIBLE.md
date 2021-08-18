<!--
  ------------------------------------------------------------------------
  Copyright 2020, 2021 IBM Corp. All Rights Reserved.

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

# Building Images and Starting Deployments with Red Hat® Ansible®

In the following we describe how to build the images and deploy
containers based on the images for running an SAP® system in a Red
Hat® OpenShift® Container Platform using the Red Hat Ansible CLI.

<!-- TOC-START -->

## Contents

<details>
  <summary>Table of Contents</summary>

- [Getting Started with Red Hat Ansible](#getting-started-with-red-hat-ansible)
- [Performing Manual Tasks before Running the Playbook](#performing-manual-tasks-before-running-the-playbook)
- [Setting up the Inventory for the Playbook](#setting-up-the-inventory-for-the-playbook)
- [Specifying your Settings](#specifying-your-settings)
- [Running the Playbook](#running-the-playbook)
- [Verifying the Deployment of the SAP System in the Cluster](#verifying-the-deployment-of-the-sap-system-in-the-cluster)
- [Connecting to the SAP System](#connecting-to-the-sap-system)
- [Recovering from Errors](#recovering-from-errors)

</details>

<!-- TOC-END -->

## Getting Started with Red Hat Ansible

To get started you need to set up your work environment and install
the Red Hat Ansible CLI. For detailed information on how to install
the Red Hat Ansible CLI refer to the [Red Hat Ansible installation
documentation](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html).

Start by cloning this GitHub repository to your build LPAR:

```shell
  $ git clone https://github.com/IBM/containerization-for-sap-s4hana.git
```

Directory `ansible/` of your repository clone contains the following components for building images:

``` shell
  $ tree -L 1 ansible
  ansible
  ├── ...
  ├── ocp-deployment-ansible-tower.yml
  ├── ocp-deployment.yml
  ├── roles
  │   ├── build-images
  │   ├── copy-hdb-nfs
  │   ├── create-overlay-share
  │   ├── deploy-images
  │   ├── ocp-prerequisites
  │   ├── os-prerequisites
  │   └── push-images
  ├── tasks
  │   └── ...
  └── vars
      └── ocp-extra-vars.yml
```

The `roles/` directory contains Ansible roles that are reusable and
are included in the playbook `ocp-deployment.yml`. The following roles
are used to build images of your reference SAP HANA and SAP S/4HANA
system:

  + __os-prerequisites__ installs packages like *podman*,
    *git*, *python3*, *python3-devel*. This role also
    verifies if the *oc* tool is installed and checks the connection
    to the NFS server and OCP cluster. It generates the configuration file
    `config.yaml` and credentials file `creds.yaml` as well as secret for distributed SAP HANA and SAP S/4HANA systems.

  + __ocp-prerequisites__ creates a new project on the Red
    Hat OpenShift Container Platform, sets up permissions and generates the
    service-account. The role verifies that all configuration settings in `config.yaml` and `creds.yaml` are set up correctly. 

  + __copy-hdb-nfs__ creates a snapshot copy of your SAP HANA
    `data/` and `log/` directories on the NFS server.

  + __build-images__ runs the process for building the
    *Init*, *SAP AppServer* and *SAP HANA* images.

The following roles are used to deploy the built images into the Red
Hat OpenShift Container Platform:

  + __push-images__ executes a task to push all images
    (`soos-init`, `soos-<nws4-sid>`, `soos-<hdb-sid>`) from the local
    registry to your Red Hat OpenShift Container Platform. Here, `<nws4-sid>` is
    the SAP system ID of your reference SAP NetWeaver or SAP S/4HANA
    system and `<hdb-sid>` is the SAP system ID of your reference
    database system.

  + __create-overlay-share__ creates an SAP HANA overlay
    share on the NFS server.

  + __deploy-images__ generates a deployment description file
    which describes the container setup and environment in the Red Hat
    OpenShift Container Platform and starts the deployment on the cluster.

## Performing Manual Tasks before Running the Playbook

The following tasks are not automated and need to be performed
manually (find more details in document
[*Prerequisites*](PREREQUISITES.md)):

  + Ensure that your file system on the build LPAR has at least 500
    GB capacity.

  + Create symbolic links to the directories under which the container
    images are  built.

  + Ensure that the `/etc/hosts` file is existing on your build LPAR.

  + See the section [*Distributing the SSH Keys*](./PREREQUISITES.md#distributing-the-ssh-keys) that describes how to configure SSH connections between different hosts.
 
## Setting up the Inventory for the Playbook

Before running the `ocp-deployment.yml` playbook, you need to set up
your inventory file on your build LPAR:

- Create a new file `ansible/hosts` in the `ansible/` directory of
  your repository clone and add the name of your build LPAR to the
  file.

- Create a new directory `ansible/host_vars/` in the `ansible/`
  directory

- Create a file `ansible/host_vars/<build-LPAR-name>.yml` where
  `<build-LPAR-name>` is the name of your build LPAR as specified
  in the `ansible/hosts` file.

- Add your remote user name and SSH key to
  `ansible/host_vars/<build-LPAR-name>.yml`:

  ```
  ---
  ansible_user: <username>
  ansible_ssh_private_key_file: ~/.ssh/<your_rsa_key>
  ```
  
- Check connectivity to the target host by running: 
  
  ```
   $ ansible -i hosts -m ping <build-LPAR-name>
  ```
  
  If connection to the build LPAR fails with message: `"fatal: [<build-LPAR-name>]: UNREACHABLE! ..."`
then add as mentioned previously `<your_rsa_key>` public-key to the `authorized_keys` of the target host. Finally, try again to ping the build LPAR.   

## Specifying your Settings

The file `vars/ocp-extra-vars.yml` in the `vars/` directory contains
all required variables that are used in the playbooks. Some variables
may contain sensitive information like IP addresses, passwords,
usernames. As an option you can use the Ansible Vault utility to
encrypt this sensitive content. See the [Red Hat Ansible
documentation](https://docs.ansible.com/ansible/latest/user_guide/vault.html)
for a details on how to set up Ansible Vault.

The file `vars/ocp-extra-vars.yml` looks as follows - replace all
placeholders of type `<parameter>` with your own settings:

<details>
  <summary>Content of vars/ocp-extra-vars.yml</summary>

```
---
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

######################
# build LPAR parameter
######################

# Path to the directory of the clone of this repository on the build LPAR,required
path_to_ocp_tool: <github_clone_dir>

# Directory under which the build contexts for image build are assembled
tmp_root: /data/tmp

# installs packages with ansible package module and state present
package_state: present

# install python3 or higher version
python3x_version: python3

# generate config file for automatic tools script execution with template config.j2.template
template_config_file: config.j2.template

# generate credentials file for automatic tools script execution with template creds.j2.template
template_creds_file: creds.j2.template

# Absolute path to the private SSH ID file which is used for SSH connect operations 
# from the build machine to remote systems, optional
# If the value is '' then the configured user ssh settings from ~/.ssh/ are used  
build_user_sshid: ''

#############################
# OpenShift cluster parameter
#############################

# Domain name of the Red Hat OpenShift Container Platform (OCP) cluster - used for "oc" operations
# The build LPAR must be able to connect to api.<ocp_cluster_domain>, required
ocp_cluster_domain: <ocp4_cluster_domain_name>

# Password of the kubeadmin user in OCP cluster,required
ocp_admin_password: <kubeadmin_password>

# User in OCP cluster which is used for "oc" operations, required
ocp_user_name: <ocp4_userid>

# Password of ocp_user in OCP cluster, required
ocp_user_password: <ocp4_user_password>

# Name of the OCP project which will be created for the SAP workload (e.g. my-sap-project), required
ocp_project_name: <ocp4_project_name_for_SAP>

# Name of the host as seen in the intranet (*not* in the cluster network), required
ocp_helper_node: <ocp4_helper_node_name>

# User on the OCP helper host which is used for accessing the helper host via SSH (needs root permissions)
ocp_helper_node_user_name: <ocp4_helper_node_user_name>

# User password to connect to the host of OCP helper node, optional; 
# Specify '' if password-less access is configured
ocp_helper_node_user_password: <ocp4_helper_node_user_password>

# Absolute path to the private SSH ID file which is used for SSH connect operations 
# from the OCP helper node to the OCP worker nodes, optional
# If the value is '' then the configured user ssh settings from ~/.ssh/ are used 
ocp_helper_node_user_sshid: ''

###########################################
# SAP NetWeaver or SAP S/4HANA parameter
###########################################

# Host on which the original SAP NetWeaver or SAP S/4HANA system is installed, required
# The SAP instance profile must also have this hostname in its name
nws4_host_name: <reference_system_hostname>

# ASCS and Dialog instance, SAP system ID, required, upper case
nws4_sid: <AppServer_SID>

# SAP system ID of the original SAP NetWeaver or SAP S/4HANA system (lower case)
# Use lower case "sid" to generate deployment file name
# Please provide instance number for ASCS and DI
nws4_sid_lower_case: <AppServer_sid_lower_case>

# ASCS and Dialog instance <sid>adm user, required
nws4_sidadm_name: <AppServer_sidadm_name>

# ASCS and Dialog <sid>adm user password, optional
# Specify '' if password-less access is configured
nws4_sidadm_password: <AppServer_sidadm_password>

# SAP HANA database user which is used by the application server instance to connect to the database,
# required if the reference system database is remote to the application server, otherwise
# specify '' if the reference system is a standard system
nws4_hdbconnect_name: SAPHANADB

# SAP HANA database user password which is used by the application server instance to connect to the database,
# required if the reference system database is remote to the application server, otherwise
# specify '' if the reference system is a standard system
nws4_hdbconnect_password: <HDB_connect_password>

# SAP system ID of the original SAP HANA system (lower case)
# Use lower case "sid" to generate deployment file name, required 
hdb_sid_deployment: <HDB_sid_name_lower_case>

# SAP HANA database <sid>adm user name, required
hdb_sidadm_name: <HDB_sidadm_user_name>

# SAP HANA <sid>adm user password, optional
# Specify '' if password-less access is configured
hdb_sidadm_password: <HDB_sidadm_password>

# Requested memory for Dialog instance, optional; 
# Will be derived from the original instance if '' is specified
containers_di_requests_memory: ''

# Memory limit; must be >= requested memory, optional; 
# Will be derived from the original instance if '' is specified
containers_di_limits_memory: ''

# Requested memory for ASCS instance, required 
containers_ascs_requests_memory: 10Gi

# Memory limit; must be >= requested memory, required
containers_ascs_limits_memory: 10Gi

# set flag 'yes' for distributed SAP HANA and SAP S/4HANA, required
distributed_sap_system: 'no'

# Name of the OCP secret in which credentials of the SAP HANA database user (see creds.yaml) are stored for use within the Pod;
# required if the reference system database is remote to the application server, otherwise
# specify '' if the reference system is a standard system
containers_di_secret: <secret_name_for_HDB_credentials>

# Requested memory; will be derived from the original database size if '' is supplied, optional
containers_hdb_requests_memory: ''

# Memory limit; must be >= requested memory; will be derived from the original database size if '' is supplied, optional
containers_hdb_limits_memory: ''

###############
# NFS parameter
###############

# Host on which the NFS server is running, if '' is specified ocp.helper.host.name is used
nfs_host_name: ''

# User on nfs.host which is used for ssh and rsync operations (needs root permissions)
# Password-less access for this user from build LPAR to NFS server must be configured, required 
nfs_user_name: root

# NFS user password, optional; 
# Specify '' if password-less access is configured
nfs_user_password: <NFS_user_password>

# Absolute path to the private SSH ID file which is used for SSH connect operations 
# from the NFS server to the SAP HANA database instance system, optional
# If the value is '' then the configured user ssh settings from ~/.ssh/ are used 
nfs_user_sshid: ''

# Path on nfs_host where directories {data,log} of the original HANA system are copied to, required 
nfs_path_to_hdb_copy: <NFS_server_export_dir_for_hdb>

# Path on nfs_host under which overlay file systems for container instances are created, required
nfs_path_to_overlay: <NFS_server_export_dir_for_overlay>

##################
# GitHub parameter
##################

# GitHub repository URL for project containerization-for-sap-s4hana
github_repo_url: https://github.com/IBM/containerization-for-sap-s4hana.git
```

</details>

## Running the Playbook

To run the playbook execute

```shell
     $ cd ansible
     $ ansible-playbook -i hosts -e @vars/ocp-extra-vars.yml ocp-deployment.yml
```

The playbook

- installs all prerequisites,

- creates three container images `soos-init`, `soos-<nws4-sid>`,
  `soos-<hdb-sid>` which are stored in the local podman registry on
  your build LPAR and

- uses the roles `push-images`, `create-overlay-share`,
  `deploy-images` to push the container images into the cluster and
  start the deployment of the SAP system.

If the playbook run completed without errors, all three images were
successfully built and pushed into the local registry of your Red Hat
OpenShift Container Platform and the deployment of the SAP system was
started on the cluster.

## Verifying the Deployment of the SAP System in the Cluster

Access to the SAP system from outside the cluster is enabled by a
cluster service of type NodePort. Verify whether the service was
correctly started by running

     $ oc get service/soos-<nws4-sid>-np

     NAME                 TYPE       CLUSTER-IP       EXTERNAL-IP   PORT(S)                              AGE
     soos-<nws4-sid>-np   NodePort   172.30.187.181   <none>        32<nws4-di-instno>:<node-port>/TCP   9m9s

To verify that SAP HANA and SAP S/4HANA are running in the cluster use
this command:

```shell
    $ oc describe pod soos-<nws4-sid>
```

For more information on verifying the successful deployment of the SAP
system in the cluster see section [*Verifying the
Deployment*](VERIFYING-MANAGING.md#verifying-the-deployment). However,
if your current working directory is `ansible` where the
`ocp-deployment.yml` playbook runs, activate the virtual environment
before verifying the deployment and use option `-q creds.yaml`. To do
this, use the following command, where `<path_to_ocp_tool>` is the
absolute system path of the containerization tool:

```
    $ cd <path_to_ocp_tool> && source ./venv/bin/activate && ./tools/ocp-pod-status -q ./creds.yaml
```

## Connecting to the SAP System

Section [*Managing Your
Deployment*](VERIFYING-MANAGING.md#managing-your-deployment) describes
how to connect to the SAP system. Use the following command to connect
to the SAP system, where `<path_to_ocp_tool>` is the absolute system
path of the containerization tool:

```
    $ cd <path_to_ocp_tool> && source ./venv/bin/activate && ./tools/ocp-port-forwarding -q ./creds.yaml
```

## Recovering from Errors

In case of playbook execution failure you can delete your deployment
from the cluster, using the implemented task in
`tasks/stop-deployment.yml`. Include this task with `import_tasks` in
a new playbook and run it.

To remove one or more of the previously created images from the local
podman repository on your build LPAR, list the images by running

``` shell
$ podman images

```

copy the image ID and remove the image by issuing:

``` shell
$ podman rmi -f <image-id>
```
