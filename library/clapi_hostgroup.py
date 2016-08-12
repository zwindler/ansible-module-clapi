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
module: clapi_hostgroup
short_description: Centreon CLAPI hostgroup creates/updates/deletes
description:
   - This module allows you to create, modify and delete Centreon hostgroups 
   - More informations on CLAPI can be found on 
   - https://documentation.centreon.com/docs/centreon-clapi/en/latest/
version_added: "0.1"
author:
    - "Denis GERMAIN (@zwindler)"
requirements:
    - "python >= 2.6"
    - Centreon with CLAPI
options:
    "username": {"required": True, "type": "str"},
    "password": {"required": True, "type": "str"},
    "hostgroupname": {"required": True, "type": "str"},
    "hostgroupalias": {"required": False, "type": "str"},
    "members": {"required": False, "type": "str"},
    "action": {
        "default": "add", 
        "choices": ['add', 'delete', 'addmembers', 'delmembers'],  
        "type": 'str' 
    },

    username:
        description:
            - Centreon username (must be admin to be allowed to use CLAPI)
        required: true
    password:
        description:
            - Centreon user password
        required: true
    hostgroupname:
        description:
            - hostgroupname to remove/add to centreon configuration
        required: true
    hostgroupalias:
        description:
            - hostgroupalias when you add a new hostgroup
        required: false
    members:
        description:
            - pipe separated hostnames to add to/remove from hostgroup
            - Members MUST exist
        required: false
    action:
        description:
            - Choose whether the hostgroup must be present or absent or modified
            - from Centreon configuration files
            - C(add) adds hostgroup from configuration if needed
            - C(addmembers) adds hosts to hostgroups if needed
            - C(delete) removes hostgroup from configuration if needed
            - C(delmembers) removes hosts from hostgroups 
            - if needed
        required: true
        choices: ['add', 'addmembers', 'delete', 'delmembers']
        default: "add"
'''

EXAMPLES = '''
#Adds a test hostgroup, delegated to centreon poller "ces"
- hosts: localhost
  tasks:
    - name: add test hostgroup
      clapi_hostgroup:
        username: clapi
        password: clapi
        hostgroupname: testgroup
        hostgroupalias: "my test group"
        action: add
      delegate_to: ces
      
#Deletes a test hostgroup
- hosts: localhost
  tasks:
    - name: add test hostgroup
      clapi_hostgroup:
        username: clapi
        password: clapi
        hostgroupname: testgroup
        action: delete
        
#Adds, if needed, the following pipe separated hosts to hostgroup testgroup
- hosts: localhost
  tasks:
    - name: add hosts to test hostgroup
      clapi_hostgroup:
        username: clapi
        password: clapi
        hostgroupname: testgroup
        members: server1|server2|server3
        action: addmembers
        
#Removes, if needed, server3 &4 from hostgroup testgroup
- hosts: localhost
  tasks:
    - name: remove hosts from test hostgroup
      clapi_hostgroup:
        username: clapi
        password: clapi
        hostgroupname: testgroup
        members: server3|server4
        state: delmembers
'''

def base_command(username, password):
    #TODO find centreon path
    return "centreon -u "+username+" -p "+password

def run_command(fullcmd):
    proc = subprocess.Popen(shlex.split(fullcmd), stdout=subprocess.PIPE)
    return proc.communicate()[0],proc.returncode

def hostgroup_add(data):
    #building command
    basecmd = base_command(data['username'], data['password'])
    operation = " -o HG -a add"
    varg = ' -v "'+data['hostgroupname']+';'
    if data['hostgroupalias']:
        varg += data['hostgroupalias']+';"'
    else:
        varg += data['hostgroupname']+';"'
    #running full command
    (cmdout, rc) = run_command(basecmd+operation+varg)

    if rc == 0:
        return (True, {"added": "successfully added hostgroup"})
    else:
        if cmdout.find("Object already exists") == 0:
            return (False, {"present": cmdout})
        else:
            print json.dumps({
                "failed" : True,
                "msg"    : "centreon command failed with error: "+cmdout
            })
            sys.exit(1)

def hostgroup_addmembers(data):
    basecmd = base_command(data['username'], data['password'])
    operation = " -o HG -a addmember"
    #TODO Check w/ "-a getmember" each host individually before doing anything
    varg = ' -v "'+data['hostgroupname']+';'+data['members']+'"'
    
    (cmdout, rc) = run_command(basecmd+operation+varg)

    if rc == 0:
        return (True, {"added": "successfully added to hostgroup"})
    else:
        print json.dumps({
            "failed" : True,
            "msg"    : "centreon command failed with error: "+cmdout
        })
        sys.exit(1)

def hostgroup_delete(data):
    basecmd = base_command(data['username'], data['password'])
    operation = " -o HG -a del"
    varg = ' -v "'+data['hostgroupname']+'"'
    (cmdout, rc) = run_command(basecmd+operation+varg)

    if rc == 0:
        return (True, {"deleted": "successfully deleted hostgroup"})
    else:
        if cmdout.find("Object not found") == 0:
            return (False, {"absent": cmdout})
        else:
            print json.dumps({
                "failed" : True,
                "msg"    : "centreon command failed with error: "+cmdout
            })
            sys.exit(1)

def hostgroup_delmembers(data):
    basecmd = base_command(data['username'], data['password'])
    operation = " -o HG -a delmember"
    #TODO Check w/ "-a getmember" each host individually before doing anything
    varg = ' -v "'+data['hostgroupname']+';'+data['members']+'"'
    
    (cmdout, rc) = run_command(basecmd+operation+varg)

    if rc == 0:
        return (True, {"deleted": "successfully deleted from hostgroup"})
    else:
        print json.dumps({
            "failed" : True,
            "msg"    : "centreon command failed with error: "+cmdout
        })
        sys.exit(1)

def main():
    fields = {
        "username": {"required": True, "type": "str"},
        "password": {"required": True, "type": "str"},
        "hostgroupname": {"required": True, "type": "str"},
        "hostgroupalias": {"required": False, "type": "str"},
        "members": {"required": False, "type": "str"},
        "action": {
            "default": "add", 
            "choices": ['add', 'addmembers', 'delete', 'delmembers'],  
            "type": 'str' 
        },
    }
    choice_map = {
      "add": hostgroup_add,
      "addmembers": hostgroup_addmembers,
      "delete": hostgroup_delete,
      "delmembers": hostgroup_delmembers,
    }

    module = AnsibleModule(argument_spec=fields)
    has_changed, result = choice_map.get(module.params['action'])(module.params)
    module.exit_json(changed=has_changed, meta=result)

from ansible.module_utils.basic import *
import shlex, subprocess, sys

if __name__ == '__main__':  
    main()
