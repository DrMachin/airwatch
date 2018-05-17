#!/Library/Frameworks/Python.framework/Versions/3.6/bin/python3

from toolbox.AirWatchAPI import AirWatchAPI as airwatch
import argparse
import re

"""	Accepted Arguments """
parser = argparse.ArgumentParser(description='Update apps assigned to Smart Group')
parser.add_argument("-smartgroup", help='Find apps assigned to smart group', type=str)
parser.add_argument("-serialnumber", help='Find apps assigned to device by serial number', type=str)
parser.add_argument("-deviceID", help='Find apps assigned to device by serial number', type=str)
parser.add_argument("-orgID", help='Only update devices in specified organization group', type=str)

args = parser.parse_args()

if not args.smartgroup and not args.serialnumber and not args.deviceID:
	args.error ('Either -smartgroup, -serialnumber or -deviceID is required.')
	quit()

api = airwatch()
appList = orgID = deviceID = None

"""SEARCH FOR SMART GROUP"""
if args.smartgroup:
	data = api.findSmartGroup(args.smartgroup)
	if data is None:
		print('\nNo Smart Groups Found')
		quit()
	else:
		if len(data['SmartGroups']) > 1:
			print('\nFound multiple groups matching name:')
			for group in data['SmartGroups']:
				print('\t' + group['Name'])
			quit()
		else:
			print('\nShowing Apps for', data['SmartGroups'][0]['Name'])
			
			groupID = data['SmartGroups'][0]['SmartGroupID']
			appList = api.getSmartGroupAssignedApps(groupID)

if args.serialnumber:
	device = api.getDeviceInformation(serialNumber=args.serialnumber)
	if 'errorCode' not in device:
		deviceID = device['Id']['Value']
	else:
		print('Device was not found')
		quit()

if args.deviceID:
	device = api.getDeviceInformation(deviceID=args.deviceID)
	if 'errorCode' not in device:
		deviceID = args.deviceID
	else:
		print('Device was not found')
		quit()

if deviceID is not None and not args.smartgroup:
	data = api.getDeviceAppDetails(deviceID=deviceID)
	appList = data['DeviceApps']

if args.orgID is not None:
	ogSearch = api.findOrganizationGroup(groupID=args.orgID)
	if ogSearch is None:
		print('Organization Group Not Found')
		quit()
	else:
		print('\n** Filtering Update to', ogSearch['OrganizationGroups'][0]['Name'] + ' **')
		orgID = ogSearch['OrganizationGroups'][0]['Id']

if args.serialnumber or args.deviceID and appList is not None:
	if args.smartgroup is None:
		## Clean Normalize the data
		tempList = []
		for app in appList:
			if app['IsManaged']:
				app['applicationName'] = app['ApplicationName']
				app['id'] = app['Id']['Value']
				app.pop('ApplicationName')
				app.pop('Id')
				tempList.append(app)
		appList = tempList
		print('\nShowing Apps for device', deviceID)

if appList is None or len(appList) == 0:
	print('No Apps Found')
	quit()
else:
	print("\nID\t| Name")
	idList = []
	for app in appList:
		print(app['id'], '\t|', re.split(r" - | – ", app['applicationName'])[0])
		idList.append(str(app['id']))
	print()
	#quit()
	appID = input('Press Enter to Update All or Enter ID of app to update: ')
	updateAll = False
	if not appID:
		updateAll = True
		confirm = input('UPDATE ALL? Type yes:')
		if confirm not in ('y', 'yes'):
			quit()
	elif appID not in idList:
		print('ID is not assigned to smart group.')
		quit()
	else:
		for app in appList:
			if app['id'] == int(appID):
				print('Updating', app['applicationName'])
				confirm = input('Is this correct:[n]')
				if confirm in ('y', 'yes'):
					break
				quit()
	print('\n---- Starting Update ----\n')

	if orgID is None and args.smartgroup:
		if deviceID is not None:
			print('\nUpdating Device:', device['Id'])
			if updateAll:
				for app in appList:
					print(app['applicationName'], api.installPurchasedApp(app['id'], deviceID=deviceID))
			else:
				print(api.installPurchasedApp(appID, deviceID=deviceID))
		else:
			for device in api.getSmartGroupDeviceDetails(groupID)['Devices']:
				print(device['Name'], device['Id'])
				if updateAll:
					for app in appList:
						print(app['applicationName'], api.installPurchasedApp(app['id'], deviceID=device['Id']))
				else:
					print(api.installPurchasedApp(appID, deviceID=device['Id']))
	elif orgID:
		if updateAll:
			for app in appList:
				deviceList = api.getDevicesAssignedToPurchasedApp(appID=app['id'], orgID=orgID, status='Assigned')['DeviceId']
				for device in deviceList:
					print(app['applicationName'], api.installPurchasedApp(app['id'], deviceID=device))
		else:
			deviceList = api.getDevicesAssignedToPurchasedApp(appID=app['id'], orgID=orgID, status='Assigned')['DeviceId']
			for device in deviceList:
				print(api.installPurchasedApp(appID, deviceID=device))
	elif deviceID is not None:
		if updateAll:
			for app in appList:
				print(app['applicationName'], api.installPurchasedApp(app['id'], deviceID=deviceID))
		else:
			print(app['applicationName'], api.installPurchasedApp(app['id'], deviceID=deviceID))
