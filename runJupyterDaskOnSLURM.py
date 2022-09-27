#!/usr/bin/env python

"""
This script provides convenience functions to launch a jupyter dask on SLURM session from a local machine
with ssh access to the remote supercomputer administerd by SLURM. This assumes the installation and configuration of
JupyterDaskOnSLURM has been completed on the remote host.

USE:
The script can most easily be invoked as 'python runJupyterDaskOnSLURM.py --<your arg>'

When invoking the script one of the following command line arguments MUST be provided:
--add_platform (-a) : The script will query the user for login and connection information for the platform.
                      This information is then saved in ./config/platforms/platforms.ini for future use
--one_off (-oo)     : As for add platform, except that the information entered is NOT saved
--platform (-p)     : The script will look for the login and connection information for the platform specified 
                      by the string passed and will use this, if successful.

Optionally the user can pass the local port to be used in the Jupyter instance from the remote host. This can be done using

--local_port (-lp)  : The script will set up portforwarding to the specified port of the localhost. 
                      If not specified port 8889 is used

"""     
import os
import argparse
import configparser
import time
import webbrowser
from fabric import Connection

"""
Specify paths
config_path     : path to config file that is created/updated. default is in local instalation of JupyterDaskOnSLURM
                 repository. Can be adapted to user preferences
remoteWD        : Working directory from which to submit batch job on remote host
remoteScriptWD  : Path to directory on remote host where job submission scripts are located
                  ATTENTION! When adding a job script on a plattform other than spider/snellius @SURF the user MUST
                  create a jobscript for the platform (this can be done by using the exisiting scripts as templates).
                  Expected naming convention is 'jupyter_dask_xxx.bsh', where xxx is the name of the platform.  
"""
config_path = './config/platforms/platforms.ini'
remoteWD = 'JupyterDaskOnSLURM'
remoteScriptD = '~/JupyterDaskOnSLURM/scripts/'


