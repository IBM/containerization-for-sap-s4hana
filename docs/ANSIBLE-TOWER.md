<!--
  ------------------------------------------------------------------------
  Copyright 2020, 2022 IBM Corp. All Rights Reserved.

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

# Building Images and Starting Deployments with Red Hat® Ansible Tower®

In the following we describe how to build the images and deploy
containers based on the images for running an SAP® system in a Red
Hat® OpenShift® Container Platform using Red Hat Ansible Tower.

<!-- TOC-START -->

## Contents

<details>
  <summary>Table of Contents</summary>

- [Getting Started with Red Hat Ansible Tower](#getting-started-with-red-hat-ansible-tower)
- [Performing Manual Tasks](#performing-manual-tasks)
- [Creating a New Red Hat Ansible Tower Project](#creating-a-new-red-hat-ansible-tower-project)
- [Creating the Inventory](#creating-the-inventory)
- [Creating the Job Template](#creating-the-job-template)
- [Building the Images and Starting the SAP System](#building-the-images-and-starting-the-sap-system)
- [Connecting to the Deployed SAP System](#connecting-to-the-deployed-sap-system)

</details>

<!-- TOC-END -->

## Getting Started with Red Hat Ansible Tower


In the following we assume that you have installed and configured Red
Hat Ansible Tower on your build LPAR.

The basic installation of Ansible Tower is described in the [Ansible
Automation Platform Quick Installation
Guide](https://docs.ansible.com/ansible-tower/latest/html/quickinstall/index.html).

More detailed information is available in the [Ansible Automation
Platform Installation and Reference
Guide](https://docs.ansible.com/ansible-tower/3.8.0/html/installandreference/index.html#ir-start).

## Performing Manual Tasks

The tasks that need to be performed manually are described in section
[*Performing manual tasks before running the
playbook*](ANSIBLE.md#performing-manual-tasks-before-running-the-playbook).

## Creating a New Red Hat Ansible Tower Project

You need to set up a project that will be used in a job template for
building and deploying images.

To define a new project, log into the Red Hat Ansible Tower web
interface using *admin-level* credentials. Select *Projects* in the left
navigation bar and click a green plus-button in the right top
corner. You will get a new project view in which you need to fill in
all required fields:

   + Define a project name.
   + Add a description.
   + Select organization - as an example `Default` can be used.
   + Select `Git` as __SCM TYPE__.
   + Specify __SCM BRANCH/TAG/COMMIT__ to checkout source code, as example `main` can be defined.
   + Select __SCM UPDATE OPTIONS__ check boxes such as `clean`, `delete on update` and `update revision on launch`.

You do not need credentials to access our GitHub repository since the
provided URL is public - just copy it into the field __SCM URL__ of the
*Projects* template as shown:

__SCM URL__: `https://github.com/IBM/containerization-for-sap-s4hana.git`

![New Project view](images/ansible_tower_projects_view.png)

## Creating the Inventory

Before creating a job template you need to set up your inventory
defining the build host and credentials. Refer to chapter
[Inventories](https://docs.ansible.com/ansible-tower/latest/html/userguide/inventories.html)
of the *Ansible Tower User Guide* for detailed instructions.

## Creating the Job Template

Next, select *Templates* on the left side of the navigation panel. You
will see a list of job templates, if there are any. To define a new
job template click the green plus on the top right corner as shown:

![How to add a new job template](images/ansible_tower_add_new_job_template.png)

Fill in all required fields and the desired optional fields. Detailed
explanations about job templates are described in chapter [Job
Templates](https://docs.ansible.com/ansible-tower/latest/html/userguide/job_templates.html)
of the *Ansible Tower User Guide*.

Add your variables as specified in file `vars/ocp-extra-vars.yml` to
field __Extra Variables__. See section [*Specifying your
settings*](ANSIBLE.md#specifying-your-settings) for all required variables.

Select playbook `ansible/ocp-deployment-ansible-tower.yml` in field __Playbook__.

Finally save the job template.

## Building the Images and Starting the SAP System

Launch the job. A green status of the job run indicates that the three
images were successfully built and the deployment of the SAP system
was successfully started.

Verify whether your SAP system was correctly started by performing the
steps described in section [*Verifying 
Deployments*](VERIFYING-MANAGING.md#verifying-deployments).

## Connecting to the Deployed SAP System

To connect to the deployed SAP system refer to section [*Managing
Deployments*](VERIFYING-MANAGING.md#managing-deployments).
