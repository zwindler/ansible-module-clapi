#!/usr/bin/python

from ansible.module_utils.basic import *

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
    module.exit_json(changed=False, meta=module.params)


if __name__ == '__main__':  
    main()
