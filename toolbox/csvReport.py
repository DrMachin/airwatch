
class csvReport:

	__FILENAME = ''

	def __init__(self, fileName):
		self.data = []
		self.__FILENAME = fileName

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

	def __parseValues(self, jList):
		csvOutput = ''
		child = False
		if isinstance(jList, list):
			for item in jList:
				csvOutput += self.__parseValues(item)
		else:
			for key, value in jList.items():
				if not isinstance(value, list):
					csvOutput += '\"' + str(value) + '\",'
				else:
					child = True
					childCSV = self.__parseValues(value)
					copyOut = csvOutput
					csvOutput = ''
					for line in childCSV.splitlines():
						csvOutput += copyOut + line + '\n'
					csvOutput = csvOutput.rstrip()
		if not child:
			csvOutput = csvOutput[:-1]
		csvOutput += '\n'
		return csvOutput


	def jsonToCsv(self, aJSON):
		keyList = []
		if aJSON is not None:
			keyList = self.__parseKeys(aJSON)
			csvOutput = ''
			for header in keyList:
				csvOutput += '\"' + header + '\",'
			csvOutput = csvOutput[:-1] + '\n'
			csvOutput += self.__parseValues(aJSON)
			fh = open(self.__FILENAME, "w")
			fh.write(csvOutput)
			fh.close()
