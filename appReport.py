#!/Library/Frameworks/Python.framework/Versions/3.6/bin/python3

from toolbox.AirWatchAPI import AirWatchAPI as airwatch
import argparse

"""	Accepted Arguments	"""
parser = argparse.ArgumentParser(description='Search and Report on Deployed Apps')
parser.add_argument("name", help='Name of app', type=str)
parser.add_argument('-platform', help='App Platform (android or apple)')

args = parser.parse_args()


api = airwatch()

print(api.prettyJSON(api.searchApplications(args.name, platform=args.platform)))