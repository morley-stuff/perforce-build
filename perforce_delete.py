import pprint
import shutil
import os
import json
from P4 import P4, P4Exception
from sharedfuncs import loadConfig, perforceInit

def perforceDelete():
# Load information from config files
    config = loadConfig("config.json")

    try:
        # Perforce login and initialize workspace
        p4 = perforceInit(config)

        # Delete everything
        p4.run_delete('//depot/...')
        change = p4.fetch_change()
        change._description = "This change deletes everything in the depot"
        p4.run_submit(change)
        
        print("All files deleted from depot")

        p4.disconnect()

    except P4Exception as e:
        print(e)

    if os.path.exists('root-ws'):
        shutil.rmtree('root-ws')

if __name__ == "__main__":
    perforceDelete()