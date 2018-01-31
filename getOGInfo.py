#!/Library/Frameworks/Python.framework/Versions/3.6/bin/python3

from toolbox.AirWatchAPI import AirWatchAPI as airwatch
import argparse

"""	Accepted Arguments """
parser = argparse.ArgumentParser(description='Search and Print Organization Group Info')
parser.add_argument("name", help='Name of Organization Group')

args = parser.parse_args()

api = airwatch()

print(api.prettyJSON(api.findOrganizationGroup(args.name)['OrganizationGroups']))