#!/usr/bin/env python

import argparse
import os
from fabric import Connection
import webbrowser

config_path = './config/platforms/platforms.ini'
remoteWD = 'JupyterDaskOnSLURM'
remoteScriptD = '~/JupyterDaskOnSLURM/scripts/'

def parse_cla():
    parser = argparse.ArgumentParser()
    parser.add_argument("--local_port", "-lp", help="specify non-default local port for port forwarding", type=str)
    group = parser.ad_mutually_exclusive_group(required=True)
    group.add_argument("--add_platform", "-a", help="add new platform and store config", action="store_true")
    group.add_argument("--one_off", "-oo", help="one-off interactive configuration", action="store_true")
    group.add_argument("--platform", "-p", help="Make use of configuration for known platform as saved in platforms.ini.", type=str)
    args = parser.parse_args()
    return args 

def get_verified_input(prompt):
    unverified = True
    while unverifed:
        userinput = input(prompt+'\n')
        print(userinput+'\n')
        verification = input('is this correct? [Y]/n]'+'\n') or 'Y'
        print(verification+'\n')
        if verification == 'Y':
            unverified = False
    return userinput

def add_platform(oneoff=False):
    platform_name = get_verified_input('Please enter platform name:')
    platform_host = get_verified_input('Please enter host (alias), e.g. USER@spider.surf.nl, where spider.surf.nl is the host alias:')
    user_name = get_verified_input('Please enter user name for platform: ')
    key_path = get_verified_input('Please enter absolute (local) path to SSH key granting access to platform:')
    config_inputs = {'host':platform_host, 'user':user_name, 'keypath':key_path} 

    if oneoff:
        pass 
    else:
        config = configparser.ConfigParser()
        config[platform_name]=config_inputs
        with open(config_path, 'w') as cf:
            config.write(cf)
    return config_inputs, platform_name	

def load_platform_config(platform):
    config = configparser.ConfigParser()
    config.read(config_path)
    if platform not in config.sections():
        raise ValueError(
            f'unknown platform: {platform}. Please add platform')
    else:
        pfconfig = config[platform]
        config_inputs = {'host':pfconfig['host'], 'user':pfconfig['user'], 'keypath':pfconfig['keypath']}
        return config_inputs, platform

def get_config(args):
    if args.add_platform:
	    return add_platform()
    elif args.one_off:
	    return add_platform(oneoff=True)
    else:
        return load_platform_config(args.platform)

def establish_connection(config_inputs):
    conn = Connection(host=config_inputs['host'],user=config_inputs['user'],connect_kwargs={'key_filename':config_inputs['keypath']})
    return conn

def submit_scheduler(conn, args, platform):
    jscript = 'jupyter_dask_'+platform+'.bsh'
    if args.local_port is not None:
        lport = args.local_port
        cmd = f"cd {remoteWD} && sbatch --export=ALL,lport={lport} {remoteScriptD}{jscript}"
    else:
        cmd = f"cd {remoteWD} && sbatch {remoteScriptD}{jscript}"
    result = conn.run(cmd)
    jobnumber = result.stdout.rstrip().split(' ')[3]
    outfilename = 'slurm-'+jobnumber+'.out'
    return outfilename

def retrieve_node_info(conn,outfilename):
    cmd = f"cd {remoteWD} && cat {outfilename} | grep '/path/to/private/ssh/key' - | cut -d ' ' -f 6- - "
    result = conn.run(cmd)
    portsnodes = result.stdout.rstrip()
    node = portsnodes.split(' ')[0].split(':')[1]
    lp = portsnodes.split(' ')[0].split(':')[0]
    remoteport = portsnodes.split(' ')[0].split(':')[2] 
    return portsnodes, lp, node, remoteport

def forward_ports(portsnodes, config_inputs):
    cmd = f'ssh -i {config_inputs['keypath']} -N -L {portsnodes} &'
    os.system(cmd)


def launchJupyterLabLocal(localport):
    local_address = f"http://localhost:{localport}"
    webbrowser.open(local_address, new=0,autoraise=true)


def main():
    #parse commandd line arguments
    args = parse_cla()
    # retrieve or set config
    config_inputs, platform_name = get_config(args)
    #establish connection to remote
    conn = establish_connection(config_inputs)
    #submit batch job with scheduler
    outfilename = submit_scheduler(conn,args,platform_name)
    #parse response to get node information
    portsnodes, localport, node, remoteport = retrieve_node_info(conn, outfilename)
    #set up port forwarding from remote to local
    forward_ports(portsnodes, config_inputs)
    #lauch local browser cconnected to remote Jupyter Lab instance
    launchJupyterLabLocal(localport)


if __name__ == '__main__':
    main()

	












