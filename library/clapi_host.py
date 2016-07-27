#!/usr/bin/python

from ansible.module_utils.basic import *
import subprocess

def host_present(data):
    if data['groupname']:
        varg = '"'+data['hostname']+';'+data['hostname']+';'+data['ipaddress']+';'+data['hosttemplate']+';'+data['pollername']+';'+data['groupname']+';"'
    else:
        varg = '"'+data['hostname']+';'+data['hostname']+';'+data['ipaddress']+';'+data['hosttemplate']+';'+data['pollername']+';"'
    
    proc = subprocess.Popen(["centreon", "-u", data['username'], "-p", data['password'], "-o", "HOST", "-a", "add", "-v", varg], stdout=subprocess.PIPE)
    (out, err) = proc.communicate()

    has_changed = True
    meta = {"present": out}
    return (has_changed, meta)

def main():

    fields = {
        "username": {"required": True, "type": "str"},
        "password": {"required": True, "type": "str"},
        "hostname": {"required": True, "type": "str"},
        "ipaddress": {"required": True, "type": "str"},
        "hosttemplate": {"default": "generic-host", "type": "str"},
        "pollername": {"default": "Central", "type": "str"},
        "groupname": {"type": "str"}
    }

    module = AnsibleModule(argument_spec=fields)
    has_changed, result = host_present(module.params)
    module.exit_json(changed=has_changed, meta=result)


if __name__ == '__main__':  
    main()
