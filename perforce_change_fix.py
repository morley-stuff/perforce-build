import pprint
import os
import shutil
import subprocess
import json
from sharedfuncs import loadConfig, perforceInit
from P4 import P4, P4Exception

def fixChange():
    # Load information from config files
    config = loadConfig("config.json")

    try:
        # Perforce login and initialize workspace
        p4 = perforceInit(config)

        # Make a change to src files
        os.rename("root-ws/src/file3.txt", "root-ws/src/file2.txt")

        # Reconcile src directory, submitting any changes
        try:
            p4.run_reconcile("//depot/src/...")
            change = p4.fetch_change()
            change._description = "This change fixes the error introduced previously"
            p4.run_submit(change)
            print("Submitted a change that will fix the build")
        except P4Exception as e:
            # Warning "No files to reconcile" throws an exception so let's ignore it
            #   and print some nicer output.
            if 'Error' not in str(e):
                print("No changes to submit")
            else:
                raise(e)
        
        # Disconnect
        p4.disconnect()

    except P4Exception as e:
        print(e)

if __name__ == "__main__":
    fixChange()

