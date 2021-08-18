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

# Verifying and Managing the Deployment

This document describes steps for verifying and managing the
deployment of your SAP system.

<!-- TOC-START -->

## Contents

<details>
  <summary>Table of Contents</summary>

- [Important Remark](#important-remark)
- [Verifying the Deployment](#verifying-the-deployment)
  - [Verifying the Status of the Pod](#verifying-the-status-of-the-pod)
  - [Getting detailed Information about the Image Pulling Process](#getting-detailed-information-about-the-image-pulling-process)
  - [Verifying the Status of the Containers](#verifying-the-status-of-the-containers)
  - [Checking the Memory Usage of the Containers](#checking-the-memory-usage-of-the-containers)
  - [Logging into a Container](#logging-into-a-container)
  - [Verifying the Status of the SAP System](#verifying-the-status-of-the-sap-system)
- [Managing your Deployment](#managing-your-deployment)
  - [Preparing Connections to the SAP System](#preparing-connections-to-the-sap-system)
    - [Verifying the Status of the *NodePort* Services](#verifying-the-status-of-the-nodeport-services)
    - [Establishing a Port Forwarding Tunnel to the SAP System](#establishing-a-port-forwarding-tunnel-to-the-sap-system)
  - [Establishing a Connection to the SAP System Using SAP GUI](#establishing-a-connection-to-the-sap-system-using-sap-gui)
  - [Establishing a Connection to the SAP System Using SAP HANA Studio](#establishing-a-connection-to-the-sap-system-using-sap-hana-studio)
  - [Enabling Additional Connections to the SAP System](#enabling-additional-connections-to-the-sap-system)

</details>

<!-- TOC-END -->

## Important Remark

> :warning: **Before invoking the tools, do not forget to [activate
> the virtual Python
> environment](./PREREQUISITES.md#activating-the-virtual-environment).**

## Verifying the Deployment 

### Verifying the Status of the Pod

You can verify that the pod is started by issuing

```shell
$ tools/ocp-pod-status
```

The output should look like
```shell
Status of pod 'soos-nw7-dc7c96ffd-fdl6z': Running
```

Status shown: 

- `Running`: The pod is up and running 

- `PodInitializing`: When the deployment is started for the first time
  after pushing the images to the local cluster, the images must first
  be copied to the local registry of the worker node, on which the
  deployment is about to start. This process may take several
  minutes. You can check the status of the image pulling process using
  the `oc describe` command as described below [Getting detailed
  Information about the Image Pulling
  Process](#getting-detailed-information-about-the-image-pulling-process).

- `undefined`: The status of the pod could not be discovered.

- all others: See the [Red Hat® OpenShift®
  documentation](https://docs.openshift.com/container-platform/4.8/support/troubleshooting/investigating-pod-issues.html)

### Getting detailed Information about the Image Pulling Process

You can get detailed information about the status of the image pulling
process by issuing

```shell
$ oc describe pod soos-<nws4-sid> | grep -i pull
```

The output of the command shows lines containing messages

```shell
⋮
… Pulling image "image-registry.openshift-image-registry.svc:5000/<ocp-project-name>/soos-init"
⋮
… Pulling image "image-registry.openshift-image-registry.svc:5000/<ocp-project-name>/soos-<hdb-sid>"
⋮
… Pulling image "image-registry.openshift-image-registry.svc:5000/<ocp-project-name>/soos-<nws4-sid>"
⋮
```

Only when the status of all images looks like

```shell
… Successfully pulled image "<image-name>"
```

they were successfully copied to the worker node. The image pulling
process is then finished and the pod will start.

### Verifying the Status of the Containers

If you want to get information about the status of the containers,
issue the following command - note that you must specify the
<nws4-sid> in **lowercase** characters:

```shell
nws4sid='<nws4-sid>' && \
podname=$(oc get pods --selector="app=soos-${nws4sid}" -o template --template "{{range .items}}{{.metadata.name}}{{end}}") && \
oc get pod ${podname} -o template --template '{{range .status.containerStatuses}}{{.name}} {{.started}}{{"\n"}}{{end}}'
```

The command shows *true* for the container if it is started:

```shell
soos-<hdb-sid> true
soos-<nws4-sid>-ascs true
soos-<nws4-sid>-di true
```

### Checking the Memory Usage of the Containers

If you want to get information about the memory usage of the
containers, issue the following command:

```shell
tools/ocp-pod-meminfo
```

You get information about the memory used, the *limits* set and the
percentage used:

```shell
--------------------2021-08-11 11:24:48 (CEST)--------------------
             Used Limit   Used
Container     GiB   GiB      %
------------------------------
ASCS        4.003  10.0  40.03
DI          6.036  25.0  24.14
HDB        16.229  24.0  67.62
```

### Logging into a Container

You can easily log into a container of your running SAP system by
using the command:

```shell
tools/ocp-container-login -i <container-flavor>
```

where `<container-flavor>` is one of the following: 

- `di`: Default, Dialog instance container 
- `ascs`: ASCS container 
- `hdb`: SAP HANA® DB Container 

### Verifying the Status of the SAP System

You can check the status of the SAP system processes in your pod by
issuing:

```shell
tools/sap-system-status --process-list
```

```shell
--------------------2021-08-11 11:20:43 (CEST)--------------------
======================================== ASCS ========================================
Name                 Description          Status       Started              Elapsed
msg_server           MessageServer        Running      2021-08-09 10:43:06  48:37:40
enserver             EnqueueServer        Running      2021-08-09 10:43:06  48:37:40
======================================== DI   ========================================
Name                 Description          Status       Started              Elapsed
disp+work            Dispatcher           Running      2021-08-09 10:44:58  48:35:49
igswd_mt             IGS Watchdog         Running      2021-08-09 10:44:58  48:35:49
gwrd                 Gateway              Running      2021-08-09 10:44:59  48:35:48
icman                ICM                  Running      2021-08-09 10:44:59  48:35:48
======================================== HDB  ========================================
Name                 Description          Status       Started              Elapsed
hdbdaemon            HDB Daemon           Running      2021-08-09 10:43:07  48:37:42
hdbcompileserver     HDB Compileserver    Running      2021-08-09 10:43:19  48:37:30
hdbindexserver       HDB Indexserver-HA2  Running      2021-08-09 10:43:20  48:37:29
hdbnameserver        HDB Nameserver       Running      2021-08-09 10:43:07  48:37:42
hdbpreprocessor      HDB Preprocessor     Running      2021-08-09 10:43:19  48:37:30
hdbwebdispatcher     HDB Web Dispatcher   Running      2021-08-09 10:44:52  48:35:57
hdbxsengine          HDB XSEngine-HA2     Running      2021-08-09 10:43:20  48:37:29
```

If you omit the `--process-list` option you will get the summarized
information for the different SAP instances:

```shell
--------------------2021-08-11 11:13:29 (CEST)--------------------
Instance  Status
-----------------------------------
ASCS      running
DI        running
HDB       running
```

## Managing your Deployment 
 
### Preparing Connections to the SAP System

The sockets listening for SAPGUI and hdbsql communication in the SAP
**di** and **hdb** containers are not accessible directly from outside
of the Red Hat OpenShift cluster, but are exposed via Red Hat
Openshift *NodePorts*. However, the *NodePorts* cannot match port
range(s) as expected from SAPGUI and SAP HANA Studio®
clients. Therefore SSH port forwarding tunnels can be established via
the helper node.

#### Verifying the Status of the *NodePort* Services

To verify whether the cluster service(s) of type *NodePort* were
correctly started run the following command on the build LPAR:

```shell
$ oc get service/soos-<nws4-sid>-np
 TYPE       CLUSTER-IP       EXTERNAL-IP   PORT(S)                              AGE
soos-<nws4-sid>-np   NodePort   172.30.187.181   <none>        32<nws4-di-instno>:<node-port>/TCP   9m9s
```

#### Establishing a Port Forwarding Tunnel to the SAP System

To enable establishing a connection to the SAP system run the
following command on the build LPAR:

```shell
tools/ocp-port-forwarding
```

The command establishes SSH tunnel(s) from the helper node to the pod
on which the SAP system is running. It displays both the **SAP GUI
connection** and the **SAP HANA Studio connection** parameters:

```shell
Establishing port forwarding to SAP system '<nws4-sid>' in cluster '<cluster-domain-name>'

Use the following parameters to create a SAP GUI connection:

----------------------------------------
   System ID           <nws4-sid>
   Instance Number     <Instance No. of Dialog Instance>
   Application Server  <build-LPAR>
----------------------------------------

Use the following parameters to create a HANA Studio connection:

----------------------------------------
   Host Name           <build-LPAR>
   Instance Number     <Instance No. of HDB Instance>
   System ID           <hdb-sid>
----------------------------------------
...............................................................
To connect to the tenant DB with SAP HANA Studio it is required
to set a new entry in the SAP HANA DB parameter global.ini file
In section public_hostname_resolution:
    - Ensure Key: use_default_route has  value ip (default)
    - Add    Key: map_<build-LPAR>    with value <ip>
Use scope System for the parameter change
...............................................................
```

Description of the output parameters:

- `<nws4-sid>` is the SAP system ID of your SAP NetWeaver system

- `<Instance No. of Dialog Instance>` in general corresponds to the
  instance number of the dialog instance of your reference system. It
  may differ if the required port on the build LPAR is already in use
  by another application.

- `<build-LPAR>` is the name of your build LPAR.

- `<Instance No. of HDB Instance>` in general corresponds to the
  instance number of the SAP HANA Database instance of your reference
  system. It may differ if the required port on the build LPAR is
  already in use by another application.

- `<hdb-sid>` is the SAP system ID of your SAP HANA database system


### Establishing a Connection to the SAP System Using SAP GUI

If you want to connect to your SAP system using the SAP Graphical User
Interface (SAP GUI) you can use the parameters emitted by
`tools/ocp-port-forwarding` shown in the **SAP GUI connection**
section.

Specify these parameters in the *Create New System Entry* section of
the SAP GUI as *System Connection Parameters*.

### Establishing a Connection to the SAP System Using SAP HANA Studio

Define a **SAP HANA Studio connection** using the above parameters and
connect to your SAP HANA database:

  - Connection to the SAP HANA **SYSTEM DB** with **SAP HANA Studio**
    will work without additional customization

  - To connect to the **tenant DB** with **SAP HANA Studio**
    additional settings in the SAP HANA DB parameter file
    **global.ini** are required:

    - In section **public_hostname_resolution** ensure that

        Key **use_default_route** has value **ip**

        Add Key **mapHdbHost** with value **\<IP address of the helper node\>**

    Use scope **System** for the parameter change
	
See section [*Connecting to the SAP® S/4HANA® Database using SAP HANA
Studio®*](HOWTO.md#connecting-to-the-sap-s4hana-database-using-sap-hana-studio)
for detailed information on how to establishing a connection to the
SAP system using SAP HANA Studio.

### Enabling Additional Connections to the SAP System

Our standard deployment description enables all *NodePorts* which are
required for establishing a SAP GUI connection and a SAP HANA Studio
connection to the SAP system containers.

In case you would like to expose additional ports of the SAP dialog
instance or SAP HANA database via OpenShift *NodePorts* and the SSH
tunnel add additional *NodePort(s)* to the service definition using
the following convention for the *NodePort* name:

- The name needs to start either with '**di-**' (if the *NodePort*
  relates to the dialog instance) or '**hdb-**' (if the *NodePort*
  relates to the SAP HANA database).

- Add the port pattern to the name. The port pattern is a placeholder
  for the TCP port of the tunnel where '**xx**' will be replaced by an
  instance number.

  Example: **hdb-5xx13**

  ```shell
  spec:
      type: NodePort
      ports:
           -name: hdb-5xx13
            port: 5{{HDB_INSTNO}}13
            targetPort: 5{{HDB_INSTNO}}13
            protocol: TCP
  ```
 
  Either add the additional port to the template
  [openshift/service-nodeport.yaml.template](../openshift/service-nodeport.yaml.template)
  before the container deployment, or use the `oc` CLI to edit the
  service definition to add the additional *NodePorts*.

During start, `tools/ocp-port-forwarding` will scan through the
entries of service *soos-<nws4-sid>-np* and will create an SSH tunnel
from the helper node to the pod for each *NodePort* matching the port
pattern.
