"""
	TESTED ON:
		Python 3.6.3
		macOS High Sierra 10.13.1
		AirWatch Console v.9.1.4
"""
from urllib.parse import quote
from pathlib import Path
from time import strftime
import http.client
import json
import hashlib
import os.path
import plistlib
from .password_store import keychain

class AirWatchAPI:
	"""Make requests to AirWatch API"""

	__HOST 			= ['host', '']
	__AUTH 			= ['authorization', '']
	__TENANT_CODE 	= ['aw-tenant-code', '']
	__USERNAME		= ''
	__CUSTOMER_OG	= ''

	"""	SETTINGS LOCATION """
	__plistFileName = 'toolbox.airwatchapi.plist'
	__plistFileLocation = str(Path.home()) + '/Library/Preferences/'
	__keychainRoot = 'airwatch_api'
	#"""
	
	"""  SERVER CONSTANTS"""
	__USER_AGENT 	= ['user-agent', ":Fiddler"]
	__UNIQUE_TOKEN 	= ['unique-token', hashlib.md5(strftime("%A %d %B %Y %H%M%S").encode()).hexdigest()]
	__CACHE 		= ['cache-control', "no-cache"]
	__RESPONSE_TYPE	= ['accept', "application/json;version=2"]
	__CONTENT_TYPE	= ['content-type', "application/x-www-form-urlencoded"]
	
	"""API URIS"""
	__APIURI = "/api"
	"""		Mobile Device Management """
	__APIURI_MDM			= __APIURI      		+ "/mdm"
	__APIURI_MDM_DEVICE		= __APIURI_MDM  		+ "/devices"
	__APIURI_MDM_DEVICE_CA	= __APIURI_MDM_DEVICE 	+ "/customattribute"
	"""		Mobile Application Management """
	__APIURI_MAM	 		= __APIURI      		+ "/mam"
	__APIURI_MAM_APPS		= __APIURI_MAM 			+ "/apps"
	__APIURI_MAM_PUB		= __APIURI_MAM_APPS		+ "/public"
	__APIURI_MAM_VPP		= __APIURI_MAM_APPS		+ "/purchased"
	"""		Mobile Content Management	"""
	__APIURI_MCM 			= __APIURI      		+ "/mcm"
	"""		Mobile Email Management		"""
	__APIURI_MEM 			= __APIURI      		+ "/mem"
	"""		System Administration		"""
	__APIURI_SYS			= __APIURI      		+ "/system"
	"""		Enrollment User Management	"""
	__APIURI_EUSER			= __APIURI_SYS 			+ "/users"
	"""		Organization Group Management """
	__APIURI_OGM			= __APIURI_SYS  		+ "/groups"
	"""		Smart Group Management	"""
	__APIURI_MDM_SG 		= __APIURI_MDM 			+ "/smartgroups"
	"""		Tag Management	"""
	__APIURI_MDM_TAGS 		= __APIURI_MDM 			+ "/tags"
	"""		Custom Attribute Management	"""
	__APIURI_SYS_CA			= __APIURI_SYS 			+ "/customattributes"

	"""----- OTHER OPTIONS -----"""
	__PAGESIZE = "pagesize=500000"

	"""----- END CONSTANTS -----"""

	def __init__(self, dev=False):
		self.data = []
		self.__loadSettings()

	"""	READ / WRITE SETTINGS PLIST 	"""
	def __loadSettings(self, dev=False):
		plistFile = self.__plistFileLocation + self.__plistFileName
		fileStatus = os.path.exists(plistFile)

		keys_user = keychain(self.__keychainRoot + '_user')
		keys_tent = keychain(self.__keychainRoot + '_tenant')

		conStatus = None

		while conStatus != True:
			if not fileStatus or conStatus is not None:
				if conStatus is None:
					print('Settings Not Found')
				else:
					print(conStatus)

				pl = dict(
					host = input('Enter Server Address: '),
					auth = 'Basic',
					username = keys_user.login()
					)

				keys_tent.login(username=pl['username'], key=True)

				plistlib.writePlist(pl, plistFile)
			
			plist = plistlib.readPlist(plistFile)

			self.__HOST[1]		 = plist['host']
			self.__USERNAME		 = plist['username']
			self.__AUTH[1]		 = plist['auth'] + ' ' + keys_user.get_password(self.__USERNAME)
			self.__TENANT_CODE[1] = keys_tent.get_password(self.__USERNAME, key=True)
			conStatus = self.testRequest()
			if 	'customerOG' in plist:
				self.__CUSTOMER_OG = str(plist['customerOG'])
			elif conStatus:
				ogSearch = self.findOrganizationGroup(type='Customer')
				plist['customerOG'] = ogSearch['OrganizationGroups'][0]['Id']
				plistlib.writePlist(plist, plistFile)

	def __loadJSON(self, data):
		if not data:
			return None # Empty String received
		else:
			return json.loads(data)

	def prettyJSON(self, data):
		 return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))

	def __formatParameters(self, pList):
		#for joining long parameter strings
		param = '?' + self.__PAGESIZE
		for item in pList:
			param += '&' + item
		return param

	""" API CONNECTION AND REQUEST TYPES	"""
	def apiConnect(self, method, url, body=None, contentType=None):
		"""Make HTTPS connection to AirWatch"""
		conn = http.client.HTTPSConnection(self.__HOST[1])

		if contentType is None:
			cType = self.__CONTENT_TYPE[1]
		elif contentType == 'json':
			cType = 'application/json'
		else:
			return 'Invalid Content Type'

		headers = {
		    self.__AUTH[0]: self.__AUTH[1],
		    self.__USER_AGENT[0]: self.__USER_AGENT[1],
		    self.__HOST[0]: self.__HOST[1],
		    self.__TENANT_CODE[0]: self.__TENANT_CODE[1],
		    self.__CACHE[0]: self.__CACHE[1],
		    self.__UNIQUE_TOKEN[0]: self.__UNIQUE_TOKEN[1],
		    self.__RESPONSE_TYPE[0]: self.__RESPONSE_TYPE[1],
		    self.__CONTENT_TYPE[0]: cType
		    }

		conn.request(method, url, body=body, headers=headers)
		return conn

	def apiGetRequest(self, url, body=None, contentType=None):
		conn = self.apiConnect('GET', url, body, contentType)
		response = conn.getresponse()
		data = response.read()
		conn.close()
		return data.decode('utf-8')

	def apiPostRequest(self, url, body=None, contentType=None, verbose=False):
		conn = self.apiConnect('POST', url, body, contentType)
		res = conn.getresponse()
		if verbose:
			response = res.read().decode('utf-8')
		else:
			response = str(res.status) + ' ' + str(res.reason)
		conn.close()
		return response

	"""	AIRWATCH SPECIFIC REQUESTS	"""
	def testRequest(self):
		"""Make a test connection and return response"""
		conn = self.apiConnect('GET', "/api/system/info")
		response = conn.getresponse()
		conn.close()
		if response.status is 200:
			return True
		else:
			return "Error: " + str(response.status) + ' ' + str(response.reason)

	"""		Organization Group Management"""
	def getOG_deviceCount(self, groupID):
		""" Returns the Device Count for all the Organization Groups that are available 
			under the specified Organization Group.
		"""
		url = self.__APIURI_OGM + "/devicecounts?organizationgroupid" + groupID
		return self.__loadJSON(self.apiGetRequest(url))
	def findOrganizationGroup(self, name=None, type=None):
		"""Searches for Organization Group Details based on the parameters provided in the URL"""
		url = self.__APIURI_OGM + "/search"

		pList = []
		if name is not None:
			pList.append('name=' + quote(groupName))
		if type is not None:
			pList.append('type=' + type)

		param = self.__formatParameters(pList)
		return self.__loadJSON(self.apiGetRequest(url + param))

	def findOGbyName(self, groupName):
		url = self.__APIURI_OGM + "/search?name=" + quote(groupName)
		return self.__loadJSON(self.apiGetRequest(url))

	"""		Smart Group Management"""
	def findSmartGroupbyName(self, name):
		"""Searches for smart groups using the name."""
		# /mdm/smartgroups/search?name=
		url = self.__APIURI_MDM_SG + "/search?name=" + quote(name)
		return self.__loadJSON(self.apiGetRequest(url))
	def getSmartGroupDeviceDetails(self, sgroupID):
		"""Retrieves the device details in the smart group."""
		url = self.__APIURI_MDM_SG + "/" + str(sgroupID) + "/devices"
		return self.__loadJSON(self.apiGetRequest(url))
	def getSmartGroupAppList(self, sgroupID):
		"""Gets the list of apps assigned to Smart Group"""
		url = self.__APIURI_MDM_SG + "/" + str(sgroupID) + "/apps"
		return self.__loadJSON(self.apiGetRequest(url))

	"""		Mobile Device Management"""
	def searchDevices(self, username=None, model=None, platform=None, lastseen=None, ownership=None, iGID=None, compliantstatus=None, 
		seensince=None):
		""" Searches for devices using the query information provided.
		/mdm/devices/search?
		user 				--  Enrolled username
		model 				-- 	Device model
		platform			--	Device platform
		lastseen			--	Last seen date string
		ownership			--	Device ownership
		Igid				--	(Integer) Organization group to be searched, user's OG is considered if not sent
		compliantstatus		--	(Boolean) Complaint status
		seensince			--	Specifies the date filter for device search, which retrieves the devices that are seen after this date
		page 				--	Page number
		pagesize			--	Records per page
		orderby				--	Order by column name
		sortorder			--	Sorting order. Values ASC or DESC. Defaults to ASC.
		"""
		url = self.__APIURI_MDM_DEVICE + "/search"

		pList = []

		if username is not None:
			pList.append("user=" + username)
		if model is not None:
			pList.append("model=" + model)
		if platform is not None:
			pList.append("platform=" + platform)
		if lastseen is not None:
			pList.append("lastseen=" + lastseen)
		if ownership is not None:
			pList.append("ownership=" + ownership)
		if iGID is not None:
			pList.append("Igid" + iGID)
		if compliantstatus is not None:
			pList.append("compliantstatus=" + str(compromised))
		if seensince is not None:
			pList.append("seensince=" + quote(seensince))

		param = self.__formatParameters(pList)
		return self.__loadJSON(self.apiGetRequest(url + param))

	def getDeviceInformation(self, deviceID=None, serialNumber=None, macAddress=None, udid=None, imei=None, easID=None):
		""" searchby The alternate id type (Macaddress, Udid, Serialnumber, ImeiNumber, EasId)""" 
		url = self.__APIURI_MDM_DEVICE
		if deviceID is not None:
			url += "/" + str(deviceID)
		else:
			searchBy = "?searchby="
			searchID = "&id="
			if serialNumber is not None:
				searchBy += "Serialnumber"
				searchID += str(serialNumber)
			elif macAddress is not None:
				searchBy += "Macaddress"
				searchID += str(macAddress)
			elif udid is not None:
				searchBy += "Udid"
				searchID += str(udid)
			elif imei is not None:
				searchBy += "ImeiNumber"
				searchID += str(imei)
			elif easID is not None:
				searchBy += "EasId"
				searchID += str(easID)
			url += searchBy + searchID
		return self.__loadJSON(self.apiGetRequest(url))

	def queryDevice(self, deviceID):
		# mdm/devices/{id}/query
		""" command [Lock, EnterpriseWipe, DeviceWipe, DeviceQuery, ClearPasscode, SyncDevice, StopAirPlay]."""
		""" DEPRICATED -- Future support
		#url = self.__APIURI_MDM_DEVICE + "/deviceid/commands"
		payload = "id=" + str(deviceID) + "&command=DeviceQuery"
		"""
		url = self.__APIURI_MDM_DEVICE + "/" + str(deviceID) + "/query"	
		return self.apiPostRequest(url)

	def syncDevice(self, deviceID):
		# mdm/devices/{id}/query
		""" command [Lock, EnterpriseWipe, DeviceWipe, DeviceQuery, ClearPasscode, SyncDevice, StopAirPlay]."""
		""" DEPRICATED -- Future support
		#url = self.__APIURI_MDM_DEVICE + "/deviceid/commands"
		payload = "id=" + str(deviceID) + "&command=DeviceQuery"
		"""
		url = self.__APIURI_MDM_DEVICE + "/" + str(deviceID) + "/syncdevice"	
		return self.apiPostRequest(url)

	def getDeviceAppDetails(self, deviceID):
		# mdm/devices/{id}/apps
		url = self.__APIURI_MDM_DEVICE + '/' + str(deviceID) + '/apps'
		return self.__loadJSON(self.apiGetRequest(url))

	def searchDeviceCustomAttributes(self, deviceID=None, serialNumber=None, orgID=None, startdatetime=None, enddatetime=None):
		# mdm/devices/customattribute/search?organizationgroupid={organizationgroupid}&deviceid={deviceid}&serialnumber={serialnumber}&startdatetime= {startdatetime}&enddatetime={enddatetime}
		url = self.__APIURI_MDM_DEVICE + '/customattribute/search'

		pList = []

		if orgID is not None:
			pList.append("organizationgroupid=" + orgID)
		if deviceID is not None:
			pList.append("deviceid=" + deviceID)
		if deviceID is not None:
			pList.append("serialnumber=" + serialNumber)
		if startdatetime is not None:
			pList.append("startdatetime=" + startdatetime)
		if enddatetime is not None:
			pList.append("enddatetime=" + enddatetime)

		param = self.__formatParameters(pList)
		return self.__loadJSON(self.apiGetRequest(url + param))

	"""		Mobile Application Management """
	def searchApplications(self, name=None, appType=None, category=None, orgID=None, bundleID=None):
		#https://host//api/mam/apps/search?type={type}&applicationtype={applicationtype}&applicationname= {applicationname}&category={category}&locationgroupid={locationgroupid}&bundleid={bundleid}&platform= {platform}&model={model}&status={status}&orderby={orderby}&page={page}&pagesize={pagesize}
		url = self.__APIURI_MAM_APPS + '/search'
		
		pList = []

		if appType is not None:
			if appType.lower() == 'purchased':
				return self.searchVPPApplications(name)
			pList.append("applicationtype=" + appType)
		if name is not None:
			pList.append("applicationname=" + quote(name))
		if category is not None:
			pList.append("category=" + quote(appType))
		if orgID is not None:
			pList.append("locationgroupid=" + str(orgID))
		if bundleID is not None:
			pList.append("bundleid=" + quote(bundleID))
		pList.append("type=app")

		param = self.__formatParameters(pList)
		return self.__loadJSON(self.apiGetRequest(url + param))

	def searchVPPApplications(self, name):
		#/mam/apps/purchased/search
		url = self.__APIURI_MAM_VPP + '/search'

		if name is not None:
			url += "?applicationname=" + quote(name)

		return self.__loadJSON(self.apiGetRequest(url))

	def getDevicesWithInstalledPublicApp(self, appID, ogID=None):
		"""
		Deprecated: GET? Doc says post but it doesn't work
		 https://host/api/mam/apps/public/{applicationid}/installeddevices?locationgroupid={locationgroupid}&page={page}&pagesize={pagesize}
		Supported: POST
		 https://host/api/mam/apps/public/applicationid/devices
		"""
		url = self.__APIURI_MAM_PUB + '/' + str(appID) + '/installeddevices'
		
		if ogID is not None:
			url += '?locationgroupid=' + ogID

		return self.__loadJSON(self.apiGetRequest(url))

	def installPurchasedApp(self, appID, serialNumber=None, deviceID=None, udid=None):
		""" Send Install Purchased App command to device 
			If Serial, DeviceID or UDID is not provided return None
		"""
		url = self.__APIURI_MAM_VPP + '/' + str(appID) + "/install"
		if serialNumber is not None:
			payload = "SerialNumber=" + serialNumber
		elif deviceID is not None:
			payload = "DeviceId=" + deviceID
		elif udid is not None:
			payload = "Udid=" + udid
		else:
			return None
		
		return self.apiPostRequest(url, payload)

	def getDevicesAssignedToPurchasedApp(self, appID):
		# Supported: https://host/api/mam/purchased/applicationid/devices 
		#url = self.__APIURI_MAM_VPP + "/applicationid/devices"
				#/api/mam/apps/purchased/85/installeddevices?locationgroupid=570
		url = self.__APIURI_MAM_VPP + "/" + str(appID) + "/assigneddevices?" + self.__PAGESIZE
		#payload = "ApplicationID=" + str(appID)
		print(url)
		return self.__loadJSON(self.apiGetRequest(url))

	"""		Profile Management"""
	def findDeviceProfile(self, profileName, profileType=None, ogID=None, platform=None, status=None):
		# /mdm/profiles/search?
		# type=					-	"Optional"	| "Auto" | "Compliance"
		# &profilename=			-	Name
		# &organizationgroupid	-	OG ID Number
		# &platform=			-	"Apple" | "AppleOsX" | "Android"
		# &status=				- 	"Active" | "Inactive"
		# &ownership=			-	Ownership type of the enrolled device
		# &orderby=				-	Order by column mentioned above
		# &sortorder=			- 	"ASC" | "DESC"
		url = self.__APIURI_MDM_PROFILE + "/search?"
		query = ""
		if profileName is not None:
			query = "profilename=" + str(profileName)
			if profileType is not None:
				query += "&type=" + str(profileType)
			if ogID is not None:
				query += "&organizationgroupid" + str(ogID)
			if platform is not None:
				query += "&platform=" + platform
			if status is not None:
				query += "&status=" + status
		else:
			return None
		url += query
		return self.__loadJSON(self.apiGetRequest(url))

	def getProfileDetails(self, profileID):
		# mdm/profiles/{profileid}
		url = self.__APIURI_MDM_PROFILE + "/" + str(profileID)
		return self.__loadJSON(self.apiGetRequest(url))

	"""		Enrollment User Management	"""
	def createBasicUser(self, username, password, firstName, lastName, emailAddress=None, status=True, messageType=None):	#-- work in progress
		"""
			URL: api/system/users/adduser
			"UserName":"String",	-
			"Password":"String",	-
			"FirstName":"String",	-
			"LastName":"String",	-
			"Status":"Boolean",		-
			"Email":"String",		- if None, set to username (check if email)
			"SecurityType":Numeric,	- 1 for Basic, 2 for Directory
			"ContactNumber":"String",
			"MobileNumber":"String",
			"Group":Numeric,
			"LocationGroupId":Numeric,
			"Role":"String",
			"MessageType":"String",	- None by default
			"MessageTemplateId":Numeric
		"""

		url = self.__APIURI_EUSER + '/adduser'
		return None

	"""		Tag Management	"""
	def searchTag(self, name=None, orgID=None, tagType=None):
		#	mdm/tags/search?name={name}&organizationgroupid={organizationgroupid}&tagtype={tagtype}&page={page}&pagesize={pagesize}
		url = self.__APIURI_MDM_TAGS + '/search'
		
		pList = []
		if name is not None:
			pList.append('name=' + name)
		if orgID is None:
			orgID = self.__CUSTOMER_OG
		if tagType is not None:
			pList.append('tagtype=' + tagtype)
		pList.append('organizationgroupid=' + orgID)

		param = self.__formatParameters(pList)
		return self.__loadJSON(self.apiGetRequest(url + param))

	def getTaggedDevices(self, tagID, lastseen=None):
		#	mdm/tags/{tagid}/devices?LastSeen={lastseen}
		url = self.__APIURI_MDM_TAGS + '/' + str(tagID) + '/devices'

		if lastseen is not None:
			url += '?lastseen=' + lastseen

		return self.__loadJSON(self.apiGetRequest(url))
	
	def tagDevice(self, tagID, deviceID=None, bulkDevices=None, verbose=False):
		#mdm/tags/{tagid}/adddevices
		url = self.__APIURI_MDM_TAGS + '/' + str(tagID) + '/adddevices'

		##	""{\"BulkValues\":{\"Value\":[\"5963\"]}}"
		payload = "{\"BulkValues\":{\"Value\":["

		if deviceID is not None:
			payload += "\"" + str(deviceID) + "\""
		elif bulkDevices is not None:
			for device in bulkDevices:
				payload += "\"" + str(device) + "\""
		else:
			return None

		payload +="] }}"
		response = self.apiPostRequest(url, payload, contentType='json', verbose=verbose)

		if verbose:
			return self.__loadJSON(response)
		else:
			return response

	"""		Custom Attribute Management	"""
	def searchCustomAttributes(self, name=None, orgID=None):
		#system/customattributes/search?organizationgroupid={organizationgroupid}&name={name}
		url = self.__APIURI_SYS_CA + '/search'

		pList = []
		if orgID is not None:
			plist.append('organizationgroupid=' + orgID)
		if name is not None:
			pList.append('name=' + quote(name))

		param = self.__formatParameters(pList)
		return self.__loadJSON(self.apiGetRequest(url + param))