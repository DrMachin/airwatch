# AirWatch API Scripts
## About
Set of python scripts I use regularly to manage my AirWatch instance.  These were made to be run on macOS. Most things should work on other platforms, but may need some modifying.

**USE AT YOUR OWN RISK**

I am fairly new to Python scripting and this is my way of teaching myself. I provide no warranty or support. This can (and probably will) cause issues if used improperly. You have been warned.


## Requirements
Python 3

[keyring](https://pypi.python.org/pypi/keyring) — Python Library used for storing passwords to Keychain

### “Tested” on:
AirWatch Console v.9.1.4

macOS High Sierra 10.13.1

Python 3.6.3


## Password and Environment Details
On first run, the script will ask for environment details.

Host, username, and Customer Org Group ID are stored to a pList file (toolbox.airwatchapi.plist) in the user preferences folder on first run.

User authentication and tenant api key hashes are stored in the user’s keychain. The keys are airwatch_api_user and airwatch_api_tenant.

Is it secure? Maybe, not really sure. I’m still figuring this out.
