Requirements
 - Python 3

This project utilizes the python script 'perforce_build.py' to perform the build for a project stored in perforce.

Access credentials to the Perforce server and an SMTP server for sending build notifications can be configured within the file 'config.json' as seen in 'config.json.sample'

The script assumes a layout similar to:
-depot/
  -src/
  -bin/
  -build.sh
  -build.bat 

build.sh / build.bat will be run dependant on the host operating system.

On failure a notification with information about recent changes to the perforce project is sent out to the recipients specified in 'config.json'

This project also contains a full integration test scenario for the build script as 'test_suite.py'. The test suite sets up a perforce project in a default state and then performs various changes against it to confirm the result of the build.