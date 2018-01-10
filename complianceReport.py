#!/Library/Frameworks/Python.framework/Versions/3.6/bin/python3

from toolbox.AirWatchAPI import AirWatchAPI as airwatch

api = airwatch()

for device in search['Devices']:
	if device['EnrollmentStatus'] == 'Enrolled' and device['LocationGroupName'] != 'Disabled':
		for policy in device['ComplianceSummary']['DeviceCompliance']:
			if policy['PolicyName'] == 'iOS AirWatch Agent Policy':
				print(api.prettyJSON(device))
				input()