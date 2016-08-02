#!/usr/bin/python

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
        "ipaddress": {"required": True, "type": "str"},
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
