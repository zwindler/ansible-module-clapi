#!/usr/bin/python

from ansible.module_utils.basic import *
import shlex, subprocess, sys

def host_present(data):
    #Building command base
    basecmd = "centreon -u "+data['username']+" -p "+data['password']
    operation = " -o HOST -a add"

    #Building -v argument
    varg = ' -v "'+data['hostname']+';'+data['hostname']+';'+data['ipaddress']+';'+data['hosttemplate']+';'+data['pollername']+';'
    if data['groupname']:
        varg += data['groupname']+';'
    varg += '"'

    #Building final command
    fullcmd = basecmd+operation+varg

    args = shlex.split(fullcmd)
    proc = subprocess.Popen(args, stdout=subprocess.PIPE)
    (out, err) = proc.communicate()

    if out == '':
        has_changed = True
        meta = {"present": "successfully added"}
        return (has_changed, meta)
    else:
        if out.find("Object already exists") == 0:
            has_changed = False
            meta = {"present": out}
            return (has_changed, meta)
        else:
            print json.dumps({
                "failed" : True,
                "msg"    : "centreon command failed with error: "+out
            })
            sys.exit(1)

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
