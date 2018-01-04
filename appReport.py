#!/Library/Frameworks/Python.framework/Versions/3.6/bin/python3

from toolbox.AirWatchAPI import AirWatchAPI as airwatch

api = airwatch()

print(api.prettyJSON(api.searchApplications(bundleID='com.airwatch.email')))