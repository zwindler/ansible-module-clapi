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
module: clapi_host
short_description: Centreon CLAPI host creates/updates/deletes
description:
 - This module allows you to create, modify and delete Centreon host entries
   and associated group and template data. More informations on CLAPI can be
   found on https://documentation.centreon.com/docs/centreon-clapi/en/latest/
version_added: "0.1"
author: "Denis GERMAIN (@zwindler)"

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

  hostname:
    description:
      - hostname to remove/add to centreon configuration
    required: true

  ipaddress:
    description:
      - ip address of the hostname to remove/add to centreon configuration
      - not useful when using delete action (remove host) so 127.0.0.1 by default
    required: true
    default: "127.0.0.1"

  hosttemplate:
    description:
      - Affects added host to host template. By design Centreon requires a host template for each hosts
      - By default, a generic-host template is created at Centreon initialisation
    required: true
    default: "generic-host"

  groupname:
    description:
      - Optional group for added host
    required: false

  pollername:
    description:
      - Select which Centreon host (poller) is targeted. By design, first Centreon poller is called Central
    required: false
    default: "Central"

  action:
    description:
      - Choose whether the host must be add or delete or modified from Centreon poller configuration file
      - C(add) adds host from configuration if needed
      - C(addtemplate) adds pipe separated templates to host
      - C(applytpl) refresh templates to host
      - C(delete) removes host from configuration if needed
      - C(deltemplate) deletes pipe separated templates to host
    required: true
    choices: ['add', 'addtemplate', 'delete', 'deltemplate', 'applytpl']
    default: "add"
'''

EXAMPLES = '''
# Add host "newserver" to Central poller with IP and group
# Delegate if playbook is launched through a non centreon host
# Notification (handlers) to clapi_poller module can be useful
- name: add an host w/ clapi_host
  clapi_host:
    username: clapi
    password: clapi
    hostname: newserver
    ipaddress: 192.168.132.100
    groupname: Ping_LAN
    action: add
  delegate_to: ces
  notify: "notify poller after modification"

# remove hostname "newserver" from Centreon configuration
- name: remove host w/ clapi_host
  clapi_host:
    username: clapi
    password: clapi
    hostname: newserver
    action: delete

# for better automation, consider using roles, facts and variables
# notification to clapi_poller module for restart
- name: add host w/ clapi_host
  clapi_host:
    username: clapi
    password: clapi
    hostname: '{{ inventory_hostname }}'
    ipaddress: '{{ ansible_default_ipv4.address }}'
    groupname: Ping_LAN
    pollername: '{{ centreon_pollername }}'
    action: add
  delegate_to: '{{ centreon_poller }}'
  notify: "notify poller after modification"

# Adds, if needed, the following pipe separated host templates to host
- hosts: localhost
  tasks:
    - name: add host templates to server1
      clapi_host:
        username: clapi
        password: clapi
        hosttemplate: template1|template2
        members: server1
        action: addmtemplate

# Removes, if needed, pipe separated host templates to host
- hosts: localhost
  tasks:
    - name: remove host templates to server1
      clapi_host:
        username: clapi
        password: clapi
        hosttemplate: template1|template2
        members: server1
        action: deltemplate

# Apply template to host
- hosts: localhost
  tasks:
    - name: apply  host templates to server1
      clapi_host:
        username: clapi
        password: clapi
        members: server1
        action: applytpl
