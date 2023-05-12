#!/usr/bin/env python

"""
This script provides installation functions to launch a jupyter dask on SURF infrastructure (snellius or spider)
with ssh access to the remote supercomputer administered by SLURM. This does not configure or set-up dCache.
This script is automatically invoked from the runJupyterDaskOnSLURM script when install or uninstall flags are invoked.

USE:
The script can most easily be invoked through 'python runJupyterDaskOnSLURM.py --<your arg>'

Paths to the working directory and scripts on the remote host, as well as to the local connection configuration file can be specified below.
Configurable paths are:

config_path     : path to config file that is created/updated. default is in local installation of JupyterDaskOnSLURM
                  repository. Can be adapted to user preferences
remoteWD        : Working directory from which to submit batch job on remote host
remoteJDD       : Clone directory of JupyterDaskOnSLURM
remoteScriptWD  : Path to directory on remote host where job submission scripts are located
                  ATTENTION! When adding a job script on a plattform other than spider/snellius @SURF the user MUST
                  create a job script for the platform (this can be done by using the existing scripts as templates).
                  Expected naming convention is 'jupyter_dask_xxx.bsh', where xxx is the name of the platform.
mamba_URL       : Download URL for mamba installation file
"""
 
from fabric import Connection
from runJupyterDaskOnSLURM import ssh_remote_executor

config_path = './config/platforms/platforms.ini'
remoteWD = '~'
remoteJDD = '~/JupyterDaskOnSLURM'
mamba_URL = 'https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-Linux-x86_64.sh'

def check_clone(conn):
    """
    Check if repository has been cloned already on remote host

    :param conn: ssh connection object
    :return folder_exists: Logical on whether the repository exists on remote host 
    """
    cmd = f"if test -d JupyterDaskOnSLURM; then echo 'True'; fi"
    folder_exists = False
    result = conn.run(cmd, hide=True)
    folder_exists = result.stdout
    return folder_exists

def clone_folder(conn):
    """
    Clone repository from github to remote host

    :param conn: ssh connection object
    :return None:
    """
    cmd = "git clone --branch workshops https://github.com/RS-DAT/JupyterDaskOnSLURM.git"
    conn.run(cmd, hide=True)
    return None

def test_mamba(conn):
    """
    Check if mamba is installed on remote host

    :param conn: ssh connection object
    :return mamba_exists: Logical on if mamba is installed on remote host
    """
    cmd = "if command -v mamba ; then echo 'True'; fi"
    mamba_exists = False
    result = conn.run(cmd, hide=True)
    mamba_exists = result.stdout
    return mamba_exists

def install_mamba(conn):
    """
    Install mamba on remote host

    :param conn: ssh connection object
    :return None:
    """
    cmd = f"/project/stursdat/Software/mambaforge/condabin/conda init"
    conn.run(cmd)
    cmd = f"mamba init"  # need to login again to access mamba
    conn.run(cmd)
    return None

def test_env(conn, envfile):
    """
    Check whether the mamba environment is configured on remote host

    :param conn: ssh connection object
    :param envfile: Name of the yaml file containing the dependencies and environment name.
    :return env_exists: Logical on whether environment exists on remote host
    :return envname: Name of the expected environment
    """
    cmd = f"cd {remoteJDD} && head -1 {envfile} && mamba env list"
    result = conn.run(cmd, hide=True)
    env_exists = False
    index = result.stdout.find('\n')
    envname = result.stdout[6:index]
    if envname in result.stdout[index+1:]:
        env_exists = True
    return env_exists, envname

def create_env(conn, envfile):
    """
    Create mamba environment from file on remote host

    :param conn: ssh connection object
    :param envfile: Name of the yaml file containing the dependencies and environment name.
    :return None:
    """
    cmd = f"cd {remoteJDD} && mamba env create -f {envfile}"
    conn.run(cmd, hide=False)
    return None

def check_jpconfig(conn):
    """
    Check if jupyter has been configured on remote host

    :param conn: ssh connection object
    :return jpconfig_exists: Logical on whether jupyter is configured on remote host
    """
    cmd = "if test -f ~/.jupyter/jupyter_server_config.py ; then echo 'True'; fi"
    jpconfig_exists = False
    result = conn.run(cmd, hide=True)
    jpconfig_exists = result.stdout
    return jpconfig_exists

def jpconfig(conn, envname):
    """
    Configure jupyter on remote host

    :param conn: ssh connection object
    :param envname: Name of the expected environment
    :return None: 
    """
    cmd = f'cd {remoteJDD} && mamba activate {envname} && jupyter server --generate-config && jupyter server password && chmod 400 ~/.jupyter/jupyter_server_config.py'
    conn.run(cmd, hide=False)
    return None

def check_daskconfig(conn):
    """
    Check if dask has been configured on remote host

    :param conn: ssh connection object
    :param args: ArgumentParser return object containing command line arguments. included for optional specification of local port
    :param platform: platform name
    :return outfilename: name of slurm output file on remote host
    """
    cmd = "if test -f ~/.config/dask/config.yml ; then echo 'True'; fi"
    daskconfig_exists = False
    result = conn.run(cmd, hide=True)
    daskconfig_exists = result.stdout
    return daskconfig_exists

