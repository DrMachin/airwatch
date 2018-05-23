#!/Library/Frameworks/Python.framework/Versions/3.6/bin/python3

from toolbox.AirWatchAPI import AirWatchAPI as airwatch
import argparse
import os
import csv
import sys

parser = argparse.ArgumentParser(description='Cross reference csv file with AirWatch')
parser.add_argument("-csv", help='CSV file to import', type=str)
parser.add_argument("-header", help='CSV column header', type=str)
parser.add_argument("-output", "-out", help='Specify Output CSV file', type=str)
parser.add_argument('-searchBy', help='Search by SerialNumber, DeviceID, or EASID', type=str)

args = parser.parse_args()

if args.csv:
	if not args.header:
		print('Please specify column header')
		quit()
	if not args.searchBy:
		print('Please specify search type: SerialNumber, DeviceID, or EASID')
		quit()
	api = airwatch()
	import csv
	csvlist = []
	outputlist = []
	with open(args.csv, 'r') as inFile:
		reader = csv.DictReader(inFile)
		for line in reader:
			csvlist.append(line)
	listLength = len(csvlist)
	csvHeader = None
	progress = 0
	print()
	for item in csvlist:
		progress += 1
		sys.stdout.write('\rProcessing ' + str(progress) + ' of ' + str(listLength) + ' items.')
		sys.stdout.flush()
		if args.searchBy.lower() == 'serialnumber' or args.searchBy.lower() == 'serial':
			search = api.getDeviceInformation(serialNumber=item[args.header])
		elif args.searchBy.lower() == 'deviceid':
			search = api.getDeviceInformation(deviceID=item[args.header])
		elif args.searchBy.lower() == 'easid':
			search = api.getDeviceInformation(easID=item[args.header])
		else:
			print('Unknown search type: SerialNumber, DeviceID, or EASID')
		newItem = {}
		if not 'errorCode' in search.keys():
			item['AirWatchDeviceID'] = str(search['Id']['Value'])
			item['DeviceFriendlyName'] = search['DeviceFriendlyName']
			item['EnrollmentStatus'] = search['EnrollmentStatus']
			item['Model'] = search['Model']
			item['LastEnrolledOn'] = search['LastEnrolledOn']
			item['LastSeen'] = search['LastSeen']
			item['Ownership'] = search['Ownership']
			item['SerialNumber'] = search['SerialNumber']
			item['UserName'] = search['UserName']
			if csvHeader is None:
				csvHeader = item.keys()
		elif search['errorCode'] == 404:
			item['EnrollmentStatus'] = 'Not Found'
		else:
			print(search['errorCode'])
			print(search['message'])
			input()
		outputlist.append(item)
	if csvHeader is not None:
		if args.output:
			outputFile = args.output
		else:
			directory = os.path.dirname(args.csv)
			inFileName, file_extension = os.path.splitext(os.path.basename(args.csv))
			filename = inFileName + '-report.csv'
			outputFile = directory + '/' + filename
		with open(outputFile, 'w') as output_file:
		    dict_writer = csv.DictWriter(output_file, csvHeader)
		    dict_writer.writeheader()
		    dict_writer.writerows(outputlist)
		print('Success')
	else:
		print('No devices found')
else:
	parser.print_help()
	quit()