'''

def base_command(username, password):
  #TODO find centreon path
  return "centreon -u "+username+" -p "+password

def run_command(fullcmd):
  proc = subprocess.Popen(shlex.split(fullcmd), stdout=subprocess.PIPE)
  return proc.communicate()[0],proc.returncode

def host_presence(data):
  basecmd = base_command(data['username'], data['password'])
  operation = " -o HOST -a show"

  #running full command
  (cmdout, rc) = run_command(basecmd+operation)

  if rc == 0:
    for line in cmdout.split('\n'):
      if line and line.split(";")[1] == data['hostname']:
        return True
    return False
  else:
    print json.dumps({
      "failed" : True,
      "msg"    : "centreon SHOW command failed with error: "+cmdout
    })
    sys.exit(1)

def host_template_presence(data):
  basecmd = base_command(data['username'], data['password'])
  operation = " -o HOST -a gettemplate"
  varg = ' -v "'+data['hostname']+'"'
  
  #running full command
  (cmdout, rc) = run_command(basecmd+operation+varg)

  if rc == 0:
    for line in cmdout.split('\n'):
      if line and line.split(";")[1] == data['hosttemplate']:
        return True
    return False
  else:
    print json.dumps({
      "failed" : True,
      "msg"    : "centreon GETTEMPLATE command failed with error: "+cmdout
    })
    sys.exit(1)
    
def host_add(data):
  #check if host is already present
  if host_presence(data):
    return (False, {"add": "host "+data['hostname'] + " already exists"})
  
  #building command
  basecmd = base_command(data['username'], data['password'])
  operation = " -o HOST -a add "
  varg = '-v "'+data['hostname']+';'+data['hostname']+';'+data['ipaddress']+';'+data['hosttemplate']+';'+data['pollername']+';'
  if data['groupname']: varg += data['groupname']+';'
  varg += '"'

  #running full command
  (cmdout, rc) = run_command(basecmd+operation+varg)

  if rc == 0:
    return (True, {"add": "successfully added "+data['hostname']})
  else:
    if cmdout.find("Object already exists") == 0:
      return (False, {"add": cmdout})
    else:
      print json.dumps({
        "failed" : True,
        "msg"    : "centreon command ADD failed with error: "+cmdout
      })
      sys.exit(1)

def host_addtemplate(data):
  #check if host template is already present
  if host_template_presence(data):
    return (False, {"add": "host template "+data['hosttemplate'] + " is already a template for "+data['hostname']})
  
  basecmd = base_command(data['username'], data['password'])
  operation = " -o HOST -a addtemplate"
  varg = ' -v "'+data['hostname']+';'+data['hosttemplate']+'"'

  (cmdout, rc) = run_command(basecmd+operation+varg)

  if rc == 0:
    return (True, {"added": "successfully added template "+data['hosttemplate']+" to host "+data['hosttemplate']})
  else:
    print json.dumps({
      "failed" : True,
      "msg"    : "centreon command ADDTEMPLATE failed with error: "+cmdout
    })
    sys.exit(1)

def host_applytpl(data):
  basecmd = base_command(data['username'], data['password'])
  operation = " -o HOST -a applytpl"
  varg = ' -v "'+data['hostname']+'"'

  #running full command
  (cmdout, rc) = run_command(basecmd+operation+varg)

  if rc == 0:
    return (True, {"added": "successfully applied templates to host "+data['hosttemplate']})
  else:
    print json.dumps({
      "failed" : True,
      "msg"    : "centreon command APPLYTPL failed with error: "+cmdout
    })
    sys.exit(1)

def host_delete(data):
  #check if host is already present
  if not host_presence(data):
    return (False, {"delete": "host "+data['hostname'] + " already absent"})
  
  #building command
  basecmd = base_command(data['username'], data['password'])
  operation = " -o HOST -a del"
  varg = ' -v "'+data['hostname']+'"'

  #running full command
  (cmdout, rc) = run_command(basecmd+operation+varg)

  if rc == 0:
    return (True, {"delete": "successfully removed "+data['hostname']})
  else:
    if cmdout.find("Object not found") == 0:
      return (False, {"delete": cmdout})
    else:
      print json.dumps({
        "failed" : True,
        "msg"    : "centreon command DEL failed with error: "+cmdout
      })
      sys.exit(1)

def host_deltemplate(data):
  #check if host template is already present
  if not host_template_presence(data):
    return (False, {"deltemplate": "host template "+data['hosttemplate'] + " isn't a template for "+data['hostname']})

  basecmd = base_command(data['username'], data['password'])
  operation = " -o HOST -a deltemplate"
  varg = ' -v "'+data['hostname']+';'+data['hosttemplate']+'"'

  (cmdout, rc) = run_command(basecmd+operation+varg)

  if rc == 0:
    return (True, {"deleted": "successfully deleted template "+data['hosttemplate']+" from host"+data['hosttemplate']})
  else:
    print json.dumps({
    "failed" : True,
    "msg"    : "centreon command DELTEMPLATE failed with error: "+cmdout
    })
    sys.exit(1)

def main():
  fields = {
    "username": {"required": True, "type": "str"},
    "password": {"required": True, "type": "str"},
    "hostname": {"required": True, "type": "str"},
    "ipaddress": {"default": "127.0.0.1", "type": "str"},
    "hosttemplate": {"default": "generic-host", "type": "str"},
    "pollername": {"default": "Central", "type": "str"},
    "groupname": {"type": "str"},
    "action": {
      "default": "add",
      "choices": ['add', 'addtemplate', 'delete', 'deltemplate', 'applytpl'],
      "type": 'str'
    },
  }
  choice_map = {
    "add": host_add,
    "addtemplate": host_addtemplate,
    "delete": host_delete,
    "deltemplate": host_deltemplate,
    "applytpl": host_applytpl,
  }

  module = AnsibleModule(argument_spec=fields)
  has_changed, result = choice_map.get(module.params['action'])(module.params)
  module.exit_json(changed=has_changed, meta=result)

from ansible.module_utils.basic import *
import shlex, subprocess, sys, string

if __name__ == '__main__':
    main()
