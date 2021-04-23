import pprint
import os
import shutil
import json
from P4 import P4, P4Exception
from sharedfuncs import loadConfig, perforceInit

def setupPerforce():

    # Load information from config files
    config = loadConfig("config.json")

    try:
        # Perforce login and initialize workspace
        p4 = perforceInit(config)

        # Create directory layout
        os.makedirs('root-ws/src')
        os.makedirs('root-ws/bin')
        # build script
        shutil.copyfile("resources/build.sh",  "root-ws/build.sh")
        os.chmod("root-ws/build.sh", 509) # execute permission for script
        # src files
        shutil.copyfile("resources/file1.txt", "root-ws/src/file1.txt")
        shutil.copyfile("resources/file2.txt", "root-ws/src/file2.txt")

        # Add new files
        p4.run_add('root-ws/build.sh')
        p4.run_add('root-ws/src/file1.txt')
        p4.run_add('root-ws/src/file2.txt')

        # Submit changes
        change = p4.fetch_change()
        change._description = "Initial setup of files"
        p4.run_submit(change)
        
        # Disconnect
        p4.disconnect()

        print("Initial depot setup completed")
    except P4Exception as e:
        print(e)

if __name__ == "__main__":
    setupPerforce()

