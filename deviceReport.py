#!/Library/Frameworks/Python.framework/Versions/3.6/bin/python3

from toolbox.AirWatchAPI import AirWatchAPI as airwatch
import argparse

parser = argparse.ArgumentParser(description='Get Device Information')
parser.add_argument("-serialnumber", help='Search by serial number', type=str)
parser.add_argument("-deviceID", help='Search by device ID', type=str)
parser.add_argument("-easID", "-easid", help='Search by Exchange ActiveSync ID', type=str)

args = parser.parse_args()

api = airwatch()

if args.serialnumber:
	search = api.getDeviceInformation(serialNumber=args.serialnumber)
elif args.deviceID:
	search = api.getDeviceInformation(deviceID=args.deviceID)
elif args.easID:
	search = api.getDeviceInformation(easID=args.easID)
else:
	parser.print_help()
	quit()

print(api.prettyJSON(search))