def parse_cla():
    """
    command line argument parser

    accepted arguments:
        mutualy exclusive, one required:
        --add_platform (-a) : The script will query the user for login and connection information for the platform.
                              This information is then saved in ./config/platforms/platforms.ini for future use
        --one_off (-oo)     : As for add platform, except that the information entered is NOT saved
        --platform (-p)     : The script will look for the login and connection information for the platform specified 
                              by the string passed and will use this, if successful.

        optional:
        --local_port (-lp)  : The script will set up portforwarding to the specified port of the localhost. 
                              If not specified port 8889 is used 

    :return args: ArgumentParser return object containing command line arguments  

    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--local_port", "-lp", help="specify non-default local port for port forwarding", type=str)
    parser.add_argument("--wait_time", "-wt", help="time in integer seconds to wait for SLURM to schedule jupyter server job", type=int)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--add_platform", "-a", help="add new platform and store config", action="store_true")
    group.add_argument("--one_off", "-oo", help="one-off interactive configuration", action="store_true")
    group.add_argument("--platform", "-p", help="Make use of configuration for known platform as saved in platforms.ini.", type=str)
    args = parser.parse_args()
    return args 

def get_verified_input(prompt):
    """
    Query user for input on command line using specified prompt.
    Register input, display input and ask for confirmation of correctness. Only proceed upon confirmation.

    :param prompt: str; prompt to display to user requesting input
    :return userinput: str; user supplied input  
    """
    unverified = True
    while unverified:
        userinput = input(prompt+'\n')
        print(userinput+'\n')
        verification = input('is this correct? [Y]/n]'+'\n') or 'Y'
        print(verification+'\n')
        if verification == 'Y':
            unverified = False
    return userinput

def add_platform(oneoff=False):
    """
    Query information from user required to use a platform in the context of JupyterDaskOnSLURM. Optionally save.
    Returns input information.
    Queries:
        platform name
        host alias, e.g. USER@spider.surf.nl, where spider.surf.nl is the host alias
        user name for platform
        absolute (local) path to SSH key granting access to platform

    :param oneoff: default False; if true DO NOT save input to config file, but only use for this deployment
    :return config_inputs: dictionary with fields {host: user: keypath:}
    :return platform_name: name specifying platform (is used in selecting job scripts) 
    
    """
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
    """
    Load platfrom configuration from config file

    :param platform: str specifiying platform. Corresponds to section in the platforms.ini file
    :return config_inputs: dictionary with fields {host: user: keypath:}
    :return platform: echo platform input argument
    """
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
    """
    Retrieve configuration depending on user selection in command line arguments. The arguments specificying
    platform input and configuration are mutually exclusive (see documentation above). Wrapper around config 
    retrieval functions.

    :param args: ArgumentParser return object containing command line arguments

    :return config_inputs: dictionary with fields {host: user: keypath:}
    :return platform: (echo) platform name
    """
    if args.add_platform:
	    return add_platform()
    elif args.one_off:
	    return add_platform(oneoff=True)
    else:
        return load_platform_config(args.platform)

def establish_connection(config_inputs):
    """
    Establish ssh connection oject to remote host based on configuration.

    :param config_inputs: configuration input parameters
    :return conn: ssh connection object
    """
    conn = Connection(host=config_inputs['host'],user=config_inputs['user'],connect_kwargs={'key_filename':config_inputs['keypath']})
    return conn

def submit_scheduler(conn, args, platform):
    """
    submit batch job with jupyter server on remote host

    :param conn: ssh connection object
    :param args: ArgumentParser return object containing command line arguments. included for optional specification of local port
    :return outfilename: name of slurm output file on remote host
    """
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

def check_for_SLURM(conn,outfilename,args):
    """
    check whether SLURM output file is present indicating SLURM has scheduled jupyter server job


    """

    if args.wait_time is not None:
        attempts = int(ceil(args.wait_time)/2)
    else:
        attempts = 10

    cmd = f"cd {remoteWD} && [ ! -f {outfilename} ] && echo 'waiting' || echo 'found' "
    i=0
    file_present = False
    print(f"Waiting for SLURM output: {outfilename} ...")
    while i < attempts:
        res = conn.run(cmd)
        if 'found' in res.stdout :
            print(f"SLURM outputfile {outfilename} present. Retrieving node information")
            file_present = True
            break
        else:
            if i <= (attempts-2):
                i+= 1
                time.sleep(2)
            else:
                i+= 1
                print(f"SLURM outputfile {outfilename} was not found after {args.wait_time} seconds. Aborting")
    return file_present 


 

def retrieve_node_info(conn,outfilename):
    """
    Parse and retrieve information on node where server is running on remote platform and whicch ports are being used
    for port forwarding to local host

    :param conn: ssh connection object
    :param outfilename: name of slurm output file on remote host
    :return portsnodes: pastable string for ssh port forwarding command
    :return lp: local port number
    :return node: node identifier of remote platform
    :return remoteport: number of remote port where jupyter server is exposed
    """
    cmd = f"cd {remoteWD} && cat {outfilename} | grep '/path/to/private/ssh/key' - | cut -d ' ' -f 6- - "
    result = conn.run(cmd)
    portsnodes = result.stdout.rstrip()
    node = portsnodes.split(' ')[0].split(':')[1]
    lp = portsnodes.split(' ')[0].split(':')[0]
    remoteport = portsnodes.split(' ')[0].split(':')[2] 
    return portsnodes, lp, node, remoteport

def forward_ports(portsnodes, config_inputs):
    """
    execute port forwarding command

    :param portsnodes: pastable string for ssh port forwarding command
    :config_inputs: dictionary with fields {host: user: keypath:} for ssh connection to remote 
    """
    cmd = f"ssh -i {config_inputs['keypath']} -N -L {portsnodes} & "
    os.system(cmd)


def launchJupyterLabLocal(localport):
    """
    Launch web browser (system default) listening to local port of fowarded remote jupyter server

    :param localport: port on localhost 
    """
    local_address = f"http://localhost:{localport}"
    webbrowser.open(local_address, new=0, autoraise=True)


def main():
    """
    run thrrough steps to lauch JupyterDaskOnSLURM instance on remote platform
    """
	 
    #parse commandd line arguments
    args = parse_cla()
    # retrieve or set config
    config_inputs, platform_name = get_config(args)
    #establish connection to remote
    conn = establish_connection(config_inputs)
    #submit batch job with scheduler
    outfilename = submit_scheduler(conn,args,platform_name)
    file_present = check_for_SLURM(conn,outfilename,args)

    if file_present:
        #parse response to get node information
        portsnodes, localport, node, remoteport = retrieve_node_info(conn, outfilename)
        #set up port forwarding from remote to local
        forward_ports(portsnodes, config_inputs)
        #lauch local browser cconnected to remote Jupyter Lab instance
        launchJupyterLabLocal(localport)
    else:
        print("SLURM failed to schedule job for submission with specified time\n")
        print("Try increasing the wait time or check the submission on remote host")


if __name__ == '__main__':
    main()

	












