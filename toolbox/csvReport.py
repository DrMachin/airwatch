"""
	Convert JSON to CSV for reporting.
	Steps (I, think)
	1 - First Pass: Parse through JSON to get generate list of all keys
		-- Going to need to learn how to make recursive loops to dig deep.
	2 - Create csv header using keys
	3 - Second Pass: Parse through JSON to match value to key

	This should be fun...
"""

class csvReport:

	def __init__(self):
		self.data = []

	def __parseKeys(self, jList):
		keyList = []
		if isinstance(jList, list):
			for item in jList:
				keyList = self.__parseKeys(item)
		else:
			for key, value in jList.items():
				if not isinstance(value, list):
					if str(key) not in keyList:
						keyList.append(key)
				else:
					for item in value:
						childList = self.__parseKeys(item)
						for citem in childList:
							if str(citem) not in keyList:
								keyList.append(citem)
		return keyList

	def __parseValues(self, jList, keyList):
		valueList = dict()
		if isinstance(jList, list):
			for item in jList:
				valueList = self.__parseValues(item, keyList)
		else:
			for key, value in jList.items():
				if not isinstance(value, list):
					if key in keyList:
						value[str(key)] = value
		return valueList


	def jsonToCsv(self, aJSON):
		keyList = []
		if aJSON is not None:
			keyList = self.__parseKeys(aJSON)
			parseValues = self.__parseValues(aJSON, keyList)
			print(parseValues)