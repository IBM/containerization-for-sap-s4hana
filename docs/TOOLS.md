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

## Contents

<details>
  <summary>Table of Contents</summary>

- [Overview of the Tools](#overview-of-the-tools)
- [Tool `codingstyle`](#tool-codingstyle)
  - [Usage](#usage)
  - [Purpose](#purpose)
  - [Arguments](#arguments)
- [Tool `config`](#tool-config)
  - [Usage](#usage-1)
  - [Purpose](#purpose-1)
  - [Arguments](#arguments-1)
- [Tool `containerize`](#tool-containerize)
  - [Usage](#usage-2)
  - [Purpose](#purpose-2)
  - [Arguments](#arguments-2)
- [Tool `creds`](#tool-creds)
  - [Usage](#usage-3)
  - [Purpose](#purpose-3)
  - [Arguments](#arguments-3)
- [Tool `gpg-key-gen`](#tool-gpg-key-gen)
  - [Usage](#usage-4)
  - [Purpose](#purpose-4)
- [Tool `image-build`](#tool-image-build)
  - [Usage](#usage-5)
  - [Purpose](#purpose-5)
  - [Arguments](#arguments-4)
- [Tool `image-push`](#tool-image-push)
  - [Usage](#usage-6)
  - [Purpose](#purpose-6)
  - [Arguments](#arguments-5)
- [Tool `nfs-hdb-copy`](#tool-nfs-hdb-copy)
  - [Usage](#usage-7)
  - [Purpose](#purpose-7)
  - [Arguments](#arguments-6)
- [Tool `nfs-overlay-list`](#tool-nfs-overlay-list)
  - [Usage](#usage-8)
  - [Purpose](#purpose-8)
  - [Arguments](#arguments-7)
- [Tool `nfs-overlay-setup`](#tool-nfs-overlay-setup)
  - [Usage](#usage-9)
  - [Purpose](#purpose-9)
  - [Arguments](#arguments-8)
- [Tool `nfs-overlay-teardown`](#tool-nfs-overlay-teardown)
  - [Usage](#usage-10)
  - [Purpose](#purpose-10)
  - [Arguments](#arguments-9)
- [Tool `ocp-container-login`](#tool-ocp-container-login)
  - [Usage](#usage-11)
  - [Purpose](#purpose-11)
  - [Arguments](#arguments-10)
- [Tool `ocp-container-run`](#tool-ocp-container-run)
  - [Usage](#usage-12)
  - [Purpose](#purpose-12)
  - [Arguments](#arguments-11)
- [Tool `ocp-deployment-gen`](#tool-ocp-deployment-gen)
  - [Usage](#usage-13)
  - [Purpose](#purpose-13)
  - [Arguments](#arguments-12)
- [Tool `ocp-etc-hosts`](#tool-ocp-etc-hosts)
  - [Usage](#usage-14)
  - [Purpose](#purpose-14)
  - [Arguments](#arguments-13)
- [Tool `ocp-hdb-secret-gen`](#tool-ocp-hdb-secret-gen)
  - [Usage](#usage-15)
  - [Purpose](#purpose-15)
  - [Arguments](#arguments-14)
- [Tool `ocp-login`](#tool-ocp-login)
  - [Usage](#usage-16)
  - [Purpose](#purpose-16)
  - [Arguments](#arguments-15)
- [Tool `ocp-pod-meminfo`](#tool-ocp-pod-meminfo)
  - [Usage](#usage-17)
  - [Purpose](#purpose-17)
  - [Arguments](#arguments-16)
- [Tool `ocp-pod-status`](#tool-ocp-pod-status)
  - [Usage](#usage-18)
  - [Purpose](#purpose-18)
  - [Arguments](#arguments-17)
- [Tool `ocp-port-forwarding`](#tool-ocp-port-forwarding)
  - [Usage](#usage-19)
  - [Purpose](#purpose-19)
  - [Arguments](#arguments-18)
- [Tool `ocp-service-account-gen`](#tool-ocp-service-account-gen)
  - [Usage](#usage-20)
  - [Purpose](#purpose-20)
  - [Arguments](#arguments-19)
- [Tool `sap-system-status`](#tool-sap-system-status)
  - [Usage](#usage-21)
  - [Purpose](#purpose-21)
  - [Arguments](#arguments-20)
- [Tool `ssh-key-gen`](#tool-ssh-key-gen)
  - [Usage](#usage-22)
  - [Purpose](#purpose-22)
  - [Arguments](#arguments-21)
- [Tool `ssh-keys`](#tool-ssh-keys)
  - [Usage](#usage-23)
  - [Purpose](#purpose-23)
  - [Arguments](#arguments-22)
- [Tool `venv-setup`](#tool-venv-setup)
  - [Usage](#usage-24)
  - [Purpose](#purpose-24)
- [Tool `verify-config`](#tool-verify-config)
  - [Usage](#usage-25)
  - [Purpose](#purpose-25)
  - [Arguments](#arguments-23)
- [Tool `verify-ocp-settings`](#tool-verify-ocp-settings)
  - [Usage](#usage-26)
  - [Purpose](#purpose-26)
  - [Arguments](#arguments-24)

</details>


## Overview of the Tools

The tools are located in the `tools` directory of the repository clone.

Purpose of the tools is to

* prepare the infrastructure environment for the container build
* build images from a reference SAP® system
* deploy containers based on these images to Red Hat® OpenShift® Container Platform
* run the containers in the Red Hat OpenShift Container Platform
* manage and monitor the containers deployed to Red Hat OpenShift Container Platform

The tools are invoked from command line.

Containerization is supported for target platform Red Hat OpenShift Container Platform on IBM® Power Systems™.

<details>
<summary>List of tools</summary>

- [Tool `codingstyle`](#tool-codingstyle)
- [Tool `config`](#tool-config)
- [Tool `containerize`](#tool-containerize)
- [Tool `creds`](#tool-creds)
- [Tool `gpg-key-gen`](#tool-gpg-key-gen)
- [Tool `image-build`](#tool-image-build)
- [Tool `image-push`](#tool-image-push)
- [Tool `nfs-hdb-copy`](#tool-nfs-hdb-copy)
- [Tool `nfs-overlay-list`](#tool-nfs-overlay-list)
- [Tool `nfs-overlay-setup`](#tool-nfs-overlay-setup)
- [Tool `nfs-overlay-teardown`](#tool-nfs-overlay-teardown)
- [Tool `ocp-container-login`](#tool-ocp-container-login)
- [Tool `ocp-container-run`](#tool-ocp-container-run)
- [Tool `ocp-deployment-gen`](#tool-ocp-deployment-gen)
- [Tool `ocp-etc-hosts`](#tool-ocp-etc-hosts)
- [Tool `ocp-hdb-secret-gen`](#tool-ocp-hdb-secret-gen)
- [Tool `ocp-login`](#tool-ocp-login)
- [Tool `ocp-pod-meminfo`](#tool-ocp-pod-meminfo)
- [Tool `ocp-pod-status`](#tool-ocp-pod-status)
- [Tool `ocp-port-forwarding`](#tool-ocp-port-forwarding)
- [Tool `ocp-service-account-gen`](#tool-ocp-service-account-gen)
- [Tool `sap-system-status`](#tool-sap-system-status)
- [Tool `ssh-key-gen`](#tool-ssh-key-gen)
- [Tool `ssh-keys`](#tool-ssh-keys)
- [Tool `venv-setup`](#tool-venv-setup)
- [Tool `verify-config`](#tool-verify-config)
- [Tool `verify-ocp-settings`](#tool-verify-ocp-settings)

</details>

## Tool `codingstyle`
### Usage
`codingstyle [-h] [-c <config-file>] [-q <creds-file>] [-g <logfile-dir>] [-v {critical,error,warning,info,debug,notset}] [-w] [--dump-context] [-r <recursion-level>] [-f <format>] <source> [<source> ...] `
### Purpose

Check coding style of python files


### Arguments
| Arguments | Description | Default |
|:----------|:------------|:--------|
|`-h, --help`|show this help message and exit||
|`-c <config-file>, --config-file <config-file>`|Configuration file |`./config.yaml`|
|`-q <creds-file>, --creds-file <creds-file>`|Credentials file (encrypted) |`./creds.yaml.gpg`|
|`-g <logfile-dir>, --logfile-dir <logfile-dir>`|logfile directory |`./log`|
|`-v {critical,error,warning,info,debug,notset}, --loglevel {critical,error,warning,info,debug,notset}`|logging level |`warning`|
|`-w, --log-to-terminal`|Log to terminal instead of logging to file |`False`|
|`--dump-context`|Dump context (CLI arguments, configuration, credentials) |`False`|
|`-r <recursion-level>, --recursion-level <recursion-level>`|Perform recursive check up to depth \<recursion-level\> if \<source\> is a directory; ('-1': no depth limitation) |`0`|
|`-f <format>, --format <format>`|Select output format ('text', 'html', 'empty') |`text`| 
## Tool `config`
### Usage
`config [-h] [-c <config-file>] [-q <creds-file>] [-g <logfile-dir>] [-v {critical,error,warning,info,debug,notset}] [-w] [--dump-context] [-n] [-e] [-d] [--non-interactive] [-s] `
### Purpose

Configuration management


### Arguments
| Arguments | Description | Default |
|:----------|:------------|:--------|
|`-h, --help`|show this help message and exit||
|`-c <config-file>, --config-file <config-file>`|Configuration file |`./config.yaml`|
|`-q <creds-file>, --creds-file <creds-file>`|Credentials file (encrypted) |`./creds.yaml.gpg`|
|`-g <logfile-dir>, --logfile-dir <logfile-dir>`|logfile directory |`./log`|
|`-v {critical,error,warning,info,debug,notset}, --loglevel {critical,error,warning,info,debug,notset}`|logging level |`warning`|
|`-w, --log-to-terminal`|Log to terminal instead of logging to file |`False`|
|`--dump-context`|Dump context (CLI arguments, configuration, credentials) |`False`|
|`-n, --new`|Create a new configuration file |`False`|
|`-e, --edit`|Change configuration in an existing configuration file |`False`|
|`-d, --dump`|Dump configuration to stdout |`False`|
|`--non-interactive`|Perform '-n' and '-e' non-interactively (reading values from environment) |`False`|
|`-s, --suppress-descriptions`|Don't show detailed descriptions during edit |`False`| 
## Tool `containerize`
### Usage
`containerize [-h] [-c <config-file>] [-q <creds-file>] [-g <logfile-dir>] [-v {critical,error,warning,info,debug,notset}] [-w] [--dump-context] [-y] [-b] [-p] [-o] [-u <overlay-uuid>] [-l] [-t] [-d] [-s] [-x] [-a] [-r] `
### Purpose

Automated build, push and deploy


### Arguments
| Arguments | Description | Default |
|:----------|:------------|:--------|
|`-h, --help`|show this help message and exit||
|`-c <config-file>, --config-file <config-file>`|Configuration file |`./config.yaml`|
|`-q <creds-file>, --creds-file <creds-file>`|Credentials file (encrypted) |`./creds.yaml.gpg`|
|`-g <logfile-dir>, --logfile-dir <logfile-dir>`|logfile directory |`./log`|
|`-v {critical,error,warning,info,debug,notset}, --loglevel {critical,error,warning,info,debug,notset}`|logging level |`warning`|
|`-w, --log-to-terminal`|Log to terminal instead of logging to file |`False`|
|`--dump-context`|Dump context (CLI arguments, configuration, credentials) |`False`|
|`-y, --hdb-copy`|Copy HANA DB snapshot to NFS server |`False`|
|`-b, --build-images`|Build images |`False`|
|`-p, --push-images`|Push images to local OCP cluster registry |`False`|
|`-o, --setup-overlay-share`|Setup overlay share |`False`|
|`-u <overlay-uuid>, --overlay-uuid <overlay-uuid>`|UUID of overlay share for options '-d' and '-t' |`None`|
|`-l, --list-overlay-shares`|List existing overlay shares |`False`|
|`-t, --tear-down-overlay-share`|Tear down overlay share specified with option '-u' |`False`|
|`-d, --create-deployment-file`|Create deployment file |`False`|
|`-s, --start-deployment`|Start deployment on OCP cluster |`False`|
|`-x, --stop-deployment`|Stop deployment on OCP cluster |`False`|
|`-a, --execute-all`|Execute all actions (except '-t', '-l' and '-x') |`False`|
|`-r, --execute-rest`|Start with specified action and execute all subsequent actions in automation process. |`False`| 
## Tool `creds`
### Usage
`creds [-h] [-c <config-file>] [-q <creds-file>] [-g <logfile-dir>] [-v {critical,error,warning,info,debug,notset}] [-w] [--dump-context] [-n] [-e] [-d] [--non-interactive] [-s] [-u] [-r <recipient>] `
### Purpose

Credentials management


### Arguments
| Arguments | Description | Default |
|:----------|:------------|:--------|
|`-h, --help`|show this help message and exit||
|`-c <config-file>, --config-file <config-file>`|Configuration file |`./config.yaml`|
|`-q <creds-file>, --creds-file <creds-file>`|Credentials file (encrypted) |`./creds.yaml.gpg`|
|`-g <logfile-dir>, --logfile-dir <logfile-dir>`|logfile directory |`./log`|
|`-v {critical,error,warning,info,debug,notset}, --loglevel {critical,error,warning,info,debug,notset}`|logging level |`warning`|
|`-w, --log-to-terminal`|Log to terminal instead of logging to file |`False`|
|`--dump-context`|Dump context (CLI arguments, configuration, credentials) |`False`|
|`-n, --new`|Create a new credentials file |`False`|
|`-e, --edit`|Change credentials in an existing credentials file |`False`|
|`-d, --dump`|Dump credentials to stdout (DISPLAYS SECRETS IN CLEAR TEXT) |`False`|
|`--non-interactive`|Perform '-n' and '-e' non-interactively (reading values from environment) |`False`|
|`-s, --suppress-descriptions`|Don't show detailed descriptions during edit |`False`|
|`-u, --unencrypted`|If '-n' is specified: Don't encrypt a newly created credentials file |`False`|
|`-r <recipient>, --recipient <recipient>`|If '-n' is specified and '-u' is not specified: Owner e-mail address or key fingerprint of GPG key which will be used for encrypting a newly created credentials file. If not specified, symmetric AES256 encryption is used. |`None`| 
## Tool `gpg-key-gen`
### Usage
`gpg-key-gen`
### Purpose
Generate GPG key for build user for asymmetric encryption

Use reported **\<recipient\>** for subsequent `tools/creds [-r <recipient>]` operations

## Tool `image-build`
### Usage
`image-build [-h] [-c <config-file>] [-q <creds-file>] [-g <logfile-dir>] [-v {critical,error,warning,info,debug,notset}] [-w] [--dump-context] [-f <image-flavor>] [-t <temp-root>] [-d <build-dir>] [-k] `
### Purpose

Build a container image of a given flavor


### Arguments
| Arguments | Description | Default |
|:----------|:------------|:--------|
|`-h, --help`|show this help message and exit||
|`-c <config-file>, --config-file <config-file>`|Configuration file |`./config.yaml`|
|`-q <creds-file>, --creds-file <creds-file>`|Credentials file (encrypted) |`./creds.yaml.gpg`|
|`-g <logfile-dir>, --logfile-dir <logfile-dir>`|logfile directory |`./log`|
|`-v {critical,error,warning,info,debug,notset}, --loglevel {critical,error,warning,info,debug,notset}`|logging level |`warning`|
|`-w, --log-to-terminal`|Log to terminal instead of logging to file |`False`|
|`--dump-context`|Dump context (CLI arguments, configuration, credentials) |`False`|
|`-f <image-flavor>, --image-flavor <image-flavor>`|Image flavor ('init', 'nws4', 'hdb') |`init`|
|`-t <temp-root>, --temp-root <temp-root>`|Use \<temp-root\> as root for temporary files generated during build |`/data/tmp`|
|`-d <build-dir>, --build-directory <build-dir>`|Use \<build-dir\> as build directory; if not specified, a new build directory is created under '\<temp-root\>' |`None`|
|`-k, --keep-files`|Keep existing files in <build-dir> which were copied from <host> in a previous run; has no effect if '-d' is not specified |`False`| 
## Tool `image-push`
### Usage
`image-push [-h] [-c <config-file>] [-q <creds-file>] [-g <logfile-dir>] [-v {critical,error,warning,info,debug,notset}] [-w] [--dump-context] [-f <image-flavor>] `
### Purpose

Push a container image of a given flavor to the internal cluster registry


### Arguments
| Arguments | Description | Default |
|:----------|:------------|:--------|
|`-h, --help`|show this help message and exit||
|`-c <config-file>, --config-file <config-file>`|Configuration file |`./config.yaml`|
|`-q <creds-file>, --creds-file <creds-file>`|Credentials file (encrypted) |`./creds.yaml.gpg`|
|`-g <logfile-dir>, --logfile-dir <logfile-dir>`|logfile directory |`./log`|
|`-v {critical,error,warning,info,debug,notset}, --loglevel {critical,error,warning,info,debug,notset}`|logging level |`warning`|
|`-w, --log-to-terminal`|Log to terminal instead of logging to file |`False`|
|`--dump-context`|Dump context (CLI arguments, configuration, credentials) |`False`|
|`-f <image-flavor>, --image-flavor <image-flavor>`|Image flavor ('init', 'nws4', 'hdb') |`init`| 
## Tool `nfs-hdb-copy`
### Usage
`nfs-hdb-copy [-h] [-c <config-file>] [-q <creds-file>] [-g <logfile-dir>] [-v {critical,error,warning,info,debug,notset}] [-w] [--dump-context] `
### Purpose

Copy an SAP HANA DB snapshot the NFS server


### Arguments
| Arguments | Description | Default |
|:----------|:------------|:--------|
|`-h, --help`|show this help message and exit||
|`-c <config-file>, --config-file <config-file>`|Configuration file |`./config.yaml`|
|`-q <creds-file>, --creds-file <creds-file>`|Credentials file (encrypted) |`./creds.yaml.gpg`|
|`-g <logfile-dir>, --logfile-dir <logfile-dir>`|logfile directory |`./log`|
|`-v {critical,error,warning,info,debug,notset}, --loglevel {critical,error,warning,info,debug,notset}`|logging level |`warning`|
|`-w, --log-to-terminal`|Log to terminal instead of logging to file |`False`|
|`--dump-context`|Dump context (CLI arguments, configuration, credentials) |`False`| 
## Tool `nfs-overlay-list`
### Usage
`nfs-overlay-list [-h] [-c <config-file>] [-q <creds-file>] [-g <logfile-dir>] [-v {critical,error,warning,info,debug,notset}] [-w] [--dump-context] `
### Purpose

List availabe overlay shares on NFS server


### Arguments
| Arguments | Description | Default |
|:----------|:------------|:--------|
|`-h, --help`|show this help message and exit||
|`-c <config-file>, --config-file <config-file>`|Configuration file |`./config.yaml`|
|`-q <creds-file>, --creds-file <creds-file>`|Credentials file (encrypted) |`./creds.yaml.gpg`|
|`-g <logfile-dir>, --logfile-dir <logfile-dir>`|logfile directory |`./log`|
|`-v {critical,error,warning,info,debug,notset}, --loglevel {critical,error,warning,info,debug,notset}`|logging level |`warning`|
|`-w, --log-to-terminal`|Log to terminal instead of logging to file |`False`|
|`--dump-context`|Dump context (CLI arguments, configuration, credentials) |`False`| 
## Tool `nfs-overlay-setup`
### Usage
`nfs-overlay-setup [-h] [-c <config-file>] [-q <creds-file>] [-g <logfile-dir>] [-v {critical,error,warning,info,debug,notset}] [-w] [--dump-context] `
### Purpose

Setup overlay file system on NFS server


### Arguments
| Arguments | Description | Default |
|:----------|:------------|:--------|
|`-h, --help`|show this help message and exit||
|`-c <config-file>, --config-file <config-file>`|Configuration file |`./config.yaml`|
|`-q <creds-file>, --creds-file <creds-file>`|Credentials file (encrypted) |`./creds.yaml.gpg`|
|`-g <logfile-dir>, --logfile-dir <logfile-dir>`|logfile directory |`./log`|
|`-v {critical,error,warning,info,debug,notset}, --loglevel {critical,error,warning,info,debug,notset}`|logging level |`warning`|
|`-w, --log-to-terminal`|Log to terminal instead of logging to file |`False`|
|`--dump-context`|Dump context (CLI arguments, configuration, credentials) |`False`| 
## Tool `nfs-overlay-teardown`
### Usage
`nfs-overlay-teardown [-h] [-c <config-file>] [-q <creds-file>] [-g <logfile-dir>] [-v {critical,error,warning,info,debug,notset}] [-w] [--dump-context] -u <overlay-uuid> `
### Purpose

Tear down overlay file system on NFS server


### Arguments
| Arguments | Description | Default |
|:----------|:------------|:--------|
|`-h, --help`|show this help message and exit||
|`-c <config-file>, --config-file <config-file>`|Configuration file |`./config.yaml`|
|`-q <creds-file>, --creds-file <creds-file>`|Credentials file (encrypted) |`./creds.yaml.gpg`|
|`-g <logfile-dir>, --logfile-dir <logfile-dir>`|logfile directory |`./log`|
|`-v {critical,error,warning,info,debug,notset}, --loglevel {critical,error,warning,info,debug,notset}`|logging level |`warning`|
|`-w, --log-to-terminal`|Log to terminal instead of logging to file |`False`|
|`--dump-context`|Dump context (CLI arguments, configuration, credentials) |`False`|
|`-u <overlay-uuid>, --overlay-uuid <overlay-uuid>`|UUID of the overlay NFS share on which the HANA DB data resides |`None`| 
## Tool `ocp-container-login`
### Usage
`ocp-container-login [-h] [-c <config-file>] [-q <creds-file>] [-g <logfile-dir>] [-v {critical,error,warning,info,debug,notset}] [-w] [--dump-context] [-i <container-flavor>] `
### Purpose

Interactively log into a container running in an OpenShift cluster


### Arguments
| Arguments | Description | Default |
|:----------|:------------|:--------|
|`-h, --help`|show this help message and exit||
|`-c <config-file>, --config-file <config-file>`|Configuration file |`./config.yaml`|
|`-q <creds-file>, --creds-file <creds-file>`|Credentials file (encrypted) |`./creds.yaml.gpg`|
|`-g <logfile-dir>, --logfile-dir <logfile-dir>`|logfile directory |`./log`|
|`-v {critical,error,warning,info,debug,notset}, --loglevel {critical,error,warning,info,debug,notset}`|logging level |`warning`|
|`-w, --log-to-terminal`|Log to terminal instead of logging to file |`False`|
|`--dump-context`|Dump context (CLI arguments, configuration, credentials) |`False`|
|`-i <container-flavor>, --container-flavor <container-flavor>`|Container flavor ('di', 'ascs', 'hdb') |`di`| 
## Tool `ocp-container-run`
### Usage
`ocp-container-run [-h] [-c <config-file>] [-q <creds-file>] [-g <logfile-dir>] [-v {critical,error,warning,info,debug,notset}] [-w] [--dump-context] [-i <container-flavor>] command `
### Purpose

Log into a container running in an OpenShift cluster

### Arguments
| Arguments | Description | Default |
|:----------|:------------|:--------|
|`-h, --help`|show this help message and exit||
|`-c <config-file>, --config-file <config-file>`|Configuration file |`./config.yaml`|
|`-q <creds-file>, --creds-file <creds-file>`|Credentials file (encrypted) |`./creds.yaml.gpg`|
|`-g <logfile-dir>, --logfile-dir <logfile-dir>`|logfile directory |`./log`|
|`-v {critical,error,warning,info,debug,notset}, --loglevel {critical,error,warning,info,debug,notset}`|logging level |`warning`|
|`-w, --log-to-terminal`|Log to terminal instead of logging to file |`False`|
|`--dump-context`|Dump context (CLI arguments, configuration, credentials) |`False`|
|`-i <container-flavor>, --container-flavor <container-flavor>`|Container flavor ('di', 'ascs', 'hdb') |`di`| 
## Tool `ocp-deployment-gen`
### Usage
`ocp-deployment-gen [-h] [-c <config-file>] [-q <creds-file>] [-g <logfile-dir>] [-v {critical,error,warning,info,debug,notset}] [-w] [--dump-context] -u <overlay-uuid> [-o <output-file>] `
### Purpose

Generate OpenShift deployment YAML file


### Arguments
| Arguments | Description | Default |
|:----------|:------------|:--------|
|`-h, --help`|show this help message and exit||
|`-c <config-file>, --config-file <config-file>`|Configuration file |`./config.yaml`|
|`-q <creds-file>, --creds-file <creds-file>`|Credentials file (encrypted) |`./creds.yaml.gpg`|
|`-g <logfile-dir>, --logfile-dir <logfile-dir>`|logfile directory |`./log`|
|`-v {critical,error,warning,info,debug,notset}, --loglevel {critical,error,warning,info,debug,notset}`|logging level |`warning`|
|`-w, --log-to-terminal`|Log to terminal instead of logging to file |`False`|
|`--dump-context`|Dump context (CLI arguments, configuration, credentials) |`False`|
|`-u <overlay-uuid>, --overlay-uuid <overlay-uuid>`|UUID of the overlay NFS share on which the HANA DB data resides |`None`|
|`-o <output-file>, --output-file <output-file>`|Path to output file |`None`| 
## Tool `ocp-etc-hosts`
### Usage
`ocp-etc-hosts [-h] [-c <config-file>] [-q <creds-file>] [-g <logfile-dir>] [-v {critical,error,warning,info,debug,notset}] [-w] [--dump-context] `
### Purpose

Add OpenShift cluster domain entries to '/etc/hosts'


### Arguments
| Arguments | Description | Default |
|:----------|:------------|:--------|
|`-h, --help`|show this help message and exit||
|`-c <config-file>, --config-file <config-file>`|Configuration file |`./config.yaml`|
|`-q <creds-file>, --creds-file <creds-file>`|Credentials file (encrypted) |`./creds.yaml.gpg`|
|`-g <logfile-dir>, --logfile-dir <logfile-dir>`|logfile directory |`./log`|
|`-v {critical,error,warning,info,debug,notset}, --loglevel {critical,error,warning,info,debug,notset}`|logging level |`warning`|
|`-w, --log-to-terminal`|Log to terminal instead of logging to file |`False`|
|`--dump-context`|Dump context (CLI arguments, configuration, credentials) |`False`| 
## Tool `ocp-hdb-secret-gen`
### Usage
`ocp-hdb-secret-gen [-h] [-c <config-file>] [-q <creds-file>] [-g <logfile-dir>] [-v {critical,error,warning,info,debug,notset}] [-w] [--dump-context] `
### Purpose

Generate OpenShift HANA secret YAML file


### Arguments
| Arguments | Description | Default |
|:----------|:------------|:--------|
|`-h, --help`|show this help message and exit||
|`-c <config-file>, --config-file <config-file>`|Configuration file |`./config.yaml`|
|`-q <creds-file>, --creds-file <creds-file>`|Credentials file (encrypted) |`./creds.yaml.gpg`|
|`-g <logfile-dir>, --logfile-dir <logfile-dir>`|logfile directory |`./log`|
|`-v {critical,error,warning,info,debug,notset}, --loglevel {critical,error,warning,info,debug,notset}`|logging level |`warning`|
|`-w, --log-to-terminal`|Log to terminal instead of logging to file |`False`|
|`--dump-context`|Dump context (CLI arguments, configuration, credentials) |`False`| 
## Tool `ocp-login`
### Usage
`ocp-login [-h] [-c <config-file>] [-q <creds-file>] [-g <logfile-dir>] [-v {critical,error,warning,info,debug,notset}] [-w] [--dump-context] [-u] [-a] `
### Purpose

Log into OCP


### Arguments
| Arguments | Description | Default |
|:----------|:------------|:--------|
|`-h, --help`|show this help message and exit||
|`-c <config-file>, --config-file <config-file>`|Configuration file |`./config.yaml`|
|`-q <creds-file>, --creds-file <creds-file>`|Credentials file (encrypted) |`./creds.yaml.gpg`|
|`-g <logfile-dir>, --logfile-dir <logfile-dir>`|logfile directory |`./log`|
|`-v {critical,error,warning,info,debug,notset}, --loglevel {critical,error,warning,info,debug,notset}`|logging level |`warning`|
|`-w, --log-to-terminal`|Log to terminal instead of logging to file |`False`|
|`--dump-context`|Dump context (CLI arguments, configuration, credentials) |`False`|
|`-u, --user`|Log into OCP as regular user |`False`|
|`-a, --admin`|Log into OCP as admin user |`False`| 
## Tool `ocp-pod-meminfo`
### Usage
`ocp-pod-meminfo [-h] [-c <config-file>] [-q <creds-file>] [-g <logfile-dir>] [-v {critical,error,warning,info,debug,notset}] [-w] [--dump-context] [-l] [-t <sleep-time>] `
### Purpose

Get SAP system memory consumption information


### Arguments
| Arguments | Description | Default |
|:----------|:------------|:--------|
|`-h, --help`|show this help message and exit||
|`-c <config-file>, --config-file <config-file>`|Configuration file |`./config.yaml`|
|`-q <creds-file>, --creds-file <creds-file>`|Credentials file (encrypted) |`./creds.yaml.gpg`|
|`-g <logfile-dir>, --logfile-dir <logfile-dir>`|logfile directory |`./log`|
|`-v {critical,error,warning,info,debug,notset}, --loglevel {critical,error,warning,info,debug,notset}`|logging level |`warning`|
|`-w, --log-to-terminal`|Log to terminal instead of logging to file |`False`|
|`--dump-context`|Dump context (CLI arguments, configuration, credentials) |`False`|
|`-l, --loop`|Print information in endless loop |`False`|
|`-t <sleep-time>, --sleep-time <sleep-time>`|Sleep time in seconds between two loop executions |`5`| 
## Tool `ocp-pod-status`
### Usage
`ocp-pod-status [-h] [-c <config-file>] [-q <creds-file>] [-g <logfile-dir>] [-v {critical,error,warning,info,debug,notset}] [-w] [--dump-context] `
### Purpose

Get the status of a pod


### Arguments
| Arguments | Description | Default |
|:----------|:------------|:--------|
|`-h, --help`|show this help message and exit||
|`-c <config-file>, --config-file <config-file>`|Configuration file |`./config.yaml`|
|`-q <creds-file>, --creds-file <creds-file>`|Credentials file (encrypted) |`./creds.yaml.gpg`|
|`-g <logfile-dir>, --logfile-dir <logfile-dir>`|logfile directory |`./log`|
|`-v {critical,error,warning,info,debug,notset}, --loglevel {critical,error,warning,info,debug,notset}`|logging level |`warning`|
|`-w, --log-to-terminal`|Log to terminal instead of logging to file |`False`|
|`--dump-context`|Dump context (CLI arguments, configuration, credentials) |`False`| 
## Tool `ocp-port-forwarding`
### Usage
`ocp-port-forwarding [-h] [-c <config-file>] [-q <creds-file>] [-g <logfile-dir>] [-v {critical,error,warning,info,debug,notset}] [-w] [--dump-context] `
### Purpose

SSH port forwarding for creating a SAP GUI connection to the containerized SAP
system


### Arguments
| Arguments | Description | Default |
|:----------|:------------|:--------|
|`-h, --help`|show this help message and exit||
|`-c <config-file>, --config-file <config-file>`|Configuration file |`./config.yaml`|
|`-q <creds-file>, --creds-file <creds-file>`|Credentials file (encrypted) |`./creds.yaml.gpg`|
|`-g <logfile-dir>, --logfile-dir <logfile-dir>`|logfile directory |`./log`|
|`-v {critical,error,warning,info,debug,notset}, --loglevel {critical,error,warning,info,debug,notset}`|logging level |`warning`|
|`-w, --log-to-terminal`|Log to terminal instead of logging to file |`False`|
|`--dump-context`|Dump context (CLI arguments, configuration, credentials) |`False`| 
## Tool `ocp-service-account-gen`
### Usage
`ocp-service-account-gen [-h] [-c <config-file>] [-q <creds-file>] [-g <logfile-dir>] [-v {critical,error,warning,info,debug,notset}] [-w] [--dump-context] [-o <output-file>] `
### Purpose

Generate YAML file for service account creation


### Arguments
| Arguments | Description | Default |
|:----------|:------------|:--------|
|`-h, --help`|show this help message and exit||
|`-c <config-file>, --config-file <config-file>`|Configuration file |`./config.yaml`|
|`-q <creds-file>, --creds-file <creds-file>`|Credentials file (encrypted) |`./creds.yaml.gpg`|
|`-g <logfile-dir>, --logfile-dir <logfile-dir>`|logfile directory |`./log`|
|`-v {critical,error,warning,info,debug,notset}, --loglevel {critical,error,warning,info,debug,notset}`|logging level |`warning`|
|`-w, --log-to-terminal`|Log to terminal instead of logging to file |`False`|
|`--dump-context`|Dump context (CLI arguments, configuration, credentials) |`False`|
|`-o <output-file>, --output-file <output-file>`|Path to output file |`None`| 
## Tool `sap-system-status`
### Usage
`sap-system-status [-h] [-c <config-file>] [-q <creds-file>] [-g <logfile-dir>] [-v {critical,error,warning,info,debug,notset}] [-w] [--dump-context] [-l] [-t <sleep-time>] [--process-list] `
### Purpose

Get SAP system status


### Arguments
| Arguments | Description | Default |
|:----------|:------------|:--------|
|`-h, --help`|show this help message and exit||
|`-c <config-file>, --config-file <config-file>`|Configuration file |`./config.yaml`|
|`-q <creds-file>, --creds-file <creds-file>`|Credentials file (encrypted) |`./creds.yaml.gpg`|
|`-g <logfile-dir>, --logfile-dir <logfile-dir>`|logfile directory |`./log`|
|`-v {critical,error,warning,info,debug,notset}, --loglevel {critical,error,warning,info,debug,notset}`|logging level |`warning`|
|`-w, --log-to-terminal`|Log to terminal instead of logging to file |`False`|
|`--dump-context`|Dump context (CLI arguments, configuration, credentials) |`False`|
|`-l, --loop`|Print information in endless loop |`False`|
|`-t <sleep-time>, --sleep-time <sleep-time>`|Sleep time in seconds between two loop executions |`5`|
|`--process-list`|Print the process list for every container |`False`| 
## Tool `ssh-key-gen`
### Usage
`ssh-key-gen [-h] [-c <config-file>] [-q <creds-file>] [-g <logfile-dir>] [-v {critical,error,warning,info,debug,notset}] [-w] [--dump-context] [-i <ssh-id>] `
### Purpose

Generate a passphrase-less SSH private / public key pair


### Arguments
| Arguments | Description | Default |
|:----------|:------------|:--------|
|`-h, --help`|show this help message and exit||
|`-c <config-file>, --config-file <config-file>`|Configuration file |`./config.yaml`|
|`-q <creds-file>, --creds-file <creds-file>`|Credentials file (encrypted) |`./creds.yaml.gpg`|
|`-g <logfile-dir>, --logfile-dir <logfile-dir>`|logfile directory |`./log`|
|`-v {critical,error,warning,info,debug,notset}, --loglevel {critical,error,warning,info,debug,notset}`|logging level |`warning`|
|`-w, --log-to-terminal`|Log to terminal instead of logging to file |`False`|
|`--dump-context`|Dump context (CLI arguments, configuration, credentials) |`False`|
|`-i <ssh-id>, --ssh-id <ssh-id>`|Path to the SSH ID private key file |`None`| 
## Tool `ssh-keys`
### Usage
`ssh-keys [-h] [-c <config-file>] [-q <creds-file>] [-g <logfile-dir>] [-v {critical,error,warning,info,debug,notset}] [-w] [--dump-context] [-a] [-d] [-r] [-y] `
### Purpose

Add/remove SSH public keys to/from the various authorized_keys files


### Arguments
| Arguments | Description | Default |
|:----------|:------------|:--------|
|`-h, --help`|show this help message and exit||
|`-c <config-file>, --config-file <config-file>`|Configuration file |`./config.yaml`|
|`-q <creds-file>, --creds-file <creds-file>`|Credentials file (encrypted) |`./creds.yaml.gpg`|
|`-g <logfile-dir>, --logfile-dir <logfile-dir>`|logfile directory |`./log`|
|`-v {critical,error,warning,info,debug,notset}, --loglevel {critical,error,warning,info,debug,notset}`|logging level |`warning`|
|`-w, --log-to-terminal`|Log to terminal instead of logging to file |`False`|
|`--dump-context`|Dump context (CLI arguments, configuration, credentials) |`False`|
|`-a, --add-keys`|Add SSH public keys to the various authorized_keys files |`False`|
|`-d, --display-details`|Display detailed information on which keys are added/removed to the various authorized_keys files of which users |`False`|
|`-r, --remove-keys`|Remove SSH public keys from the various authorized_keys files |`False`|
|`-y, --no-confirm`|Don't confirm adding/removing keys to/from the various authorized_keys files |`False`| 
## Tool `venv-setup`
### Usage
`venv-setup`
### Purpose
Set up a Python virtual environment with all modules that are required to run the tools.

Once the virtual environment is prepared, activate it by running
`source venv/bin/activate` out of the repository directory
before the start of any of the tools.

## Tool `verify-config`
### Usage
`verify-config [-h] [-c <config-file>] [-q <creds-file>] [-g <logfile-dir>] [-v {critical,error,warning,info,debug,notset}] [-w] [--dump-context] `
### Purpose

Verify parameter settings in configuration YAML file


### Arguments
| Arguments | Description | Default |
|:----------|:------------|:--------|
|`-h, --help`|show this help message and exit||
|`-c <config-file>, --config-file <config-file>`|Configuration file |`./config.yaml`|
|`-q <creds-file>, --creds-file <creds-file>`|Credentials file (encrypted) |`./creds.yaml.gpg`|
|`-g <logfile-dir>, --logfile-dir <logfile-dir>`|logfile directory |`./log`|
|`-v {critical,error,warning,info,debug,notset}, --loglevel {critical,error,warning,info,debug,notset}`|logging level |`warning`|
|`-w, --log-to-terminal`|Log to terminal instead of logging to file |`False`|
|`--dump-context`|Dump context (CLI arguments, configuration, credentials) |`False`| 
## Tool `verify-ocp-settings`
### Usage
`verify-ocp-settings [-h] [-c <config-file>] [-q <creds-file>] [-g <logfile-dir>] [-v {critical,error,warning,info,debug,notset}] [-w] [--dump-context] `
### Purpose

Verify OpenShift cluster setup related settings


### Arguments
| Arguments | Description | Default |
|:----------|:------------|:--------|
|`-h, --help`|show this help message and exit||
|`-c <config-file>, --config-file <config-file>`|Configuration file |`./config.yaml`|
|`-q <creds-file>, --creds-file <creds-file>`|Credentials file (encrypted) |`./creds.yaml.gpg`|
|`-g <logfile-dir>, --logfile-dir <logfile-dir>`|logfile directory |`./log`|
|`-v {critical,error,warning,info,debug,notset}, --loglevel {critical,error,warning,info,debug,notset}`|logging level |`warning`|
|`-w, --log-to-terminal`|Log to terminal instead of logging to file |`False`|
|`--dump-context`|Dump context (CLI arguments, configuration, credentials) |`False`| 
