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
  ------------------------------------------------------------------------
-->

# Containerization by IBM for SAP S/4HANA with Red Hat OpenShift

[![License](https://img.shields.io/badge/License-Apache2-blue.svg)](https://www.apache.org/licenses/LICENSE-2.0)
[![CLA assistant](https://cla-assistant.io/readme/badge/IBM/containerization-for-sap-s4hana)](https://cla-assistant.io/IBM/containerization-for-sap-s4hana)

Build container images from existing SAP® NetWeaver® and SAP® S/4HANA®
systems deployed on Linux®, and run them on a Red Hat® OpenShift®
cluster. Options for the build process allow to invoke it either from
command line, or automated using Red Hat Ansible® or Red Hat Ansible
Tower®.

## Contents

<details>
  <summary>Table of Contents</summary>

- [Introduction](#introduction)
- [Important note](#important-note)
- [Documentation](#documentation)
- [Contributors](#contributors)
- [License](#license)
- [Acknowledgments](#acknowledgments)

</details>

## Introduction

This project provides assets for building container images of existing
SAP® systems and for deploying containers based on the created images
in Red Hat® OpenShift® Container Platform running on IBM® Power
Systems™.

## Important note

**This is a beta release and targets for test and other non-production
landscapes. The created deliverables are not supported by SAP nor
agreed to a roadmap for official support in current state (see also
SAP Note 1122387 - *Linux: SAP Support in virtualized environments*)**

## Documentation

The various aspects of this project are described in the following
documents:

- [*Architecture*](docs/ARCHITECTURE.md)

- [*Customer Scenarios*](docs/SCENARIOS.md)

- [*Quickstart*](docs/QUICKSTART.md)

- [*Prerequisites*](docs/PREREQUISITES.md)

- Build and deployment options

  - [*Building Images and Starting Deployments from the Command
    Line*](docs/BUILDING-CLI.md)
	
	In addition, see [*Overview of the Tools*](docs/TOOLS.md) about the
    available tools and their options.

  - [*Building Images and Starting Deployments with Red Hat®
    Ansible®*](docs/ANSIBLE.md)

  - [*Building images and starting deployments with Red Hat® Ansible
    Tower®*](docs/ANSIBLE-TOWER.md)

- [*Verifying and Managing the Deployment*](docs/VERIFYING-MANAGING.md)

- [*Appendix*](docs/APPENDIX.md)

- Please refer also to this [IBM®
  Redpaper™](http://www.redbooks.ibm.com/Redbooks.nsf/RedpieceAbstracts/redp5619.html?Open)
  for more information on how to setup the required environment.

## Contributors

See the list of
[contributors](https://github.com/IBM/containerization-for-sap-s4hana/graphs/contributors)
who participated in this project.

## License

This project is licensed under the Apache 2 License - see the
[LICENSE](LICENSE) file for details.

## Acknowledgments

Thanks to all the people who contributed to all the amazing open
source tools that made this project possible.
