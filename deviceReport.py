#!/Library/Frameworks/Python.framework/Versions/3.6/bin/python3

from toolbox.AirWatchAPI import AirWatchAPI as airwatch
from toolbox.csvReport import csvReport
import argparse

parser = argparse.ArgumentParser(description='Get Device Information')
parser.add_argument("-serialnumber", help='Search by serial number', type=str)
parser.add_argument("-deviceID", help='Search by device ID', type=str)
parser.add_argument("-easID", "-easid", help='Search by Exchange ActiveSync ID', type=str)
parser.add_argument("-username", help='Search for all devices associated to enrolled username', type=str)
parser.add_argument('-csv', help='Export results to csv')

args = parser.parse_args()

api = airwatch()

if args.serialnumber:
	search = api.getDeviceInformation(serialNumber=args.serialnumber)
elif args.deviceID:
	search = api.getDeviceInformation(deviceID=args.deviceID)
elif args.easID:
	search = api.getDeviceInformation(easID=args.easID)
elif args.username:
	search = api.searchDevices(username=args.username)
else:
	parser.print_help()
	quit()

if not 'errorCode' in search.keys():
	if args.csv:
		print('Exporting report to CSV')
		cReport = csvReport(args.csv)
		cReport.jsonToCsv(search)
	else:
		print(api.prettyJSON(search))
else:
	print(search['message'])