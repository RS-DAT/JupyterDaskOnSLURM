from fabric import Connection

def ssh_remote_executor(config_inputs, func, *inargs):
    """
    Create ssh connection to remote host and execute logic of function (func) using this connection.

    :param config_inputs: configuration input parameters for ssh connection
    :param func: function object to execute. Accepts only positional arguments
    :param *inargs: positional arguments to be passed to func
    """

    if config_inputs['key_pass'] == 'False':
        with Connection(host=config_inputs['host'],user=config_inputs['user'],connect_kwargs={'key_filename':config_inputs['keypath']}) as conn:
            result = func(conn, *inargs)
    elif config_inputs['key_pass'] == 'True':
        with Connection(host=config_inputs['host'],user=config_inputs['user'],connect_kwargs={'key_filename':config_inputs['keypath'], 'passphrase':config_inputs['passphrase']}) as conn:
            result = func(conn, *inargs)


    return result