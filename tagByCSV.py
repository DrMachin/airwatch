#!/Library/Frameworks/Python.framework/Versions/3.6/bin/python3
"""
	Tag all devices based on provided CSV.
"""

from toolbox.AirWatchAPI import AirWatchAPI as airwatch
import argparse
import csv

parser = argparse.ArgumentParser(description='Add tag to specified devices based on provided CSV')
parser.add_argument("tag", help='Name of tag to be added to device(s)', type=str)
parser.add_argument("-csv", help='CSV file to import', type=str, required=True)
parser.add_argument("-header", help='CSV column header', type=str, required=True)
parser.add_argument('--remove', help='Remove specified tag from device', action="store_true")
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

deviceList = []
with open(args.csv, 'r') as inFile:
	reader = csv.DictReader(inFile)
	for line in reader:
		if str(args.header) in line:
			deviceList.append(line[args.header])

listLength = len(deviceList)

if listLength > 0:
	newTag = getTagID(args.tag)
	if newTag is not None:
		if not args.remove:
			response = api.tagDevice(newTag, bulkDevices=deviceList, verbose=True)
		else:
			response = api.tagDevice(newTag, bulkDevices=deviceList, remove=True, verbose=True)
		print("\nResponse from Server:")
		print(api.prettyJSON(response))
else:
	print("No items found in list")