#!/usr/bin/python

from ansible.module_utils.basic import *
import subprocess
import sys

def host_present(data):
    #Building command base
    cmd = "centreon -u "+data['username']+" -p "+data['password']+" -o HOST -a add"

    #Building -v argument
    varg = ' -v "'+data['hostname']+';'+data['hostname']+';'+data['ipaddress']+';'+data['hosttemplate']+';'+data['pollername']+';'
    if data['groupname']:
        varg += data['groupname']+';"'
    #Building final command
    cmd += varg+'"'

    try:
        subprocess.check_output(cmd)                       
    except subprocess.CalledProcessError as clapi_error:
        if clapi_error.output.contains("Object already exists"):
                has_changed = False
                meta = {"present": api_error.output}
                return (has_changed, meta)
        else:
                has_changed = False
                print json.dumps({
                    "failed" : True,
                    "msg"    : "centreon command failed with error: "+clapi_error.output
                })
                sys.exit(1)
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
