#!/Library/Frameworks/Python.framework/Versions/3.6/bin/python3

from toolbox.AirWatchAPI import AirWatchAPI as airwatch
import argparse

"""	Accepted Arguments """
parser = argparse.ArgumentParser(description='Update apps assigned to Smart Group')
parser.add_argument("smartgroup", help='Find apps assigned to smart group')
parser.add_argument("-orgID", help='Update devices in specified organization group', type=str)

args = parser.parse_args()

api = airwatch()
orgID = None

"""SEARCH FOR SMART GROUP"""
data = api.findSmartGroup(args.smartgroup)
if data is None:
	print('No Smart Groups Found')
	quit()
else:
	if len(data['SmartGroups']) > 1:
		print('Found multiple groups matching name:')
		for group in data['SmartGroups']:
			print('\t' + group['Name'])
		quit()
	else:
		print('Found group:')
		print('\t' + data['SmartGroups'][0]['Name'])
		confirm = input("Is this correct? [y]") or 'y'
		if confirm != 'y':
			quit()
		else:
			groupID = data['SmartGroups'][0]['SmartGroupID']
			appList = api.getSmartGroupAppList(groupID)

			if args.orgID is not None:
				ogSearch = api.findOrganizationGroup(groupID=args.orgID)
				if ogSearch is None:
					print('Organization Group Not Found')
					quit()
				else:
					print('\n** Filtering Update to', ogSearch['OrganizationGroups'][0]['Name'] + ' **')
					orgID = ogSearch['OrganizationGroups'][0]['Id']

			if appList is None or len(appList) == 0:
				print('No Apps assigned to Smart Group')
				quit()
			else:
				print("\nID  | Name")
				idList = []
				for app in appList:
					print(app['id'], '|', app['applicationName'])
					idList.append(str(app['id']))
				print()
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
				print('\n---- Starting Update Spam ----\n')

				first = True

				if orgID is None:
					for device in api.getSmartGroupDeviceDetails(groupID)['Devices']:
						print(device['Name'], device['Id'])
						if updateAll:
							for app in appList:
								print(app['applicationName'], api.installPurchasedApp(app['id'], deviceID=device['Id']))
						else:
							print(api.installPurchasedApp(appID, deviceID=device['Id']))
				else:
					if updateAll:
						for app in appList:
							deviceList = api.getDevicesAssignedToPurchasedApp(appID=app['id'], orgID=orgID, status='Assigned')['DeviceId']
							for device in deviceList:
								print(app['applicationName'], api.installPurchasedApp(app['id'], deviceID=device))
					else:
						deviceList = api.getDevicesAssignedToPurchasedApp(appID=app['id'], orgID=orgID, status='Assigned')['DeviceId']
						for device in deviceList:
							print(api.installPurchasedApp(appID, deviceID=device))