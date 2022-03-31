<!--
  ------------------------------------------------------------------------
  Copyright 2021, 2022 IBM Corp. All Rights Reserved.

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

# Quickstart

This document gives a high-level overview of necessary preparation and
execution steps.

<!-- TOC-START -->

## Contents

<details>
  <summary>Table of Contents</summary>

- [Quickstart for Containerization](#quickstart-for-containerization)
- [Additional Documentation](#additional-documentation)

</details>

<!-- TOC-END -->

## Quickstart for Containerization

The table below outlines the necessary preparation steps both for the
direct execution via scripts and for execution via an Ansible®
playbook.

Steps marked with :yellow_circle: need to be executed manually. Steps
marked with :gear: are automatically executed as part of the Ansible
playbook automation. An :x: indicates that the step/tool is not
available for that context.

| Step | Note | Command / Tool | Python Scripts | Ansible  |
|:------|:----:|:---------------|:--------------:|:--------:|
| Prepare Infrastructure Environment |  | [Build LPAR](./PREREQUISITES.md#preparation-steps-on-the-build-lpar),  [NFS Server](./PREREQUISITES.md#setting-up-the-nfs-server), [Red Hat OpenShift Container Platform](./PREREQUISITES.md#red-hat-openshift-container-platform) and [Reference SAP System](./PREREQUISITES.md#reference-sap-system)| :yellow_circle: | :yellow_circle: |
| [Clone Repository](./PREREQUISITES.md#setting-up-the-clone-repository) | |[```git clone https://github.com/IBM/containerization-for-sap-s4hana.git```](https://github.com/IBM/containerization-for-sap-s4hana.git) |:yellow_circle: | :yellow_circle: |
| [Specify Ansible Settings](./ANSIBLE.md#specifying-your-settings) || ```vi vars/ocp-extra-vars.yml```| N\/A |:yellow_circle: |
| [Setup the Ansible Inventory for the Playbook](./ANSIBLE.md#setting-up-the-inventory-for-the-playbook) || ```vi hosts; mkdir host_vars; vi host_vars/<hostname>.yaml```| N/A |:yellow_circle: |
| [Prepare the Virtual Python Environment](./PREREQUISITES.md#preparing-the-virtual-environment) || [```tools/venv-setup```](./TOOLS.md#tool-venv-setup) | :yellow_circle: | :gear: |
| [Activate the Virtual Python Environment](./PREREQUISITES.md#activating-the-virtual-environment) || ```source venv/bin/activate``` |:yellow_circle: | :gear: |
| Create GPG Key to encrypt Credentials File | :one: | [```tools/gpg-key-gen```](./TOOLS.md#tool-gpg-key-gen)|:yellow_circle: | :x: |
| [Create the Credentials file](./PREREQUISITES.md#preparing-the-credentials-file) | :two: :three: | [```tools/creds```](./TOOLS.md#tool-creds) |  :yellow_circle: | :gear: |
| [Create the Configuration file](./PREREQUISITES.md#preparing-the-configuration-file) |:two: | [```tools/config```](./TOOLS.md#tool-config)|:yellow_circle: | :gear: |
| Create SSH Key for Build User | :three:|[```tools/ssh-key-gen```](./TOOLS.md#tool-ssh-key-gen) <br> or OpenSSH command ```ssh-keygen``` |:yellow_circle: <br> :yellow_circle: | :x: <br> :yellow_circle: |
| [Distribute SSH Keys](./PREREQUISITES.md#distributing-the-ssh-keys) |:three: | [```tools/ssh-keys```](./TOOLS.md#tool-ssh-keys) <br> or OpenSSH command ```ssh-copy-id``` |:yellow_circle: <br> :yellow_circle:| :x: <br> :yellow_circle: |
| [Enable Connection to OCP Cluster](./PREREQUISITES.md#name-resolution-for-red-hat-openshift-container-platform-services) |:four:| [```tools/ocp-etc-hosts```](./TOOLS.md#tool-ocp-etc-hosts)  |:yellow_circle: | :gear: |
| [Create OCP Project](./PREREQUISITES.md#setting-up-the-project) | |OpenShift CLI |:yellow_circle: | :gear: |
| [Create YAML File for OCP Service Account](./PREREQUISITES.md#creating-the-service-account) | |[```tools/ocp-service-account-gen```](./TOOLS.md#tool-ocp-service-account-gen)| :yellow_circle: | :gear: |
| [Create OCP Service Account](./PREREQUISITES.md#creating-the-service-account) | |OpenShift CLI| :yellow_circle: | :gear: |
| [Create Security Context Constraints for OCP User](./PREREQUISITES.md#setting-up-the-permissions) | | OpenShift CLI | :yellow_circle: | :gear: |
| [Create OCP Opaque Secret](./PREREQUISITES.md#setting-up-the-opaque-secret) | :five: | [```tools/ocp-hdb-secret-gen```](./TOOLS.md#tool-ocp-hdb-secret-gen)| :yellow_circle: | :gear: |
| [Verify the Configuration](./PREREQUISITES.md#verifying-the-configuration-file)| |[```tools/verify-config```](./TOOLS.md#tool-verify-config)|:yellow_circle: | :gear: |
| [Verify OCP Settings](./PREREQUISITES.md#verifying-red-hat-openshift-container-platform-settings) | |[```tools/verify-ocp-settings```](./TOOLS.md#tool-verify-ocp-settings)| :yellow_circle: | :gear: |

Notes

:one: Optional. Only required in case you prefer encryption of the
credentials file using asymmetric keys.

:two: Alternatively, it is possible to use your favorite editor and
create the credentials file or configuration file from template file
[`creds.yaml.template`](../creds.yaml.template) or
[`config.yaml.template`](../config.yaml.template). Encryption of the
credentials file however requires usage of ```tools/creds```.

:three: Two different authentication methods may be used for
connectivity to the NFS server, reference SAP system, and OpenShift
helper node. It is possible to

- solely use **username**/**password** authentication. The passwords
  are stored in the credentials file.

- use **SSH key pairs(s)** for authentication. Name and path of the
  private keys are stored in the credentials file. Either already
  existing SSH keys can be specified, or `tools/ssh-key-gen` can be
  used to generate a new key pair for the build
  user. `tools/ssh-keys`can be used to distribute the public key and
  add it to the `authorized_keys` list on the remote system

:four: Only required if build does not run on the cluster helper node

:five: Only required in case of a distributed reference SAP system

Once all the steps above are completed, you are ready to invoke the
containerization.

| Step                   | Python Scripts | Ansible  |
|:-----------------------|:---------------|:---------|
| Building and Deploying |[```tools/containerize -a```](./BUILDING-CLI.md#building-and-deploying-automatically)|[```ansible-playbook -i hosts -e @vars/ocp-extra-vars.yml ocp-deployment.yml```](./ANSIBLE.md#running-the-playbook)|

## Additional Documentation

Refer to the following documents for additional details:

- [*Prerequisites*](./PREREQUISITES.md)
- [*Tools*](./TOOLS.md)
- [*Building Images and Starting Deployments from the Command Line*](./BUILDING-CLI.md)
- [*Building Images and Starting Deployments with Red Hat Ansible*](./ANSIBLE.md)
- [*Verifying and Managing the Deployment*](./VERIFYING-MANAGING.md)
