#!/bin/bash

echo "Current working directory is $PWD"
if [[ ! ./ -ef ~ ]] ; then
    echo "changing directory to $HOME" 
    cd $HOME
fi

#clone the hpc_container_wrapper JupyterDaskOnSLurm repositories
#tis assumes that git access (ssh key) has been configured on spider by the user
git clone git@github.com:CSCfi/hpc-container-wrapper.git
#git clone git@github.com:RS-DAT/JupyterDaskOnSLURM.git

#change directory to the hpc-container-wrapper dir
cd hpc-container-wrapper
echo "Current working directory is $PWD"

#copy spider config to hpc-container-wrapper configs
cp ../JupyterDaskOnSLURM/config/container/spider.yaml ./configs/

#run container wrapper installation
source install.sh spider
echo 'completed hpc-container-wrapper install.sh for spider'

echo 'copying environment.yaml from JupyterDaskOnSlurm'
cp ../JupyterDaskOnSLURM/environment.yaml .
echo 'creating new containerized environment'

#the hardcoded bash structure of hpc-container-wrapper makes sourced calls to the containerization
#unfeasible, at least while adhereing to the overall program flow. Similarly the bash scripts also preclude a 
#more direct call of the relevant routines. The solution below is a interm fix until we decide whether to fork and fix 
#or create and issue and submit a PR upstream.
#

containerize_source_file='./frontends/containerize'
containerize_match="calling_name=\$(basename \$0)"
containerize_insert="calling_name=\$(basename \${BASH_SOURCE\[0\]})"

sed -i "s@$containerize_match@$containerize_insert@" $containerize_source_file


mkdir -p  ./jupyter_dask
source bin/conda-containerize new --prefix ./jupyter_dask ./environment.yaml
echo 'complete'

echo 'updating JupyterDaskOnSLurm configuration'
cd ..
mkdir -p ~/.config/dask 
cp JupyterDaskOnSLURM/config/dask/config_spider.yml ~/.config/dask/config.yml

#insert path export statements into configuration files
#this makes use of `sed`. Note that the  comamnd behaviour of `sed` for inline replacement differs between Linux and MacOs
#this is handled below

dask_config_file="$HOME/.config/dask/config.yml"
dask_config_match="walltime: '10:00:00'"
dask_config_insert="    job_script_prologue:\n    -  'export PATH=\"$_inst_path/bin:\$PATH\" ' \n    python: python\n "

sed -i "s@$dask_config_match@$dask_config_match\n$dask_config_insert@" $dask_config_file

slurm_file="$HOME/JupyterDaskOnSLURM/scripts/jupyter_dask_spider_container.bsh"
slurm_match="export PATH=\"/absolute/path/to/the/container/bin:\$PATH\""
slurm_insert="export PATH=\"$_inst_path/bin:\$PATH\""

sed -i "s@$slurm_match@$slurm_insert@" $slurm_file


