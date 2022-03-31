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

# Verifying and Managing the Deployments

This document describes steps for verifying and managing the
deployments of your SAP system.

<!-- TOC-START -->

## Contents

<details>
  <summary>Table of Contents</summary>

- [Important Remark](#important-remark)
- [Managing Multiple Copies of the Reference SAP System](#managing-multiple-copies-of-the-reference-sap-system)
  - [Adding Deployments](#adding-deployments)
  - [Listing Deployments](#listing-deployments)
  - [Starting Deployments](#starting-deployments)
  - [Stopping Deployments](#stopping-deployments)
  - [Removing Deployments](#removing-deployments)
- [Verifying Deployments](#verifying-deployments)
  - [Getting detailed Information about the Image Pulling Process](#getting-detailed-information-about-the-image-pulling-process)
  - [Verifying the Status of a Pod](#verifying-the-status-of-a-pod)
  - [Verifying the Status of the Containers](#verifying-the-status-of-the-containers)
  - [Checking the Memory Usage of the Containers](#checking-the-memory-usage-of-the-containers)
  - [Logging into a Container](#logging-into-a-container)
  - [Verifying the Status of the SAP System](#verifying-the-status-of-the-sap-system)
- [Managing Deployments](#managing-deployments)
  - [Preparing Connections to the SAP System](#preparing-connections-to-the-sap-system)
    - [Verifying the Status of the *NodePort* Services](#verifying-the-status-of-the-nodeport-services)
    - [Establishing Port Forwarding to the SAP System](#establishing-port-forwarding-to-the-sap-system)
      - [Establishing a Port Forwarding Tunnel to the SAP System](#establishing-a-port-forwarding-tunnel-to-the-sap-system)
      - [Configure HAProxy service running on the helper node](#configure-haproxy-service-running-on-the-helper-node)
  - [Establishing a Connection to the SAP System Using SAP GUI](#establishing-a-connection-to-the-sap-system-using-sap-gui)
  - [Establishing a Connection to the SAP System Using SAP HANA Studio](#establishing-a-connection-to-the-sap-system-using-sap-hana-studio)
  - [Enabling Additional Connections to the SAP System](#enabling-additional-connections-to-the-sap-system)

</details>

<!-- TOC-END -->

## Important Remark

> :warning: **Before invoking the tools, do not forget to [activate
> the virtual Python
> environment](./PREREQUISITES.md#activating-the-virtual-environment).**

## Managing Multiple Copies of the Reference SAP System

> :warning: Some tools perform an `oc login` as specific Red Hat OpenShift users into
> Red Hat OpenShift Container Platform, and will execute an explicit
> `oc logout` at their end. This will impact a previously existing
> `oc login` also - so please ensure that you re-login accordingly
> into Red Hat OpenShift before attempting to issue any OC CLI commands.

After executing one of the steps described in documentation 
- [*Building Images and Starting Deployments from the Command
  Line*](./BUILDING-CLI.md)

- [*Building Images and Starting Deployments with Red Hat®
  Ansible®*](./ANSIBLE.md)

or 

- [*Building images and starting deployments with Red Hat® Ansible
  Tower®*](./ANSIBLE-TOWER.md)

you are ready to run one copy of your reference SAP system. 

A copy of your reference SAP system is identified by a unique ID 
<uuid>. This <uuid> is used for
- database overlay share on the NFS server
  `<ocp-user-name>-<ocp-project-name>-<hdb-host>-<hdb-sid>-<uuid>`
- deployment description file name
  `soos-<nws4-sid>-<uuid>-deployment.yaml`
- application name defined in the deployment description
  `soos-<nws4-sid>-<uuid>`

To manage multiple copies of your reference SAP system you can use 
```shell
$ tools/ocp-deployment --add [--number <number-of-deployments>]
$ tools/ocp-deployment --list
$ tools/ocp-deployment --start [--app-name <application-name>]
$ tools/ocp-deployment --stop [--app-name <application-name>]
$ tools/ocp-deployment --remove --app-name <application-name>
```
where `<application-name>` can be either
- a full application-name or
- a unique part of it

If omitted, the command checks if only one valid `application-name` 
exists: 
- In case of `--start`: a not deployed copy 
- In case of `--stop`: a deployed copy 

If you want to remove a copy using the `--remove` option, the 
`--app-name` argument is required.


### Adding Deployments

You can add one or more copies of your reference SAP system by running
```shell
$ tools/ocp-deployment --add [-n <number-of-deployments>]
```

If you omit the argument, one additional copy is created. 

The command creates 
- a new database overlay share on the NFS server
- a deployment description file
and 
- starts the SAP system on the cluster

### Listing Deployments

You can get a list all copies of your reference SAP system by running
```shell
$ tools/ocp-deployment --list
```

The output should look like
```shell
Status       App-Name                   OverlayUuid
==========================================================================================================
Running      soos-<nws4-sid>-p8doqtyu8r <ocp-user-name>-<ocp-project-name>-<hdb-host>-<hdb-sid>-p8doqtyu8r
Pending      soos-<nws4-sid>-avg2clisy6 <ocp-user-name>-<ocp-project-name>-<hdb-host>-<hdb-sid>-avg2clisy6
Pending      soos-<nws4-sid>-15fau5ujlh <ocp-user-name>-<ocp-project-name>-<hdb-host>-<hdb-sid>-15fau5ujlh
Pending      soos-<nws4-sid>-pqju49bl81 <ocp-user-name>-<ocp-project-name>-<hdb-host>-<hdb-sid>-pqju49bl81
Prepared     soos-<nws4-sid>-r1k0tq6dr4 <ocp-user-name>-<ocp-project-name>-<hdb-host>-<hdb-sid>-r1k0tq6dr4
```

Description of the *Status*:
- The *Status* shows the status as shown using `tools/ocp-pod-status`.
  For more information about the specific meaning of a status see [Red Hat® OpenShift®
   documentation](https://docs.openshift.com/container-platform/4.8/support/troubleshooting/investigating-pod-issues.html)

- *Prepared* 

  there exists a deployment description file for this specific copy. It can be started
  as described in chapter 
  [Starting 
  Deployments](#starting-deployments).
  The deployment description files must be located in the root directory of your local repository 
  clone on your build machine. They must have the format `soos-<nws4-sid>-<uuid>-deployment.yaml`.

### Starting Deployments

Deployments which are shown as *Prepared* in the output of `tools/ocp-deployment --list` can be
started using
```shell
$ tools/ocp-deployment --start [--app-name <application-name>]
```
where `<application-name>` can be either 
- a unique part of the deployment application name
- or the whole deployment application name

If you omit the `--app-name <application-name>` and only one *Prepared* copy is found, this 
specific one is started. 

### Stopping Deployments

Copies of your reference SAP system which are already deployed can be stopped using
```shell
$ tools/ocp-deployment --stop [--app-name <application-name>]
```
where `<application-name>` can be either 
- a unique part of the deployment application name
- or the whole deployment application name

If you omit the `--app-name <application-name>` and only one deployed copy is found, this 
specific one is stopped. 

### Removing Deployments

You can completely remove one copy of your reference SAP system by running
```shell
$ tools/ocp-deployment --remove --app-name <application-name>
```
where `<application-name>` can be either 
- a unique part of the deployment application name
- or the whole deployment application name

The command 
- stops the copy of the reference SAP system
- tears down the database overlay share on the NFS server 
- deletes the deployment description file

## Verifying Deployments

### Getting detailed Information about the Image Pulling Process

The first time you are deploying a copy of your reference SAP system it may
take a while to start this copy.  

If your pod is in `PodInitializing` state, the images are copied
to the local registry of the worker node on which your copy is about
to be started. This may take a while.

You can check the status of your pod as described in
[Verifying the Status of a Pod](#verifying-the-status-of-a-pod)

To get detailed information about the status of the image pulling
process issue

```shell
$ oc describe pod soos-<nws4-sid>-<uuid> | grep -i pull
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

> :warning: **When the images were already copied to the local registry 
> you will not see any output.**

### Verifying the Status of a Pod

You can verify that a pod is started by issuing

```shell
$ tools/ocp-pod-status --app-name <application-name>
```

where `<application-name>` can be either 
- a unique part of the deployment application name
- or the whole deployment application name

The output should look like
```shell
Pod                                          Status
----------------------------------------------------
soos-<nws4-sid>-<uuid>-845bbff4f-zq2fz       Running
```

If you omit the `--app-name <application-name>` argument, all deployed 
copies of your reference SAP system are shown.

Status shown: 

- `Running`: The pod is up and running 

- `PodInitializing`: When the deployment is started for the first time
  after pushing the images to the local cluster, the images must first
  be copied to the local registry of the worker node, on which the
  deployment is about to start. This process may take several
  minutes. You can check the status of the image pulling process using
  the `oc describe` command as described in section [*Getting detailed
  Information about the Image Pulling
  Process*](#getting-detailed-information-about-the-image-pulling-process).

- `undefined`: The status of the pod could not be discovered.

- all others: See the [Red Hat® OpenShift®
  documentation](https://docs.openshift.com/container-platform/4.8/support/troubleshooting/investigating-pod-issues.html)


### Verifying the Status of the Containers

If you want to get information about the status of the containers,
issue the following command - note that you must specify the
<nws4-sid> in **lowercase** characters:

```shell
nws4sid='<nws4-sid>' && \
uuid='<uuid>' && \
podname=$(oc get pods --selector="app=soos-${nws4sid}-${uuid}" -o template --template "{{range .items}}{{.metadata.name}}{{end}}") && \
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
tools/ocp-pod-meminfo --app-name <application-name>
```

where `<application-name>` can be either 
- a unique part of the deployment application name
- or the whole deployment application name

You get information about the memory used, the *limits* set and the
percentage used:

```shell
             Used Limit   Used
Container     GiB   GiB      %
==============================
Deployment <application-name>
------------------------------
ASCS        7.579  10.0  75.79
DI          8.882  12.0  74.02
HDB        80.341  92.0  87.33
```

If you omit the `--app-name <application-name>` argument, the memory of
all deployed copies of your reference SAP system are shown.

### Logging into a Container

You can easily log into a container of your running SAP system by
using the command:

```shell
tools/ocp-container-login -i <container-flavor> --app-name <application-name>
```

where `<container-flavor>` is one of the following: 

- `di`: Default, Dialog instance container 
- `ascs`: ASCS container 
- `hdb`: SAP HANA® DB Container 

and `<application-name>` is either
- a unique part of the deployment application name
- or the whole deployment application name

If only one deployed copy of your reference SAP system exists, you can omit the 
`--app-name <application-name>`option.

### Verifying the Status of the SAP System

You can check the status of the SAP system processes in your pod by
issuing:

```shell
tools/sap-system-status --process-list --app-name <application-name>
```

```shell
Deployment <application-name>
======================================== ASCS ========================================
Name                 Description          Status       Started              Elapsed
msg_server           MessageServer        Running      2022-02-04 15:53:37  95:03:03
enq_server           Enqueue Server 2     Running      2022-02-04 15:53:37  95:03:03
======================================== DI   ========================================
Name                 Description          Status       Started              Elapsed
disp+work            Dispatcher           Running      2022-02-04 15:54:52  95:01:49
igswd_mt             IGS Watchdog         Running      2022-02-04 15:54:52  95:01:49
gwrd                 Gateway              Running      2022-02-04 15:54:53  95:01:48
icman                ICM                  Running      2022-02-04 15:54:53  95:01:48
======================================== HDB  ========================================
Name                 Description          Status       Started              Elapsed
hdbdaemon            HDB Daemon           Running      2022-02-04 15:53:52  95:02:49
hdbcompileserver     HDB Compileserver    Running      2022-02-04 15:54:00  95:02:41
hdbdiserver          HDB Deployment Infra Running      2022-02-04 15:55:17  95:01:24
hdbdocstore          HDB DocStore-S4D     Running      2022-02-04 15:54:01  95:02:40
hdbdpserver          HDB DPserver-S4D     Running      2022-02-04 15:54:01  95:02:40
hdbindexserver       HDB Indexserver-S4D  Running      2022-02-04 15:54:01  95:02:40
hdbnameserver        HDB Nameserver       Running      2022-02-04 15:53:52  95:02:49
hdbpreprocessor      HDB Preprocessor     Running      2022-02-04 15:54:00  95:02:41
hdbwebdispatcher     HDB Web Dispatcher   Running      2022-02-04 15:55:17  95:01:24
hdbxsengine          HDB XSEngine-S4D     Running      2022-02-04 15:54:01  95:02:40
```

If you omit the `--process-list` option you will get the summarized
information for the different SAP instances:

```shell
Instance   Status
====================================
Deployment <application-name>
------------------------------------
ASCS       running
DI         running
HDB        running
```

If you do not specify the `--app-name <application-name>`argument, the SAP system status
of all running SAP systems are shown. If specified the `--process-list` argument is 
ignored.

## Managing Deployments

 
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
$ oc get service/soos-<nws4-sid>-<uuid>-np
NAME                        TYPE       CLUSTER-IP       EXTERNAL-IP   PORT(S)                              AGE
soos-<nws4-sid>-<uuid>-np   NodePort   172.30.187.181   <none>        32<nws4-di-instno>:<node-port>/TCP   9m9s
```

#### Establishing Port Forwarding to the SAP System
See also [*Introducing Options for End-User GUI Access to the Containerized Systems*](./PORTFORWARD.md#introducing-options-for-end-user-gui-access-to-the-containerized-systems).

Two tools are available to enable connectivity for end user
GUI access to the SAP System running in the Red Hat OpenShift
cluster. To enable establishing a connection to the SAP system
run one out of the following two tools on the build LPAR:

##### Establishing a Port Forwarding Tunnel to the SAP System

Start

```shell
tools/ocp-port-forwarding [--app-name <application-name>]
```

where `<application-name>` is either

- a unique part of the deployment application name
- or the whole deployment application name

If omitted and only one running copy of your reference SAP system exists,
port forwarding is established to this specific one.

OpenSSH communication to the pod on which the SAP system is running gets established.
**Listen socket(s)** are opened on the build LPAR for connection with SAP GUI / SAP HANA clients.
The client communication gets forwarded through SSH tunnel(s) via the helper node to the NodePorts.

:warning: To ensure that SAP GUI / SAP HANA client communication is accepted on the build LPAR either

- Ensure that `firewalld` is inactive on the build LPAR

 ```
 systemctl status firewalld
 ● firewalld.service - firewalld - dynamic firewall daemon
 Loaded: loaded (/usr/lib/systemd/system/firewalld.service; disabled; vendor preset: enabled)
 Active: inactive (dead)
 Docs: man:firewalld(1)
 ```
or

- Ensure that all ports in scope are allowed by the firewall configuration

##### Configure HAProxy service running on the helper node

Start
```shell
tools/ocp-haproxy-forwarding --add [--app-name <application-name>]
```

where `<application-name>` is either
- a unique part of the deployment application name
- or the whole deployment application name
If omitted and only one running copy of your reference SAP system exists, the port 
forwarding is established to this specific one.

The command updates the configuration of the HAProxy service
running on the helper node. New rules are added to forward to
the exposed NodePorts to the pod on which the SAP system is running.

Both tools will display both the **SAP GUI
connection** and the **SAP HANA Studio connection** parameters:

```shell
Establishing port forwarding to SAP system '<nws4-sid>' in cluster '<cluster-domain-name>'
  to SAP system '<nws4-sid>'
  in cluster '<cluster-domain-name>'
  for deployment '<application-name>'

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
  instance number of the Dialog instance of your reference SAP system. It
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
Interface (SAP GUI) use the parameters emitted by
`tools/ocp-port-forwarding` shown in the **SAP GUI connection**
section.

Specify these parameters in the *Create New System Entry* section of
the SAP GUI as *System Connection Parameters*.

### Establishing a Connection to the SAP System Using SAP HANA Studio

Define a **SAP HANA Studio connection** using the above parameters and
connect to your SAP HANA database.

:warning: The connection setup assumes that port `3<NN>15` is 
used as default SQL/MDX port to connect to the tenant database. 
In case another port, e.g. port `3<NN>41`, is used for the connection,
then the setup needs to be adjusted. See also
[Enabling Additional Connections to the SAP System](#enabling-additional-connections-to-the-sap-system)
on how to enable further additional ports for communication. 

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

The standard deployment description enables all *NodePorts* which are
required for establishing a SAP GUI connection and a SAP HANA Studio
connection to the SAP system containers.

For additional connections to SAP HANA, please see chapter
**Connections from Database Clients and Web Clients to SAP HANA**
in the **SAP HANA Administration Guide for SAP HANA platform** (part of
**SAP HANA Platform** product documentation) for details on ports used.

In case you like to expose additional ports of the SAP Dialog
instance or SAP HANA database via OpenShift *NodePorts*, and establish
port forwarding to the service definition then use following naming 
convention for the *NodePort* name:

- The name needs to start either with '**di-**' (if the *NodePort*
  relates to the Dialog instance) or '**hdb-**' (if the *NodePort*
  relates to the SAP HANA database).

- Add the port pattern to the name. The port pattern is a placeholder
  for the TCP port of the tunnel where '**xx**' will be replaced by an
  instance number.

  Example: **hdb-5xx41**

  ```shell
  spec:
      type: NodePort
      ports:
           -name: hdb-5xx41
            port: 5{{HDB_INSTNO}}41
            targetPort: 5{{HDB_INSTNO}}41
            protocol: TCP
  ```
 
  Either add the additional port to the template
  [openshift/service-nodeport.yaml.template](../openshift/service-nodeport.yaml.template)
  before the container deployment, or use the `oc` CLI to edit the
  service definition and add the additional *NodePorts*.

During start, `tools/ocp-port-forwarding` scans through the
entries of service *soos-<nws4-sid>-np* and creates an SSH tunnel
from the helper node to the pod for each *NodePort* matching the port
pattern.
