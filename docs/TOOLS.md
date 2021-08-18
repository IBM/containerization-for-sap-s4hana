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

# Tools

This document describes the command line tools which cover the
various aspects of containerization of reference SAP® systems.

<!-- TOC-START -->

## Contents

<details>
  <summary>Table of Contents</summary>

- [General Remarks](#general-remarks)
- [Important Remark](#important-remark)
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

<!-- TOC-END -->

## General Remarks

The tools are located in the `tools` directory of the repository
clone.

Purpose of the tools is to

* prepare the infrastructure environment for the container build

* build images from a reference SAP system

* deploy containers based on these images to Red Hat® OpenShift®
  Container Platform

* run the containers in the Red Hat OpenShift Container Platform

* manage and monitor the containers deployed to Red Hat OpenShift
  Container Platform

The tools are invoked from command line.

Containerization is supported for target platform Red Hat OpenShift
Container Platform on IBM® Power Systems™.

See the [table of contents](#contents) for a list of the tools.

## Important Remark

> :warning: **Before invoking the tools, do not forget to [activate
> the virtual Python
> environment](./PREREQUISITES.md#activating-the-virtual-environment).**

## Tool `codingstyle`

### Usage

`codingstyle [-h] [-c <config-file>] [-q <creds-file>] [-g <logfile-dir>] [-v {critical,error,warning,info,debug,notset}] [-w] [--dump-context] [-r <recursion-level>] [-f <format>] <source> [<source> ...]`

### Purpose

Check coding style of Python files

### Positional Arguments

| Argument | Description | Default |
|:---------|:------------|:--------|
|`<source>`|Names of files or directories that are to be checked|`None`|

### Optional Arguments

| Argument | Description | Default |
|:---------|:------------|:--------|
|`-h, --help`|show this help message and exit||
|`-c <config-file>, --config-file <config-file>`|Configuration file|`./config.yaml`|
|`-q <creds-file>, --creds-file <creds-file>`|Credentials file (encrypted)|`./creds.yaml.gpg`|
|`-g <logfile-dir>, --logfile-dir <logfile-dir>`|logfile directory|`./log`|
|`-v {critical,error,warning,info,debug,notset}, --loglevel {critical,error,warning,info,debug,notset}`|logging level|`warning`|
|`-w, --log-to-terminal`|Log to terminal instead of logging to file|`False`|
|`--dump-context`|Dump context (CLI arguments, configuration, credentials)|`False`|
|`-r <recursion-level>, --recursion-level <recursion-level>`|Perform recursive check up to depth &lt;recursion-level&gt; if &lt;source&gt; is a directory; (&#x27;-1&#x27;: no depth limitation)|`0`|
|`-f <format>, --format <format>`|Select output format (&#x27;text&#x27;, &#x27;html&#x27;, &#x27;empty&#x27;)|`text`|

## Tool `config`

### Usage

`config [-h] [-c <config-file>] [-q <creds-file>] [-g <logfile-dir>] [-v {critical,error,warning,info,debug,notset}] [-w] [--dump-context] [-n] [-e] [-d] [--non-interactive] [-s]`

### Purpose

Configuration management

### Optional Arguments

| Argument | Description | Default |
|:---------|:------------|:--------|
|`-h, --help`|show this help message and exit||
|`-c <config-file>, --config-file <config-file>`|Configuration file|`./config.yaml`|
|`-q <creds-file>, --creds-file <creds-file>`|Credentials file (encrypted)|`./creds.yaml.gpg`|
|`-g <logfile-dir>, --logfile-dir <logfile-dir>`|logfile directory|`./log`|
|`-v {critical,error,warning,info,debug,notset}, --loglevel {critical,error,warning,info,debug,notset}`|logging level|`warning`|
|`-w, --log-to-terminal`|Log to terminal instead of logging to file|`False`|
|`--dump-context`|Dump context (CLI arguments, configuration, credentials)|`False`|
|`-n, --new`|Create a new configuration file|`False`|
|`-e, --edit`|Change configuration in an existing configuration file|`False`|
|`-d, --dump`|Dump configuration to stdout|`False`|
|`--non-interactive`|Perform &#x27;-n&#x27; and &#x27;-e&#x27; non-interactively (reading values from environment)|`False`|
|`-s, --suppress-descriptions`|Don&#x27;t show detailed descriptions during edit|`False`|

## Tool `containerize`

### Usage

`containerize [-h] [-c <config-file>] [-q <creds-file>] [-g <logfile-dir>] [-v {critical,error,warning,info,debug,notset}] [-w] [--dump-context] [-y] [-b] [-p] [-o] [-u <overlay-uuid>] [-l] [-t] [-d] [-s] [-x] [-a] [-r]`

### Purpose

Automated build, push and deploy

### Optional Arguments

| Argument | Description | Default |
|:---------|:------------|:--------|
|`-h, --help`|show this help message and exit||
|`-c <config-file>, --config-file <config-file>`|Configuration file|`./config.yaml`|
|`-q <creds-file>, --creds-file <creds-file>`|Credentials file (encrypted)|`./creds.yaml.gpg`|
|`-g <logfile-dir>, --logfile-dir <logfile-dir>`|logfile directory|`./log`|
|`-v {critical,error,warning,info,debug,notset}, --loglevel {critical,error,warning,info,debug,notset}`|logging level|`warning`|
|`-w, --log-to-terminal`|Log to terminal instead of logging to file|`False`|
|`--dump-context`|Dump context (CLI arguments, configuration, credentials)|`False`|
|`-y, --hdb-copy`|Copy HANA DB snapshot to NFS server|`False`|
|`-b, --build-images`|Build images|`False`|
|`-p, --push-images`|Push images to local OCP cluster registry|`False`|
|`-o, --setup-overlay-share`|Setup overlay share|`False`|
|`-u <overlay-uuid>, --overlay-uuid <overlay-uuid>`|UUID of overlay share for options &#x27;-d&#x27; and &#x27;-t&#x27;|`None`|
|`-l, --list-overlay-shares`|List existing overlay shares|`False`|
|`-t, --tear-down-overlay-share`|Tear down overlay share specified with option &#x27;-u&#x27;|`False`|
|`-d, --create-deployment-file`|Create deployment file|`False`|
|`-s, --start-deployment`|Start deployment on OCP cluster|`False`|
|`-x, --stop-deployment`|Stop deployment on OCP cluster|`False`|
|`-a, --execute-all`|Execute all actions (except &#x27;-t&#x27;, &#x27;-l&#x27; and &#x27;-x&#x27;)|`False`|
|`-r, --execute-rest`|Start with specified action and execute all subsequent actions in automation process.|`False`|

## Tool `creds`

### Usage

`creds [-h] [-c <config-file>] [-q <creds-file>] [-g <logfile-dir>] [-v {critical,error,warning,info,debug,notset}] [-w] [--dump-context] [-n] [-e] [-d] [--non-interactive] [-s] [-u] [-r <recipient>]`

### Purpose

Credentials management

### Optional Arguments

| Argument | Description | Default |
|:---------|:------------|:--------|
|`-h, --help`|show this help message and exit||
|`-c <config-file>, --config-file <config-file>`|Configuration file|`./config.yaml`|
|`-q <creds-file>, --creds-file <creds-file>`|Credentials file (encrypted)|`./creds.yaml.gpg`|
|`-g <logfile-dir>, --logfile-dir <logfile-dir>`|logfile directory|`./log`|
|`-v {critical,error,warning,info,debug,notset}, --loglevel {critical,error,warning,info,debug,notset}`|logging level|`warning`|
|`-w, --log-to-terminal`|Log to terminal instead of logging to file|`False`|
|`--dump-context`|Dump context (CLI arguments, configuration, credentials)|`False`|
|`-n, --new`|Create a new credentials file|`False`|
|`-e, --edit`|Change credentials in an existing credentials file|`False`|
|`-d, --dump`|Dump credentials to stdout (DISPLAYS SECRETS IN CLEAR TEXT)|`False`|
|`--non-interactive`|Perform &#x27;-n&#x27; and &#x27;-e&#x27; non-interactively (reading values from environment)|`False`|
|`-s, --suppress-descriptions`|Don&#x27;t show detailed descriptions during edit|`False`|
|`-u, --unencrypted`|If &#x27;-n&#x27; is specified: Don&#x27;t encrypt a newly created credentials file|`False`|
|`-r <recipient>, --recipient <recipient>`|If &#x27;-n&#x27; is specified and &#x27;-u&#x27; is not specified: Owner e-mail address or key fingerprint of GPG key which will be used for encrypting a newly created credentials file. If not specified, symmetric AES256 encryption is used.|`None`|

## Tool `gpg-key-gen`

### Usage

`gpg-key-gen [-h] [-c <config-file>] [-q <creds-file>] [-g <logfile-dir>] [-v {critical,error,warning,info,debug,notset}] [-w] [--dump-context]`

### Purpose

Generate a GPG private / public key pair

### Optional Arguments

| Argument | Description | Default |
|:---------|:------------|:--------|
|`-h, --help`|show this help message and exit||
|`-c <config-file>, --config-file <config-file>`|Configuration file|`./config.yaml`|
|`-q <creds-file>, --creds-file <creds-file>`|Credentials file (encrypted)|`./creds.yaml.gpg`|
|`-g <logfile-dir>, --logfile-dir <logfile-dir>`|logfile directory|`./log`|
|`-v {critical,error,warning,info,debug,notset}, --loglevel {critical,error,warning,info,debug,notset}`|logging level|`warning`|
|`-w, --log-to-terminal`|Log to terminal instead of logging to file|`False`|
|`--dump-context`|Dump context (CLI arguments, configuration, credentials)|`False`|

## Tool `image-build`

### Usage

`image-build [-h] [-c <config-file>] [-q <creds-file>] [-g <logfile-dir>] [-v {critical,error,warning,info,debug,notset}] [-w] [--dump-context] [-f <image-flavor>] [-t <temp-root>] [-d <build-dir>] [-k]`

### Purpose

Build a container image of a given flavor

### Optional Arguments

| Argument | Description | Default |
|:---------|:------------|:--------|
|`-h, --help`|show this help message and exit||
|`-c <config-file>, --config-file <config-file>`|Configuration file|`./config.yaml`|
|`-q <creds-file>, --creds-file <creds-file>`|Credentials file (encrypted)|`./creds.yaml.gpg`|
|`-g <logfile-dir>, --logfile-dir <logfile-dir>`|logfile directory|`./log`|
|`-v {critical,error,warning,info,debug,notset}, --loglevel {critical,error,warning,info,debug,notset}`|logging level|`warning`|
|`-w, --log-to-terminal`|Log to terminal instead of logging to file|`False`|
|`--dump-context`|Dump context (CLI arguments, configuration, credentials)|`False`|
|`-f <image-flavor>, --image-flavor <image-flavor>`|Image flavor (&#x27;init&#x27;, &#x27;nws4&#x27;, &#x27;hdb&#x27;)|`init`|
|`-t <temp-root>, --temp-root <temp-root>`|Use &lt;temp-root&gt; as root for temporary files generated during build|`/data/tmp`|
|`-d <build-dir>, --build-directory <build-dir>`|Use &lt;build-dir&gt; as build directory; if not specified, a new build directory is created under &#x27;&lt;temp-root&gt;&#x27;|`None`|
|`-k, --keep-files`|Keep existing files in &lt;build-dir&gt; which were copied from &lt;host&gt; in a previous run; has no effect if &#x27;-d&#x27; is not specified|`False`|

## Tool `image-push`

### Usage

`image-push [-h] [-c <config-file>] [-q <creds-file>] [-g <logfile-dir>] [-v {critical,error,warning,info,debug,notset}] [-w] [--dump-context] [-f <image-flavor>]`

### Purpose

Push a container image of a given flavor to the internal cluster registry

### Optional Arguments

| Argument | Description | Default |
|:---------|:------------|:--------|
|`-h, --help`|show this help message and exit||
|`-c <config-file>, --config-file <config-file>`|Configuration file|`./config.yaml`|
|`-q <creds-file>, --creds-file <creds-file>`|Credentials file (encrypted)|`./creds.yaml.gpg`|
|`-g <logfile-dir>, --logfile-dir <logfile-dir>`|logfile directory|`./log`|
|`-v {critical,error,warning,info,debug,notset}, --loglevel {critical,error,warning,info,debug,notset}`|logging level|`warning`|
|`-w, --log-to-terminal`|Log to terminal instead of logging to file|`False`|
|`--dump-context`|Dump context (CLI arguments, configuration, credentials)|`False`|
|`-f <image-flavor>, --image-flavor <image-flavor>`|Image flavor (&#x27;init&#x27;, &#x27;nws4&#x27;, &#x27;hdb&#x27;)|`init`|

## Tool `nfs-hdb-copy`

### Usage

`nfs-hdb-copy [-h] [-c <config-file>] [-q <creds-file>] [-g <logfile-dir>] [-v {critical,error,warning,info,debug,notset}] [-w] [--dump-context]`

### Purpose

Copy an SAP HANA DB snapshot the NFS server

### Optional Arguments

| Argument | Description | Default |
|:---------|:------------|:--------|
|`-h, --help`|show this help message and exit||
|`-c <config-file>, --config-file <config-file>`|Configuration file|`./config.yaml`|
|`-q <creds-file>, --creds-file <creds-file>`|Credentials file (encrypted)|`./creds.yaml.gpg`|
|`-g <logfile-dir>, --logfile-dir <logfile-dir>`|logfile directory|`./log`|
|`-v {critical,error,warning,info,debug,notset}, --loglevel {critical,error,warning,info,debug,notset}`|logging level|`warning`|
|`-w, --log-to-terminal`|Log to terminal instead of logging to file|`False`|
|`--dump-context`|Dump context (CLI arguments, configuration, credentials)|`False`|

## Tool `nfs-overlay-list`

### Usage

`nfs-overlay-list [-h] [-c <config-file>] [-q <creds-file>] [-g <logfile-dir>] [-v {critical,error,warning,info,debug,notset}] [-w] [--dump-context]`

### Purpose

List availabe overlay shares on NFS server

### Optional Arguments

| Argument | Description | Default |
|:---------|:------------|:--------|
|`-h, --help`|show this help message and exit||
|`-c <config-file>, --config-file <config-file>`|Configuration file|`./config.yaml`|
|`-q <creds-file>, --creds-file <creds-file>`|Credentials file (encrypted)|`./creds.yaml.gpg`|
|`-g <logfile-dir>, --logfile-dir <logfile-dir>`|logfile directory|`./log`|
|`-v {critical,error,warning,info,debug,notset}, --loglevel {critical,error,warning,info,debug,notset}`|logging level|`warning`|
|`-w, --log-to-terminal`|Log to terminal instead of logging to file|`False`|
|`--dump-context`|Dump context (CLI arguments, configuration, credentials)|`False`|

## Tool `nfs-overlay-setup`

### Usage

`nfs-overlay-setup [-h] [-c <config-file>] [-q <creds-file>] [-g <logfile-dir>] [-v {critical,error,warning,info,debug,notset}] [-w] [--dump-context]`

### Purpose

Setup overlay file system on NFS server

### Optional Arguments

| Argument | Description | Default |
|:---------|:------------|:--------|
|`-h, --help`|show this help message and exit||
|`-c <config-file>, --config-file <config-file>`|Configuration file|`./config.yaml`|
|`-q <creds-file>, --creds-file <creds-file>`|Credentials file (encrypted)|`./creds.yaml.gpg`|
|`-g <logfile-dir>, --logfile-dir <logfile-dir>`|logfile directory|`./log`|
|`-v {critical,error,warning,info,debug,notset}, --loglevel {critical,error,warning,info,debug,notset}`|logging level|`warning`|
|`-w, --log-to-terminal`|Log to terminal instead of logging to file|`False`|
|`--dump-context`|Dump context (CLI arguments, configuration, credentials)|`False`|

## Tool `nfs-overlay-teardown`

### Usage

`nfs-overlay-teardown [-h] [-c <config-file>] [-q <creds-file>] [-g <logfile-dir>] [-v {critical,error,warning,info,debug,notset}] [-w] [--dump-context] -u <overlay-uuid>`

### Purpose

Tear down overlay file system on NFS server

### Optional Arguments

| Argument | Description | Default |
|:---------|:------------|:--------|
|`-h, --help`|show this help message and exit||
|`-c <config-file>, --config-file <config-file>`|Configuration file|`./config.yaml`|
|`-q <creds-file>, --creds-file <creds-file>`|Credentials file (encrypted)|`./creds.yaml.gpg`|
|`-g <logfile-dir>, --logfile-dir <logfile-dir>`|logfile directory|`./log`|
|`-v {critical,error,warning,info,debug,notset}, --loglevel {critical,error,warning,info,debug,notset}`|logging level|`warning`|
|`-w, --log-to-terminal`|Log to terminal instead of logging to file|`False`|
|`--dump-context`|Dump context (CLI arguments, configuration, credentials)|`False`|
|`-u <overlay-uuid>, --overlay-uuid <overlay-uuid>`|UUID of the overlay NFS share on which the HANA DB data resides|`None`|

## Tool `ocp-container-login`

### Usage

`ocp-container-login [-h] [-c <config-file>] [-q <creds-file>] [-g <logfile-dir>] [-v {critical,error,warning,info,debug,notset}] [-w] [--dump-context] [-i <container-flavor>]`

### Purpose

Interactively log into a container running in an OpenShift cluster

### Optional Arguments

| Argument | Description | Default |
|:---------|:------------|:--------|
|`-h, --help`|show this help message and exit||
|`-c <config-file>, --config-file <config-file>`|Configuration file|`./config.yaml`|
|`-q <creds-file>, --creds-file <creds-file>`|Credentials file (encrypted)|`./creds.yaml.gpg`|
|`-g <logfile-dir>, --logfile-dir <logfile-dir>`|logfile directory|`./log`|
|`-v {critical,error,warning,info,debug,notset}, --loglevel {critical,error,warning,info,debug,notset}`|logging level|`warning`|
|`-w, --log-to-terminal`|Log to terminal instead of logging to file|`False`|
|`--dump-context`|Dump context (CLI arguments, configuration, credentials)|`False`|
|`-i <container-flavor>, --container-flavor <container-flavor>`|Container flavor (&#x27;di&#x27;, &#x27;ascs&#x27;, &#x27;hdb&#x27;)|`di`|

## Tool `ocp-container-run`

### Usage

`ocp-container-run [-h] [-c <config-file>] [-q <creds-file>] [-g <logfile-dir>] [-v {critical,error,warning,info,debug,notset}] [-w] [--dump-context] [-i <container-flavor>] command`

### Purpose

Log into a container running in an OpenShift cluster

### Positional Arguments

| Argument | Description | Default |
|:---------|:------------|:--------|
|`command`|Command to be executed inside the container|`None`|

### Optional Arguments

| Argument | Description | Default |
|:---------|:------------|:--------|
|`-h, --help`|show this help message and exit||
|`-c <config-file>, --config-file <config-file>`|Configuration file|`./config.yaml`|
|`-q <creds-file>, --creds-file <creds-file>`|Credentials file (encrypted)|`./creds.yaml.gpg`|
|`-g <logfile-dir>, --logfile-dir <logfile-dir>`|logfile directory|`./log`|
|`-v {critical,error,warning,info,debug,notset}, --loglevel {critical,error,warning,info,debug,notset}`|logging level|`warning`|
|`-w, --log-to-terminal`|Log to terminal instead of logging to file|`False`|
|`--dump-context`|Dump context (CLI arguments, configuration, credentials)|`False`|
|`-i <container-flavor>, --container-flavor <container-flavor>`|Container flavor (&#x27;di&#x27;, &#x27;ascs&#x27;, &#x27;hdb&#x27;)|`di`|

## Tool `ocp-deployment-gen`

### Usage

`ocp-deployment-gen [-h] [-c <config-file>] [-q <creds-file>] [-g <logfile-dir>] [-v {critical,error,warning,info,debug,notset}] [-w] [--dump-context] -u <overlay-uuid> [-o <output-file>]`

### Purpose

Generate OpenShift deployment YAML file

### Optional Arguments

| Argument | Description | Default |
|:---------|:------------|:--------|
|`-h, --help`|show this help message and exit||
|`-c <config-file>, --config-file <config-file>`|Configuration file|`./config.yaml`|
|`-q <creds-file>, --creds-file <creds-file>`|Credentials file (encrypted)|`./creds.yaml.gpg`|
|`-g <logfile-dir>, --logfile-dir <logfile-dir>`|logfile directory|`./log`|
|`-v {critical,error,warning,info,debug,notset}, --loglevel {critical,error,warning,info,debug,notset}`|logging level|`warning`|
|`-w, --log-to-terminal`|Log to terminal instead of logging to file|`False`|
|`--dump-context`|Dump context (CLI arguments, configuration, credentials)|`False`|
|`-u <overlay-uuid>, --overlay-uuid <overlay-uuid>`|UUID of the overlay NFS share on which the HANA DB data resides|`None`|
|`-o <output-file>, --output-file <output-file>`|Path to output file|`None`|

## Tool `ocp-etc-hosts`

### Usage

`ocp-etc-hosts [-h] [-c <config-file>] [-q <creds-file>] [-g <logfile-dir>] [-v {critical,error,warning,info,debug,notset}] [-w] [--dump-context]`

### Purpose

Add OpenShift cluster domain entries to '/etc/hosts'

### Optional Arguments

| Argument | Description | Default |
|:---------|:------------|:--------|
|`-h, --help`|show this help message and exit||
|`-c <config-file>, --config-file <config-file>`|Configuration file|`./config.yaml`|
|`-q <creds-file>, --creds-file <creds-file>`|Credentials file (encrypted)|`./creds.yaml.gpg`|
|`-g <logfile-dir>, --logfile-dir <logfile-dir>`|logfile directory|`./log`|
|`-v {critical,error,warning,info,debug,notset}, --loglevel {critical,error,warning,info,debug,notset}`|logging level|`warning`|
|`-w, --log-to-terminal`|Log to terminal instead of logging to file|`False`|
|`--dump-context`|Dump context (CLI arguments, configuration, credentials)|`False`|

## Tool `ocp-hdb-secret-gen`

### Usage

`ocp-hdb-secret-gen [-h] [-c <config-file>] [-q <creds-file>] [-g <logfile-dir>] [-v {critical,error,warning,info,debug,notset}] [-w] [--dump-context]`

### Purpose

Generate OpenShift HANA secret YAML file

### Optional Arguments

| Argument | Description | Default |
|:---------|:------------|:--------|
|`-h, --help`|show this help message and exit||
|`-c <config-file>, --config-file <config-file>`|Configuration file|`./config.yaml`|
|`-q <creds-file>, --creds-file <creds-file>`|Credentials file (encrypted)|`./creds.yaml.gpg`|
|`-g <logfile-dir>, --logfile-dir <logfile-dir>`|logfile directory|`./log`|
|`-v {critical,error,warning,info,debug,notset}, --loglevel {critical,error,warning,info,debug,notset}`|logging level|`warning`|
|`-w, --log-to-terminal`|Log to terminal instead of logging to file|`False`|
|`--dump-context`|Dump context (CLI arguments, configuration, credentials)|`False`|

## Tool `ocp-login`

### Usage

`ocp-login [-h] [-c <config-file>] [-q <creds-file>] [-g <logfile-dir>] [-v {critical,error,warning,info,debug,notset}] [-w] [--dump-context] [-u] [-a]`

### Purpose

Log into OCP

### Optional Arguments

| Argument | Description | Default |
|:---------|:------------|:--------|
|`-h, --help`|show this help message and exit||
|`-c <config-file>, --config-file <config-file>`|Configuration file|`./config.yaml`|
|`-q <creds-file>, --creds-file <creds-file>`|Credentials file (encrypted)|`./creds.yaml.gpg`|
|`-g <logfile-dir>, --logfile-dir <logfile-dir>`|logfile directory|`./log`|
|`-v {critical,error,warning,info,debug,notset}, --loglevel {critical,error,warning,info,debug,notset}`|logging level|`warning`|
|`-w, --log-to-terminal`|Log to terminal instead of logging to file|`False`|
|`--dump-context`|Dump context (CLI arguments, configuration, credentials)|`False`|
|`-u, --user`|Log into OCP as regular user|`False`|
|`-a, --admin`|Log into OCP as admin user|`False`|

## Tool `ocp-pod-meminfo`

### Usage

`ocp-pod-meminfo [-h] [-c <config-file>] [-q <creds-file>] [-g <logfile-dir>] [-v {critical,error,warning,info,debug,notset}] [-w] [--dump-context] [-l] [-t <sleep-time>]`

### Purpose

Get SAP system memory consumption information

### Optional Arguments

| Argument | Description | Default |
|:---------|:------------|:--------|
|`-h, --help`|show this help message and exit||
|`-c <config-file>, --config-file <config-file>`|Configuration file|`./config.yaml`|
|`-q <creds-file>, --creds-file <creds-file>`|Credentials file (encrypted)|`./creds.yaml.gpg`|
|`-g <logfile-dir>, --logfile-dir <logfile-dir>`|logfile directory|`./log`|
|`-v {critical,error,warning,info,debug,notset}, --loglevel {critical,error,warning,info,debug,notset}`|logging level|`warning`|
|`-w, --log-to-terminal`|Log to terminal instead of logging to file|`False`|
|`--dump-context`|Dump context (CLI arguments, configuration, credentials)|`False`|
|`-l, --loop`|Print information in endless loop|`False`|
|`-t <sleep-time>, --sleep-time <sleep-time>`|Sleep time in seconds between two loop executions|`5`|

## Tool `ocp-pod-status`

### Usage

`ocp-pod-status [-h] [-c <config-file>] [-q <creds-file>] [-g <logfile-dir>] [-v {critical,error,warning,info,debug,notset}] [-w] [--dump-context]`

### Purpose

Get the status of a pod

### Optional Arguments

| Argument | Description | Default |
|:---------|:------------|:--------|
|`-h, --help`|show this help message and exit||
|`-c <config-file>, --config-file <config-file>`|Configuration file|`./config.yaml`|
|`-q <creds-file>, --creds-file <creds-file>`|Credentials file (encrypted)|`./creds.yaml.gpg`|
|`-g <logfile-dir>, --logfile-dir <logfile-dir>`|logfile directory|`./log`|
|`-v {critical,error,warning,info,debug,notset}, --loglevel {critical,error,warning,info,debug,notset}`|logging level|`warning`|
|`-w, --log-to-terminal`|Log to terminal instead of logging to file|`False`|
|`--dump-context`|Dump context (CLI arguments, configuration, credentials)|`False`|

## Tool `ocp-port-forwarding`

### Usage

`ocp-port-forwarding [-h] [-c <config-file>] [-q <creds-file>] [-g <logfile-dir>] [-v {critical,error,warning,info,debug,notset}] [-w] [--dump-context]`

### Purpose

SSH port forwarding for creating a SAP GUI connection to the containerized SAP system

### Optional Arguments

| Argument | Description | Default |
|:---------|:------------|:--------|
|`-h, --help`|show this help message and exit||
|`-c <config-file>, --config-file <config-file>`|Configuration file|`./config.yaml`|
|`-q <creds-file>, --creds-file <creds-file>`|Credentials file (encrypted)|`./creds.yaml.gpg`|
|`-g <logfile-dir>, --logfile-dir <logfile-dir>`|logfile directory|`./log`|
|`-v {critical,error,warning,info,debug,notset}, --loglevel {critical,error,warning,info,debug,notset}`|logging level|`warning`|
|`-w, --log-to-terminal`|Log to terminal instead of logging to file|`False`|
|`--dump-context`|Dump context (CLI arguments, configuration, credentials)|`False`|

## Tool `ocp-service-account-gen`

### Usage

`ocp-service-account-gen [-h] [-c <config-file>] [-q <creds-file>] [-g <logfile-dir>] [-v {critical,error,warning,info,debug,notset}] [-w] [--dump-context] [-o <output-file>]`

### Purpose

Generate YAML file for service account creation

### Optional Arguments

| Argument | Description | Default |
|:---------|:------------|:--------|
|`-h, --help`|show this help message and exit||
|`-c <config-file>, --config-file <config-file>`|Configuration file|`./config.yaml`|
|`-q <creds-file>, --creds-file <creds-file>`|Credentials file (encrypted)|`./creds.yaml.gpg`|
|`-g <logfile-dir>, --logfile-dir <logfile-dir>`|logfile directory|`./log`|
|`-v {critical,error,warning,info,debug,notset}, --loglevel {critical,error,warning,info,debug,notset}`|logging level|`warning`|
|`-w, --log-to-terminal`|Log to terminal instead of logging to file|`False`|
|`--dump-context`|Dump context (CLI arguments, configuration, credentials)|`False`|
|`-o <output-file>, --output-file <output-file>`|Path to output file|`None`|

## Tool `sap-system-status`

### Usage

`sap-system-status [-h] [-c <config-file>] [-q <creds-file>] [-g <logfile-dir>] [-v {critical,error,warning,info,debug,notset}] [-w] [--dump-context] [-l] [-t <sleep-time>] [--process-list]`

### Purpose

Get SAP system status

### Optional Arguments

| Argument | Description | Default |
|:---------|:------------|:--------|
|`-h, --help`|show this help message and exit||
|`-c <config-file>, --config-file <config-file>`|Configuration file|`./config.yaml`|
|`-q <creds-file>, --creds-file <creds-file>`|Credentials file (encrypted)|`./creds.yaml.gpg`|
|`-g <logfile-dir>, --logfile-dir <logfile-dir>`|logfile directory|`./log`|
|`-v {critical,error,warning,info,debug,notset}, --loglevel {critical,error,warning,info,debug,notset}`|logging level|`warning`|
|`-w, --log-to-terminal`|Log to terminal instead of logging to file|`False`|
|`--dump-context`|Dump context (CLI arguments, configuration, credentials)|`False`|
|`-l, --loop`|Print information in endless loop|`False`|
|`-t <sleep-time>, --sleep-time <sleep-time>`|Sleep time in seconds between two loop executions|`5`|
|`--process-list`|Print the process list for every container|`False`|

## Tool `ssh-key-gen`

### Usage

`ssh-key-gen [-h] [-c <config-file>] [-q <creds-file>] [-g <logfile-dir>] [-v {critical,error,warning,info,debug,notset}] [-w] [--dump-context] [-i <ssh-id>]`

### Purpose

Generate a passphrase-less SSH private / public key pair

### Optional Arguments

| Argument | Description | Default |
|:---------|:------------|:--------|
|`-h, --help`|show this help message and exit||
|`-c <config-file>, --config-file <config-file>`|Configuration file|`./config.yaml`|
|`-q <creds-file>, --creds-file <creds-file>`|Credentials file (encrypted)|`./creds.yaml.gpg`|
|`-g <logfile-dir>, --logfile-dir <logfile-dir>`|logfile directory|`./log`|
|`-v {critical,error,warning,info,debug,notset}, --loglevel {critical,error,warning,info,debug,notset}`|logging level|`warning`|
|`-w, --log-to-terminal`|Log to terminal instead of logging to file|`False`|
|`--dump-context`|Dump context (CLI arguments, configuration, credentials)|`False`|
|`-i <ssh-id>, --ssh-id <ssh-id>`|Path to the SSH ID private key file|`None`|

## Tool `ssh-keys`

### Usage

`ssh-keys [-h] [-c <config-file>] [-q <creds-file>] [-g <logfile-dir>] [-v {critical,error,warning,info,debug,notset}] [-w] [--dump-context] [-a] [-d] [-r] [-y]`

### Purpose

Add/remove SSH public keys to/from the various authorized_keys files

### Optional Arguments

| Argument | Description | Default |
|:---------|:------------|:--------|
|`-h, --help`|show this help message and exit||
|`-c <config-file>, --config-file <config-file>`|Configuration file|`./config.yaml`|
|`-q <creds-file>, --creds-file <creds-file>`|Credentials file (encrypted)|`./creds.yaml.gpg`|
|`-g <logfile-dir>, --logfile-dir <logfile-dir>`|logfile directory|`./log`|
|`-v {critical,error,warning,info,debug,notset}, --loglevel {critical,error,warning,info,debug,notset}`|logging level|`warning`|
|`-w, --log-to-terminal`|Log to terminal instead of logging to file|`False`|
|`--dump-context`|Dump context (CLI arguments, configuration, credentials)|`False`|
|`-a, --add-keys`|Add SSH public keys to the various authorized_keys files|`False`|
|`-d, --display-details`|Display detailed information on which keys are added/removed to the various authorized_keys files of which users|`False`|
|`-r, --remove-keys`|Remove SSH public keys from the various authorized_keys files|`False`|
|`-y, --no-confirm`|Don&#x27;t confirm adding/removing keys to/from the various authorized_keys files|`False`|

## Tool `venv-setup`

### Usage
`venv-setup`

### Purpose

Set up a Python virtual environment with all modules that are required
to run the tools.

Once the virtual environment is prepared, activate it by executing
`source venv/bin/activate` out of the repository clone root directory
before running any of the other tools.

## Tool `verify-config`

### Usage

`verify-config [-h] [-c <config-file>] [-q <creds-file>] [-g <logfile-dir>] [-v {critical,error,warning,info,debug,notset}] [-w] [--dump-context]`

### Purpose

Verify parameter settings in configuration YAML file

### Optional Arguments

| Argument | Description | Default |
|:---------|:------------|:--------|
|`-h, --help`|show this help message and exit||
|`-c <config-file>, --config-file <config-file>`|Configuration file|`./config.yaml`|
|`-q <creds-file>, --creds-file <creds-file>`|Credentials file (encrypted)|`./creds.yaml.gpg`|
|`-g <logfile-dir>, --logfile-dir <logfile-dir>`|logfile directory|`./log`|
|`-v {critical,error,warning,info,debug,notset}, --loglevel {critical,error,warning,info,debug,notset}`|logging level|`warning`|
|`-w, --log-to-terminal`|Log to terminal instead of logging to file|`False`|
|`--dump-context`|Dump context (CLI arguments, configuration, credentials)|`False`|

## Tool `verify-ocp-settings`

### Usage

`verify-ocp-settings [-h] [-c <config-file>] [-q <creds-file>] [-g <logfile-dir>] [-v {critical,error,warning,info,debug,notset}] [-w] [--dump-context]`

### Purpose

Verify OpenShift cluster setup related settings

### Optional Arguments

| Argument | Description | Default |
|:---------|:------------|:--------|
|`-h, --help`|show this help message and exit||
|`-c <config-file>, --config-file <config-file>`|Configuration file|`./config.yaml`|
|`-q <creds-file>, --creds-file <creds-file>`|Credentials file (encrypted)|`./creds.yaml.gpg`|
|`-g <logfile-dir>, --logfile-dir <logfile-dir>`|logfile directory|`./log`|
|`-v {critical,error,warning,info,debug,notset}, --loglevel {critical,error,warning,info,debug,notset}`|logging level|`warning`|
|`-w, --log-to-terminal`|Log to terminal instead of logging to file|`False`|
|`--dump-context`|Dump context (CLI arguments, configuration, credentials)|`False`|

