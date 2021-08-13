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
 
# Customer Scenarios

## Contents

<details>
  <summary>Table of Contents</summary>

- [Supported Reference SAP® Systems for Containerization](#supported-reference-sap-systems-for-containerization)
- [Supported OS Distributions](#supported-os-distributions)
- [What is an SAP Instance?](#what-is-an-sap-instance)
- [What is a Reference SAP System?](#what-is-a-reference-sap-system)

</details>

## Supported Reference SAP® Systems for Containerization

Containerization of the [reference SAP
system](#what-is-a-reference-sap-system) was developed and tested
with the following scope of scenarios:

* Standard system (former "Central System")

  In a standard SAP system, all main [SAP
  instances](#what-is-an-sap-instance) run on a single host. All the
  SAP system instances from the *Primary Application Server* and *ABAP Central
  Services* reside on the same host as the SAP HANA® database.

* Distributed System

  In a distributed system, the SAP instances can run on multiple
  hosts:

  * one host running the *ABAP Central Services* instance (ASCS) and the
    *Primary Application Server* instance (PAS),

  * one host running the *SAP HANA® DB* instance

- SAP system installed with virtual hostnames
  
  The SAP instance installation is not bound to the physical hostname
  of the host, but references to an additional IP label (virtual
  hostname). The virtual hostname either has an own unique IP address,
  or is realized as IP alias (DNS CNAME). All virtual hostnames need
  to be resolvable on all hosts attempting to communicate with them -
  either via DNS entries, or via local resolution.

  The containerization was tested for a SAP system installed with
  virtual hostnames using

  * one IP alias name for the SAP HANA database,
  * one IP alias name for both *ASCS* instance and *PAS* instance.

## Supported OS Distributions

Reference SAP systems installed on 

* RHEL 8.2 (or higher)
* SLES 12 SP4 (or higher), and SLES15 SP1 (or higher)

can be used for containerization.

## What is an SAP Instance?

An SAP instance is a group of processes that are started and stopped
at the same time. Those instances can be deployed with certain
variants.

## What is a Reference SAP System?

The reference SAP system is the source system for containerization. It
consists out of the following main SAP instances:

* *ABAP Central Services* instance (ASCS instance)
* *Primary Application Server* instance (DI instance aka PAS instance)
* *SAP HANA Database* instance (HDB instance)