def daskconfig(conn, platform):
    """
    Submit batch job with jupyter server on remote host

    :param conn: ssh connection object
    :param args: ArgumentParser return object containing command line arguments. included for optional specification of local port
    :param platform: platform name
    :return outfilename: name of slurm output file on remote host
    """
    cmd = f"cd {remoteJDD} && mkdir -p ~/.config/dask && cp -r config/dask/config_{platform}.yml ~/.config/dask/config.yml"
    conn.run(cmd, hide=True)
    return None


def install_JD(config_inputs, platform_name, envfile):
    #Clone folder as needed
    folder_exists = ssh_remote_executor(config_inputs, check_clone)
    if not folder_exists:
        print ('Cloning JupyterDaskonSLURM on remote host...')
        ssh_remote_executor(config_inputs, clone_folder)
        folder_exists = ssh_remote_executor(config_inputs, check_clone)
        if not folder_exists:
            raise ValueError(f'Error cloning repository. Check git credentials or clone manually')
        
    #Install mamba as needed
    mamba_exists = ssh_remote_executor(config_inputs, test_mamba)
    if not mamba_exists:
        print ('Installing mamba on remote host...')
        ssh_remote_executor(config_inputs, install_mamba)
        mamba_exists = ssh_remote_executor(config_inputs, test_mamba)
        if not mamba_exists:
            raise ValueError(f'Error installing mamba. Please install manually')
        
    #Create environment
    env_exists, envname = ssh_remote_executor(config_inputs, test_env, envfile)
    if not env_exists:
        print (f'Creating mamba environment from {envfile} on remote host...')
        ssh_remote_executor(config_inputs, create_env, envfile)
        env_exists = ssh_remote_executor(config_inputs, test_env, envfile)
        if not env_exists:
            raise ValueError(f'Error creating environment. Please create manually')
        
    #Configure Jupyter
    jpconfig_exists = ssh_remote_executor(config_inputs, check_jpconfig)
    if not jpconfig_exists:
        print ('Configuring Jupyter on remote host...')
        ssh_remote_executor(config_inputs, jpconfig, envname)
        jpconfig_exists = ssh_remote_executor(config_inputs, check_jpconfig)
        if not jpconfig_exists:
            raise ValueError(f'Error configuring jupyter. Please configure manually')    
    
    #Configure Dask
    daskconfig_exists = ssh_remote_executor(config_inputs, check_daskconfig)
    if not daskconfig_exists:
        print ('Configuring Dask on remote host...')
        ssh_remote_executor(config_inputs, daskconfig, platform_name)
        daskconfig_exists = ssh_remote_executor(config_inputs, check_daskconfig)
        if not daskconfig_exists:
            raise ValueError(f'Error configuring dask. Please configure manually') 
        
    #Configure Dcache
    dcache_config = input ('If you want to use dCache, it needs to be manually configured. Has dCache been configured? (Y/n): ')
    if dcache_config in {'Y', 'y'}:
        print ("dCache configured by User")
    elif dcache_config in {'N', 'n'}: 
        print ("""
Please configure dCache as per the instructions in https://github.com/RS-DAT/JupyterDaskOnSLURM/blob/main/user-guide.md.
Please note that the deployable analysis environment does not require dCache to run scalable analyses. 
            """)  
    else:
        raise ValueError('Chosen option invalid. Please retry.')
    
    install = False
    if (folder_exists and mamba_exists and env_exists and jpconfig_exists and daskconfig_exists):
        install = True
    
    return install

def remove_env(conn, envname):
    """
    Submit batch job with jupyter server on remote host

    :param conn: ssh connection object
    :param args: ArgumentParser return object containing command line arguments. included for optional specification of local port
    :param platform: platform name
    :return outfilename: name of slurm output file on remote host
    """
    cmd = f"cd {remoteWD} && mamba env remove -n {envname}"
    conn.run(cmd, hide=False)
    return None

def remove_files(conn):
    """
    Submit batch job with jupyter server on remote host

    :param conn: ssh connection object
    :param args: ArgumentParser return object containing command line arguments. included for optional specification of local port
    :param platform: platform name
    :return outfilename: name of slurm output file on remote host
    """
    cmd = f"cd {remoteWD} && rm -f ~/.config/dask/config.yml ~/.jupyter/jupyter_server_config.py "
    conn.run(cmd, hide=False)
    return None

def remove_folders(conn):
    """
    Submit batch job with jupyter server on remote host

    :param conn: ssh connection object
    :param args: ArgumentParser return object containing command line arguments. included for optional specification of local port
    :param platform: platform name
    :return outfilename: name of slurm output file on remote host
    """
    cmd = f"cd {remoteWD} && rm -rf ~/JupyterDaskOnSLURM"
    conn.run(cmd, hide=False)
    return None

def uninstall_JD(config_inputs, platform_name, envfile = 'environment.yaml'):
    print ('Uninstalling all components...')
    _, envname = ssh_remote_executor(config_inputs, test_env, envfile)
    # print ('Removing environment...')
    # ssh_remote_executor(config_inputs, remove_env, envname)
    print ('Removing JupyterDaskOnSLURM...')
    ssh_remote_executor(config_inputs, remove_folders)
    print ('Removing config files...')
    ssh_remote_executor(config_inputs, remove_files)
    
    uninstall = True
    return uninstall

