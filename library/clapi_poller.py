#!/usr/bin/python

def base_command(username, password):
    #TODO find centreon path
    return "centreon -u "+username+" -p "+password+" "

def run_command(fullcmd):
    proc = subprocess.Popen(shlex.split(fullcmd), stdout=subprocess.PIPE)
    return proc.communicate()[0],proc.returncode

def poller_action(data):
    #building command
    basecmd = base_command(data['username'], data['password'])
    operation = "-a "+data['action']+" "
    varg = '-v "'+data['pollername']+'"'
    #running full command
    (cmdout, rc) = run_command(basecmd+operation+varg)

    if rc == 0:
        has_changed = True
        meta = {"success": "action "+data['action']+" completed successfully. "+cmdout}
        return (has_changed, meta)
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
