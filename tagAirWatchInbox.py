#!/Library/Frameworks/Python.framework/Versions/3.6/bin/python3

"""
	Find devices AirWatch Inbox app and tag them

	Creating this to migrate devices from AirWatch Inbox to VMWare Boxer.
	Step 1: Identify all devices with AW Inbox installed
	Step 2: Tag All devices
	Step 3: Create smart group with 'AWInbox' tag
	Step 4: Limit Inbox Assignment to 'AWInbox' Group
		-- This should stop new devices from getting inbox without removing existing users
	Go from there...
"""

from toolbox.AirWatchAPI import AirWatchAPI as airwatch

api = airwatch()

def searchTags():
	## Get List of all Tags from Airwatch
	## tagDevice(self, tagID, deviceID=None, bulkDevices=None, verbose=False):
	search = api.searchTag()
	if search is None:
		print('No tags available.')
		return None
	else:
		return search['Tags']
	return 0

def getTagID(tagName):
	## Get ID for specified Tag
	tagID = None
	tagList = searchTags()
	if tagList is not None:
		for tag in tagList:
			if tag['TagName'] == str(tagName):
				tagID = tag['Id']['Value']
				break
	if tagID is None:
		print('Could not find tag with name:', tagName)
	return tagID

search = api.searchApplications('AirWatch Inbox')

appList = search['Application']

tagID = getTagID('AirWatch Inbox')

#"""
for app in appList:
	appID = app['Id']['Value']
	appName = app['ApplicationName']
	print(str(appID) + ' - ' + appName)
	deviceList = api.getDevicesWithInstalledPublicApp(appID)
	if deviceList is not None:
		idList = deviceList['DeviceId']
		if len(idList) < 1:
			print('\nNo devices found.')
		else:
			print('Sending request to AirWatch')
			response = api.tagDevice(tagID, bulkDevices=idList, verbose=True)

			accepted = failed = ignored = 0
			faults = []

			if response is not None:
				try:
					accepted = response['AcceptedItems']
					failed = response['FailedItems']
					if failed > 0:
						for error in response['Faults']['Fault']:
							if error['ErrorCode']:
								ignored += 1
							else:
								faults.append(error)
				except KeyError:
					print(api.prettyJSON(response))
					print('Tag Count:', len(idList))

			print()
			print("Devices Tagged:", accepted)
			print("Devices Ignored:", ignored)
			print()
			if len(faults) > 0:
				print()
				print("*****Errors Report*****")
				print(api.prettyJSON(faults))
	else:
		print('\nNo devices found.')
#"""