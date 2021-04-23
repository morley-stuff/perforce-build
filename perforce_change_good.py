import pprint
import os
import shutil
import subprocess
import json
from sharedfuncs import loadConfig, perforceInit
from P4 import P4, P4Exception

def goodChange():

    # Load information from config files
    config = loadConfig("config.json")

    try:
        # Perforce login and initialize workspace
        p4 = perforceInit(config)

        # Make a change to src files
        f = open("root-ws/src/file1.txt", 'a')
        f.write("This is a good change\n")
        f.close()

        # Reconcile src directory, submitting any changes
        try:
            p4.run_reconcile("//depot/src/...")
            change = p4.fetch_change()
            change._description = "This change updates src files safely"
            p4.run_submit(change)
            print("Submitted safe changes")
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
    goodChange()


