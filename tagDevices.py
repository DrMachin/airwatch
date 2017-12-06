#!/Library/Frameworks/Python.framework/Versions/3.6/bin/python3

from toolbox.AirWatchAPI import AirWatchAPI as airwatch
import argparse
import sys

""" CONSTANTS """
SUPERVISED_TAG = 'Supervised'

"""	Accepted Arguments	"""
parser = argparse.ArgumentParser(description='Add tag to specified devices',
							epilog="--serial or --deviceID must be specified")
parser.add_argument("tag", help='Name of tag to be added to device(s)', type=str, nargs='?', default=None)
parser.add_argument("-l", "--list", help='List all available Tags', action="store_true")
parser.add_argument('-s', "--serial", help='Tag specified device using serial number')
parser.add_argument('-id', "--deviceID", help='Tag specified device using device id')
parser.add_argument('-dep', '--supervised', help='Tag all DEP/Supervised iOS devices with Supervised tag', action="store_true")
#parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")

args = parser.parse_args()

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


def tagDevice(tagID, deviceID=None, deviceList=None):
	response = None
	if deviceID is not None:
		response = api.tagDevice(tagID,deviceID=deviceID,verbose=True)
	elif deviceList is not None:
		response = api.tagDevice(tagID,bulkDevices=deviceList,verbose=True)

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
			print('Tag Count:', len(deviceList))

	print()
	print("Devices Tagged:", accepted)
	print("Devices Ignored:", ignored)
	print()
	if len(faults) > 0:
		print()
		print("*****Errors Report*****")
		print(api.prettyJSON(faults))

## Get list of Tags when -l or --list is used
if args.list:
	print('Finding available tags\n')
	tagList = searchTags()
	if tagList is not None:
		output = 'Found the following tags:\n'
		for tag in tagList:
			output += ' * ' + tag['TagName'] + '\n'
		print(output)
	sys.exit(0)

## No arguments provided
if args.tag is None and not args.supervised:
	parser.print_help()
	sys.exit(0)

## Check if device or serial provided are found/valid then try to tag
elif not args.supervised:
	deviceID = None
	print('Finding device')
	if args.serial or args.deviceID:
		if args.serial is not None:
			aSerial = args.serial
			search = api.getDeviceInformation(serialNumber=aSerial)
			if 'ErrorCode' not in search:
				deviceID = search['Id']['Value']
			else:
				print(search['Message'])
		elif args.deviceID is not None:
			aID = args.deviceID
			search = api.getDeviceInformation(deviceID=aID)
			if 'ErrorCode' not in search:
				deviceID = aID
			else:
				print(search['Message'])
		if deviceID is None:
			sys.exit(0)
		else:
			tagID = getTagID(args.tag)
			if tagID is not None:
				tagDevice(tagID, deviceID)
	else:
		parser.print_help()
		sys.exit(0)
elif args.supervised:
	## Get Full Device List

	print('Getting updated device list')
	search = api.searchDevices()
	tCount = sCount = 0
	if search is None:
		print('Unable to retrieve device list.')
		sys.exit(0)

	supervisedTag = getTagID(SUPERVISED_TAG)

	##	Get List of curently tagged devices
	print('Getting current list of tagged devices')
	tagSearch = api.getTaggedDevices(supervisedTag)
	if tagSearch is None:
		print('Unable to retrieve tagged device list.')
		sys.exit(0)

	## Create lists and compare

	print('Processing device list')
	taggedList = []
	for device in tagSearch['Device']:
		taggedList.append(device['DeviceId'])

	supervisedList = []
	for device in search['Devices']:
		if device['IsSupervised']:
			supervisedList.append(device['Id']['Value'])

	deviceList = []
	for device in supervisedList:
		if device not in taggedList:
			deviceList.append(device)
	
	## Send request to AirWatch

	if len(deviceList) < 1:
		print('\nNo new devices found.')
	else:
		print('Sending request to AirWatch')
		response = api.tagDevice(supervisedTag,bulkDevices=deviceList,verbose=True)

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
				print('Tag Count:', len(deviceList))


		print()
		print("Devices Tagged:", accepted)
		print("Devices Ignored:", ignored)
		print()
		if len(faults) > 0:
			print()
			print("*****Errors Report*****")
			print(api.prettyJSON(faults))
	#"""