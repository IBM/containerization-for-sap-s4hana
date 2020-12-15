<!--
  ------------------------------------------------------------------------
  Copyright 2020 IBM Corp. All Rights Reserved.
 
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

# Building and deploying with Red Hat® Ansible® and Red Hat® Ansible Tower®

[![License](https://img.shields.io/badge/License-Apache2-blue.svg)](https://www.apache.org/licenses/LICENSE-2.0)
<!--
[![CLA assistant](https://cla-assistant.io/readme/badge/IBM/containerization-for-sap-s4hana)](https://cla-assistant.io/IBM/containerization-for-sap-s4hana)
-->

Build container images from existing SAP NetWeaver® and SAP S/4HANA® systems and run them on a Red Hat® OpenShift® cluster on IBM Power Systems.

## Contents
 
- [Building and deploying with Red Hat Ansible](#building-and-deploying-with-red-hat-ansible)
- [Building and deploying with Red Hat Ansible Tower](#building-and-deploying-with-red-hat-ansible-tower)

Please refer also to this [IBM® Redpaper](http://www.redbooks.ibm.com/Redbooks.nsf/RedpieceAbstracts/redp5619.html?Open)
for more information on how to setup the required environment.

## Important note

This is a beta release and targets for test and other non-production landscapes. The created deliverables are not supported by SAP nor agreed to a roadmap for official support in current state (see also SAP Note 1122387 - Linux: SAP Support in virtualized environments)

## Building and deploying with Red Hat Ansible

### Getting started

To get started you need to set up your working environment and install Red Hat Ansible CLI. For detailed information on how to install Red Hat Ansible CLI refer to this "[installation guide](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html)". 
Clone the GitHub repository containerization-for-sap-s4hana on your local machine. In directory __ansible__ you will find those components for building images: 

     $ git clone https://github.com/IBM/containerization-for-sap-s4hana.git 
     
     $ tree -L 1 ansible
     ansible
     ├── ...
     ├── ocp-deployment-ansible-tower.yml
     ├── ocp-deployment.yml
     ├── README.md
     ├── roles
     │   ├── build-images
     │   ├── copy-hdb-nfs
     │   ├── create-overlay-share
     │   ├── deploy-images
     │   ├── ocp-prerequisites
     │   ├── os-prerequisites
     │   └── push-images
     ├── tasks
     │   └── ...
     └── vars
         └── ocp-extra-vars.yml

The __roles__ directory has implemented Ansible roles that are reusable and are be included in the playbook `ocp-deployment.yml`. The following roles are used to build images of your SAP HANA and SAP S/4HANA reference system:
 
  + The role __os-prerequisites__ installs packages like podman, git, python3, python3-devel, paramiko and includes tasks for RHEL 8.x as additional prerequisites. This role also verifies if oc tool is installed and checks the connection to the NFS  server. It generates the configuration file `config.yaml` and verifies if all input variables are valid.
  + The role __ocp-prerequisites__ creates a new project on the Red Hat OpenShift cluster, sets up permissions and generates the service-account. 
  + The role __copy-hdb-nfs__ creates a snapshot copy of your SAP HANA `data` and `log` directories on the NFS server. 
  + The role __build-images__ runs the image building process of SAP HANA and SAP S/4HANA.
  
To deploy the build images into the Red Hat OpenShift cluster these roles are used:

  + The role __push-images__ executes a task to push all images (Init, `<your NWS4-SID>`, `<your SAP HANA SID>`) from the local registry to your Red Hat OpenShift cluster.
  + The role __create-overlay-share__ creates an SAP HANA overlay share on the NFS server. 
  + The role __deploy-images__ generates a deployment file about setup and environment for deployment in the Red Hat OpenShift cluster.
  
### Specify your settings

The __vars__ directory has the file `vars/ocp-extra-vars.yml` comprises all required variables, that are used in the playbooks. Some variables may contain sensitive information like IP addresses, passwords, usernames. Optionally use Ansible Vault utility to encrypt this content. In order to keep it simple, we've omitted the  Ansible Vault here. See Red Hat "[Ansible documentation](https://docs.ansible.com/ansible/latest/user_guide/vault.html)" for a details. 

The `vars/ocp-extra-vars.yml` file looks as shown. (Replace all placeholders starting with "less than" and ending with "greater than" signs with your own settings.)
```
---
######################
# build LPAR parameter
######################

# Path to the directory of the clone of this repository on the build LPAR
path_to_ocp_tool: <github_clone_dir>

# Directory under which the build contexts for image build are assembled
tmp_root: /data/tmp

# installs packages with ansible package module and state present
package_state: present

# generate config file for automatic tools script execution with template config.j2.template
template_config_file: config.j2.template


#####################################
# Red Hat OpenShift cluster parameter
#####################################

# Domain name of the Red Hat OpenShift Container Platform (OCP) cluster - used for "oc" operations
# The build LPAR must be able to connect to api.<ocp_cluster_domain>
ocp_cluster_domain: <ocp4-domain-name>

# Password of the kubeadmin user in the cluster
admin_psw: <kubeadmin-password>

# User in the Red Hat OpenShift cluster which is used for "oc" operations
oc_user: <ocp4-userid>

# Password of ocp_user in the Red Hat OpenShift cluster
oc_psw: <ocp4-user-password>

# Name of the project which will be created for the SAP workload (e.g. my-sap-project)
oc_project_name: <ocp4_project_name_for_SAP>


########################################
# SAP NetWeaver or SAP S/4HANA parameter
########################################

# Host on which the original SAP NetWeaver or SAP S/4HANA system is installed
# The SAP instance profile must also have this hostname in its name
host_nws4: <reference_system_hostname>

# User on host_nws4 which is used for ssh and rsync operations (needs root permissions)
host_user_nws4: root

# SAP system ID of the original SAP NetWeaver or SAP S/4HANA system (upper case)
nws4_sid: <AppServer_SID>

# SAP system ID of the original SAP NetWeaver or SAP S/4HANA system (lower case)
# Use lower case "sid" to generate deployment file name
nws4_sid_lower_case: <AppServer_sid_lower_case>

# SAP system ID of the original SAP HANA system (lower case)
# Use lower case "sid" to generate deployment file name
hdb_sid_deployment: <HANA_sid_lower_case>


###############
# NFS parameter
###############

# Host on which the NFS server is running
nfs_host: <NFS_server_hostname>

# User on nfs.host which is used for ssh and rsync operations (needs root permissions)
# Password-less access for this user from build LPAR to NFS server must be configured
nfs_user: root

# Path on nfs_host where directories {data,log} of the original SAP HANA system are copied to
path_to_hdb_copy: <NFS_server_export_dir_for_hdb>

# Path on nfs_host under which overlay file systems for container instances are created
path_to_overlay: <NFS_server_export_dir_for_overlay>
```

### Manual tasks before running the playbook

The following tasks are not automated and you need to do it manually:
  
  + Check if your file system on the build machine has at least 500 GB capacity, see more details in the readme part ["Prerequisites"](https://github.com/IBM/containerization-for-sap-s4hana#prerequisites),
  + Create symbolic links to directories where images of SAP HANA and SAP S/4HANA will be built, see more details in the readme part ["Prerequisites"](https://github.com/IBM/containerization-for-sap-s4hana#prerequisites),
  + Insert the `<helper-node-ip> api.<ocp-cluster-domain> oauth-openshift.apps.<ocp-cluster-domain> default-route-openshift-image-registry.apps.<ocp-cluster-domain>` into the `/etc/hosts` file on your build LPAR.  
  + Copy the public SSH key of the NFS server to your build LPAR: `ssh-copy-id -i ~/.ssh/<nfs_rsa_key>.pub <user_name>@<build_host_name>`.

### Setup inventory for playbook

Before running the `ocp-deployment.yml` playbook, you need to set up your inventory file. On your build machine define the file `ansible/hosts` in the __ansible__ directory. There, add the name of your build server and save. In the __ansible__ directory create a new directory __host_vars__ and there define a file name exactly as your build server name in the __hosts__ it may look like `ansible/host_vars/<your_build_server>.yml`. In this file add your remote username and SSH key:

```
---
ansible_user: <username>
ansible_ssh_private_key_file: ~/.ssh/<your_rsa_key>  
```
### Run playbook

For execution, run the playbook `ocp-deployment.yml` by passing extra variables using the option -e for extra variables as shown: 

```shell
     $ cd ansible
     $ ansible-playbook -i hosts -e @vars/ocp-extra-vars.yml ocp-deployment.yml
```

The playbook will install all prerequisites and three container images `Init`, `<your NWS4-SID>`, `<your SAP HANA SID>` will be created. These images will be stored in the local podman registry on your build LPAR. 
Then the playbook will use the roles `push-images`, `create-overlay-share`, `deploy-images` to deploy the container images in the cluster. 

If the playbook run completed without errors, all three images will be successfully deployed on the Red Hat OpenShift cluster. 

### Verify SAP system in cluster

Access to the SAP system from outside the cluster is enabled by a cluster service of type NodePort. Verify whether the service was correctly started by running

     $ oc get service/soos-<nws4-sid>-np

     NAME                 TYPE       CLUSTER-IP       EXTERNAL-IP   PORT(S)                              AGE
     soos-<nws4-sid>-np   NodePort   172.30.187.181   <none>        32<nws4-di-instno>:<node-port>/TCP   9m9s

To verify if SAP HANA and SAP S/4 HANA are running in the cluster use this command:

```shell
    $ oc describe pod soos-<nws4-sid>
```

### Connect to the SAP system

Look at the following page "[Connecting to the SAP system](https://github.com/IBM/containerization-for-sap-s4hana#connecting-to-the-sap-system)" how to connect to SAP system.

### Recover from errors

In case the execution of playbooks failed then you can delete your deployment from the cluster, using the implemented task in `tasks/stop-deployment.yml`. Include this task with `import_tasks` in your playbook and run it.

To remove one or more of previously created containers in your local storage, list them with the command: 

   `podman images`
       
Copy the container ID and remove the container by issuing:

   `podman rm -f <IMAGE ID>`
       
## Building and deploying with Red Hat Ansible Tower

### Getting started

We assume that you have already installed and configured Red Hat Ansible Tower on your host machine. In case that you need to install it then have a look at the "[Ansible Automation Platform Quick Installation Guide](https://docs.ansible.com/ansible-tower/latest/html/quickinstall/index.html)". It describes basic installation instructions, more detailed information is available in the "[Installation and Reference Guide](https://docs.ansible.com/ansible-tower/3.8.0/html/installandreference/index.html#ir-start)".

### Manual tasks

See above subchapter "[Manual tasks before running the playbook](#manual-tasks-before-running-the-playbook)".

### Create new project

First, you need to set up a project that will be used in a job template for building and deploying images. To define a new project, log in to Red Hat Ansible Tower web interface using admin-level credentials. Select *Projects* on the left navigation bar, click a green plus-button on the right top corner. You will get a new project view where you need to fill out all required fields: 

   + Define a project name.
   + Add a description.
   + Select organization, as example `Default` can be used.
   + Select `Git` as __SCM TYPE__.
   + Specify __SCM BRANCH/TAG/COMMIT__ to checkout source code, as example `master` can be defined.
   + Select __SCM UPDATE OPTIONS__ check boxes such as `clean`, `delete on update` and `update revision on launch`.

You do not need credentials for the open source GitHub repository, because the provided
URL, is public, and you can copy it into the field SCM URL of the Projects template as shown:

__SCM URL__: `https://github.com/IBM/containerization-for-sap-s4hana.git`

![New Project view](../docs/images/ansible_tower_projects_view.png)

### Create inventory

For the job template you need to set up your inventory defining the build host and credentials. Refer to the chapter "[Inventories](https://docs.ansible.com/ansible-tower/latest/html/userguide/inventories.html)" in the Ansible Tower User Guide v3.8.0. to find detailed instructions.

### Create new job template

Next, select *Templates* on the left side of navigation panel and you will see a list of job templates if there are any. To define a new job template click the green plus on the top right corner as shown: 

![How to add a new job template](../docs/images/ansible_tower_add_new_job_template.png)

You have to fill out all required fields and if you want optional too. The detailed explanation about job templates you can find in the chapter "[Job Templates](https://docs.ansible.com/ansible-tower/latest/html/userguide/job_templates.html)" of Ansible Tower User Guide v3.8.0. 

In the field __Extra Variables__ you need to add your own specified variables from the file `ocp-extra-vars.yml` in the __vars__ directory. See subchapter "[Specify your settings](#specify-your-settings)" for all required variables. In the field __Playbook__ select the playbook `ansible/ocp-deployment-ansible-tower.yml` that inside ansible directory. 

Finally save the job template.

### Launch job

Then launch the job. If the job run is successful it has a green status that means building and deployment of SAP HANA and SAP
S/4HANA images successfully completed. After that you can verify if SAP HANA and SAP S/4 HANA are running, how to do it see the readme part "[Verifying the correct start of the SAP system](https://github.com/IBM/containerization-for-sap-s4hana#verifying-the-correct-start-of-the-sap-system)". 

### Connect to the SAP system

To connect to SAP system see the "[Connecting to the SAP system](https://github.com/IBM/containerization-for-sap-s4hana#connecting-to-the-sap-system)" part of the readme file.
