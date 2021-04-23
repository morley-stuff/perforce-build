import json, os
from P4 import P4, P4Exception

# Loads json file specified into python dict
def loadConfig(configFilename):
    configFile = open(configFilename, "r")
    config     = json.loads(configFile.read())
    configFile.close()
    return config

# Do perforce login and client/workspace setup
def perforceInit(config):
    # Build session object
    p4 = P4()
    p4.port     = config["perforcePort"]
    p4.user     = config["perforceUser"]
    p4.password = config["perforcePassword"]
    p4.client   = config["perforceClient"]

    try:
        # Create local workspace if it doesnt exist
        if not os.path.exists('root-ws'):
            os.makedirs('root-ws')

        # Connect and login
        p4.connect()
        p4.run_login()
        print(p4, '\n')

        # Set up client
        client = p4.fetch_client("root-ws")
        client['Root'] = os.getcwd() + '/root-ws'
        client['View'] = '//depot/... //root-ws/...'
        client['Options'] = 'allwrite noclobber nocompress unlocked nomodtime normdir'
        p4.save_client(client)

        # Sync workspace with server
        p4.run_sync('-f')
    
    except P4Exception as e:
        print(e)
    
    return p4