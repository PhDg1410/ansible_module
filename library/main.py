#!/usr/bin/python3

from ansible.module_utils.basic import AnsibleModule
import os
import pandas as pd 

# extract data 
def extract_data(ansible_facts,extra_vars):
    #default 
    mounts = ansible_facts.get("mounts",[])
    for mount in mounts:
        if mount.get("mount") == "/" :
            root = mount.get("size_total")
            
    infor = {
        "hostname": ansible_facts.get("hostname"),
        "default_ip_v4": ansible_facts.get("default_ipv4", {}).get("address"),
        "distribution": ansible_facts.get("distribution"),
        "distribution_version": ansible_facts.get("distribution_version"),
        "bios_version" : ansible_facts.get("bios_version"),
        "os_kernel": ansible_facts.get("kernel"),
        "cpu": ansible_facts.get("processor_vcpus"),
        "total_ram": ansible_facts.get("memtotal_mb"),
        "disk": {mount.get("device"):str(round((mount.get("size_total")/(1024**3)),2))+"GB" for mount in ansible_facts.get("mounts", []) if not mount.get("device", "").startswith("dev/loop") and mount.get("mount", "") != "/"},
        "root": str(round(root/(1024**3),2)) + "GB",
        "username": ansible_facts.get("user_id"),
    }
    #extra_vars
    infor.update(extra_vars)
    return infor
#convert data 
def convert_data(infor):
    result = {}
    for key,value in infor.items():
        key = f"{key}"
        result[key]=[value]
    return result
#to excel
def to_excel(path,data):
    df=pd.DataFrame(data)
    try:
        if(os.path.exists(path)):
            exist_df= pd.read_excel(path)
            updated_df = pd.concat([exist_df,df],ignore_index=True)
            updated_df.to_excel(path,index=False)
            return True
        else:
            df.to_excel(path,index=False)
            return True
    except FileNotFoundError:
        return False
    
def main():
    module_args = dict(
        facts=dict(type='dict',required=True),
        path=dict(type='str', required=False, default="hostinfo.xlsx"),
        extra_vars=dict(type='dict',required=False,default={})
    )
    result = dict(changed=False,msg='')
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )
    ansible_facts =  module.params['facts']
    path = module.params["path"] 
    extra_vars= module.params["extra_vars"]
    data = extract_data(ansible_facts,extra_vars)
    converted_data = convert_data(data)
    is_success = to_excel(path,converted_data)
    if is_success == True:
        result["msg"]="Export to excel successfully"
    else:
        result["msg"]="Export to excel file failed"
    
    module.exit_json(**result)

if __name__ == "__main__":
    main()