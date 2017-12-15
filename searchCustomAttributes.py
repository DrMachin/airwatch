#!/Library/Frameworks/Python.framework/Versions/3.6/bin/python3

from toolbox.AirWatchAPI import AirWatchAPI as airwatch
from toolbox.csvReport import csvReport
import argparse
import sys

""" Accepted Arguments """
parser = argparse.ArgumentParser(description='AirWatch Custom Attributes Search')
parser.add_argument('name', help='Get list of devices with matching attribute name')
parser.add_argument("-l", "--list", help='List all available attributes', action="store_true")
parser.add_argument('-find', help='Find attribute with matching name')
parser.add_argument('-csv', help='Get list of devices with matching attribute')

args = parser.parse_args()

api = airwatch()

def searchAttributes(name=None, orgID=None):
	caSearch = api.searchCustomAttributes(name, orgID)
	if caSearch is None:
		return None
	else:
		return caSearch['CustomAttributes']

def listNames(name=None, attribList=None):
	if attribList is None:
		caList = searchAttributes(name)
	else:
		caList = attribList
	if caList is None:
		print('No Attributes found.')
		sys.exit(0)
	else:
		print('\nAttributes found:')
		for attributes in caList:
			print('\t' + attributes['Name'])

if args.list:
	print('Finding all available attributes')
	listNames()
	sys.exit(0)

if args.find:
	print('Looking for all matching attributes')
	listNames(args.find)
	sys.exit(0)

if args.name:
	attribName = args.name
	print('\nLooking for devices with matching attribute')
	search = searchAttributes(attribName)
	if search is None:
		print('No Attributes Found')
	elif len(search) > 1:
		print('More than one attribute matches requested name')
		listNames(attribList=search)
	else:
		attribName = search[0]['Name']
		print('Getting list of all devices with attributes')
		deviceList = api.searchDeviceCustomAttributes()

		print()
		report = []
		for device in deviceList['Devices']:
			value = None
			curAttrib = None
			for attribute in device['CustomAttributes']:
				if attribute['Name'] == attribName:
					device['CustomAttributes'] = [attribute]
					report.append(device)
					break

		if args.csv:
			print('Exporting report to CSV')
			cReport = csvReport(args.csv)
			cReport.jsonToCsv(report)
		else:
			print(api.prettyJSON(report))
#"""