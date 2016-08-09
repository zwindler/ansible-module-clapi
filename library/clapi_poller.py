#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#This file is part of ansible_module_clapi
#Copyright (C) 2016  Denis GERMAIN
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

DOCUMENTATION = '''
---
module: clapi_poller
short_description: Centreon CLAPI poller config generation and restart
description:
   - This module allows you to generate config and restart Centreon pollers 
   - More informations on CLAPI can be found on 
   - https://documentation.centreon.com/docs/centreon-clapi/en/latest/
version_added: "0.1"
author:
    - "Denis GERMAIN (@zwindler)"
requirements:
    - "python >= 2.6"
    - Centreon with CLAPI
options:
    username:
        description:
            - Centreon username (must be admin to be allowed to use CLAPI)
        required: true
    password:
        description:
            - Centreon user password
        required: true
    pollername:
        description:
            - Select which Centreon host (poller) is targeted. By design, first Centreon poller is called Central
        required: false
        default: "Central"
    action:
        description:
            - Choose which action is applied to Centreon poller
            - C(POLLERGENERATE) generates local configuration files for a poller
            - C(POLLERTEST) tests monitoring engine configuration of a poller
            - C(CFGMOVE) moves monitoring engine configuration files
            - C(POLLERRESTART) restarts monitoring engine of a poller
            - C(APPLYCFG) does all the previous actions in one command
        required: false
        choices: ['POLLERGENERATE', 'POLLERTEST', 'CFGMOVE', 'POLLERRESTART', 'APPLYCFG']
        default: "APPLYCFG"
'''

EXAMPLES = '''
#Use this as a handler to APPLYCFG on Central poller if there is a modification
#In this case, playbook is not executed on a Centreon host so delegate_to is used
handlers:
  - name: notify poller after modification
    clapi_poller:
      username: clapi
      password: clapi
    delegate_to: ces
  
#Generate configuration on "somesite" centreon poller
  - name: notify poller after modification
    clapi_poller:
      username: clapi
      password: clapi
      pollername: somesite
      action : POLLERGENERATE
     
#Use roles, groups and vars for better automation
- name: notify poller after modification
  clapi_poller:
    username: clapi
    password: clapi
    pollername: '{{ centreon_pollername }}'
  delegate_to: '{{ centreon_poller }}'
'''

def base_command(username, password):
    #TODO find centreon path
    return "centreon -u "+username+" -p "+password

def run_command(fullcmd):
    proc = subprocess.Popen(shlex.split(fullcmd), stdout=subprocess.PIPE)
    return proc.communicate()[0],proc.returncode

def poller_action(data):
    #building command
    basecmd = base_command(data['username'], data['password'])
    operation = " -a "+data['action']
    varg = ' -v "'+data['pollername']+'"'
    #running full command
    (cmdout, rc) = run_command(basecmd+operation+varg)

    if rc == 0:
        return (True, {"success": "action "+data['action']+" completed successfully. "+cmdout})
    else:
        err = next((s for s in cmdout.split("\n") if 'Error' in s ), "Error not found, check logs")
        print json.dumps({
            "failed" : True,
            "msg"    : "centreon command failed with error: "+err
        })
        sys.exit(1)

def main():

    fields = {
        "username": {"required": True, "type": "str"},
        "password": {"required": True, "type": "str"},
        "pollername": {"default": "Central", "type": "str"},
        "action": {
            "default": "APPLYCFG", 
            "choices": ['POLLERGENERATE', 'POLLERTEST', 'CFGMOVE', 'POLLERRESTART', 'APPLYCFG'],  
            "type": 'str' 
        },
    }

    module = AnsibleModule(argument_spec=fields)
    has_changed, result = poller_action(module.params)
    module.exit_json(changed=has_changed, meta=result)

#imports
from ansible.module_utils.basic import *
import shlex, subprocess, sys

if __name__ == '__main__':  
    main()
