#!/usr/bin/python

DOCUMENTATION = '''
---
module: clapi_host
short_description: Centreon CLAPI host creates/updates/deletes
description:
   - This module allows you to create, modify and delete Centreon host entries 
   - and associated group and template data. More informations on CLAPI can be 
   - found on https://documentation.centreon.com/docs/centreon-clapi/en/latest/
version_added: "0.1"
author:
    - "Denis GERMAIN (@zwindler)"
requirements:
    - "python >= 2.6"
    - Centreon with CLAPI
options:
    "username": {"required": True, "type": "str"},
    "password": {"required": True, "type": "str"},
    "hostname": {"required": True, "type": "str"},
    "ipaddress": {"default": "127.0.0.1", "type": "str"},
    "hosttemplate": {"default": "generic-host", "type": "str"},
    "pollername": {"default": "Central", "type": "str"},
    "groupname": {"type": "str"},
    "state": {
        "default": "present", 
            "choices": ['present', 'absent'],  
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
    hostname:
		description:
			- hostname to remove/add to centreon configuration
        required: true
	ipaddress:
		description:
			- ip address of the hostname to remove/add to centreon configuration
			- not usefull when using absent state (remove host) so 127.0.0.1 by default
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
    state:
        description:
            - Choose whether the host must be present or absent from Centreon poller configuration file
            - C(absent) removes host from configuration if needed
            - C(present) adds host from configuration if needed
        required: true
        choices: ['absent', 'present']
        default: "present"
'''

EXAMPLES = '''
#Add host "newserver" to Central poller with IP and group
#Delegate if playbook is launched through a non centreon host
#Notification (handlers) to clapi_poller module can be useful
- name: add an host w/ clapi_host
  clapi_host: 
    username: clapi
    password: clapi
    hostname: newserver
    ipaddress: 192.168.132.100
    groupname: Ping_LAN
    state: present
  delegate_to: ces
  notify: "notify poller after modification"

#remove hostname "newserver" from Centreon configuration
- name: remove host w/ clapi_host
  clapi_host:
    username: clapi
    password: clapi
    hostname: newserver
    state: absent
'''

def base_command(username, password):
    #TODO find centreon path
    return "centreon -u "+username+" -p "+password+" -o HOST "

def run_command(fullcmd):
    proc = subprocess.Popen(shlex.split(fullcmd), stdout=subprocess.PIPE)
    return proc.communicate()[0],proc.returncode

def host_absent(data):
    #building command
    basecmd = base_command(data['username'], data['password'])
    operation = "-a del "
    varg = '-v "'+data['hostname']+'"'
    #running full command
    (cmdout, rc) = run_command(basecmd+operation+varg)

    if rc == 0:
        has_changed = True
        meta = {"present": "successfully removed"}
        return (has_changed, meta)
    else:
        if cmdout.find("Object not found") == 0:
            has_changed = False
            meta = {"present": cmdout}
            return (has_changed, meta)
        else:
            print json.dumps({
                "failed" : True,
                "msg"    : "centreon command failed with error: "+cmdout
            })
            sys.exit(1)

def host_present(data):
    #building command
    basecmd = base_command(data['username'], data['password'])
    operation = "-a add "
    varg = '-v "'+data['hostname']+';'+data['hostname']+';'+data['ipaddress']+';'+data['hosttemplate']+';'+data['pollername']+';'
    if data['groupname']:
        varg += data['groupname']+';'
    varg += '"'
    #running full command
    (cmdout, rc) = run_command(basecmd+operation+varg)

    if rc == 0:
        has_changed = True
        meta = {"present": "successfully added"}
        return (has_changed, meta)
    else:
        if cmdout.find("Object already exists") == 0:
            has_changed = False
            meta = {"present": cmdout}
            return (has_changed, meta)
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
        "hostname": {"required": True, "type": "str"},
        "ipaddress": {"default": "127.0.0.1", "type": "str"},
        "hosttemplate": {"default": "generic-host", "type": "str"},
        "pollername": {"default": "Central", "type": "str"},
        "groupname": {"type": "str"},
        "state": {
            "default": "present", 
            "choices": ['present', 'absent'],  
            "type": 'str' 
        },
    }
    choice_map = {
      "present": host_present,
      "absent": host_absent, 
    }

    module = AnsibleModule(argument_spec=fields)
    has_changed, result = choice_map.get(module.params['state'])(module.params)
    module.exit_json(changed=has_changed, meta=result)

from ansible.module_utils.basic import *
import shlex, subprocess, sys

if __name__ == '__main__':  
    main()
