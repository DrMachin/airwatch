#!/Library/Frameworks/Python.framework/Versions/3.6/bin/python3

from toolbox.AirWatchAPI import AirWatchAPI as airwatch
import argparse

"""	Accepted Arguments	"""
parser = argparse.ArgumentParser(description='Search and Report on Deployed Apps')
parser.add_argument("name", help='Name of app', type=str)
parser.add_argument('-platform', help='App Platform (android | apple | windowsphone8)')
parser.add_argument('-inactive', help='Also include inactive apps', action="store_true")
parser.add_argument('-vpp', help='Search VPP apps', action="store_true")

args = parser.parse_args()

if not args.inactive:
	appActive = True
else:
	appActive = None

if args.vpp:
	appType = 'purchased'
else:
	appType = None

api = airwatch()

search = api.searchApplications(args.name, appType=appType, platform=args.platform, active=appActive)

appList = search['Application']

#print(api.prettyJSON(appList))

for app in appList:
	print(str(app['Id']['Value']) + ' - ' + app['ApplicationName'])
	print('  Type: ', app['AppType'])
	print('  BundleID:', app['BundleId'])
	if not args.vpp:
		print('  Devices Assigned: ', app['AssignedDeviceCount'])
		print('  Devices Installed:', app['InstalledDeviceCount'])
	else:
		print('  Total Licenses:', app['ManagedDistribution']['Purchased'])
		print('  Redeemed:      ', app['ManagedDistribution']['Burned'])
		print('  On Hold:       ', app['ManagedDistribution']['OnHold'])
		print('  Available:     ', app['ManagedDistribution']['Available'])

#"""