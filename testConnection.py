#!/Library/Frameworks/Python.framework/Versions/3.6/bin/python3

from toolbox.AirWatchAPI import AirWatchAPI as airwatch

api = airwatch()

conTest = api.testRequest()
if conTest:
	print('Connected Successfully')
else:
	print(conTest)