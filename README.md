ansible_module_clapi 0.1

This repository contains a few Python files that can be used by Ansible as modules to automate [Centreon](https://www.centreon.com/fr/) interactions.

# Purpose of this repository

These Ansible modules act as an interface with [CLAPI (Centreon API)](https://documentation.centreon.com/docs/centreon-clapi/en/latest/).

Although you can just use **shell** or **command** ansible module to execute CLAPI code, I have found that you couldn't use this in the *idempotent* "Ansible as a configuration Manager" way of life.

Each time you execute a playbook with CLAPI as shell on a group of servers (some of whom may already have been added) this raises an error.
```
TASK [monitor : centreon add host] *********************************************
fatal: [srv-nouveau-01 -> superviseur.company.lan]: FAILED! => {'changed': true, 'cmd': '/usr/bin/centreon -u admin -p admin -o HOST -a add -v \'srv-nouveau-01;srv-nouveau-01;192.168.1.12;generic-host;central;Ping_LAN\'', 'delta': '0:00:00.098198', 'end': '2016-07-25 17:17:01.268410', 'failed': true, 'rc': 1, 'start': '2016-07-25 17:17:01.170212', 'stderr': '', 'stdout': 'Object already exists (srv-nouveau-01)', 'stdout_lines': ['Object already exists (srv-nouveau-01)'], 'warnings': []}
```

You could just trap the error with *ignore_errors: True* but that could lead to unexpected trouble.

On the contrary, these modules can be used in a regular *Configuration Management* *policy* in which your servers are managed by groups by Ansible. The servers that don't need to be added/modified/removed won't be (the module is idempotent) and those who do will.

# Installation

For this modules to work, you need to have:
* Ansible installed somewhere (obviously). Version 2.0+ shoud be OK
* a working connection between servers (aka keys exchanged)
* a working centreon server (2.7+), with a poller, and at least some basic templates, services and hostgroups configuration.
* an admin account on this centreon host (saddly, no "CLAPI only" user yet)

The python files included in the module have been knowingly limited to Python v2.6 capability because CES (Centreon Entreprise Server) is a modified CentOS 6 which is shipped with Python 2.6.

Because CLAPI is working on an actual Centreon node, to actually make CLAPI work Ansible with you will need to:
* use the playbook directive "delegate_to : mycentreonserver"
* install ansible **on** the centreon host and execute playbook from there

# Examples

Each individual module file contains a EXAMPLES variable, as specified by the developing Ansible modules guidelines. 

But to help users, I also added a sample in the *test_suite* directory including:
* test **hosts** file with groups
* variables in **group_vars** directory
* a playbook that tests most of the current features of the modules
 - add a host in Centreon
 - remove this host 
 - remove it again to make sure this doesn't throw an error
 - add it again to continue test
 - add the host in a hostgroup
 - if any of these actions returned "Changed" attribute (all in fact)
  * regenerate configuration and restart poller