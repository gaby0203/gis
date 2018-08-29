# An example of a custom ArcGIS tool

import arcpy

class Toolbox(object):
	def __init__(self):
		# Define the toolbox
		self.label = "SSSI units and customer name search"
		self.alias = "Uplands"

		# List of tools associated with this toolbox
		self.tools = [UplandsSearch]

class UplandsSearch(object):
	def __init__(self):
		# Define the tool (tool name is the name of the class)
		self.label = "SSSI units and customer name search"
		self.description = "Search SSSI units for owner names"
		self.canRunInBackground = False

	def getParameterInfo(self):
		# Define parameter definitions.

		# Input Features parameter
		inFeature = arcpy.Parameter(
			displayName = "Select a feature layer",
			name = "inFeature",
			datatype = "Feature Layer",
			parameterType = "Required",
			direction = "Input")

		# SSSI units field
		sssiField = arcpy.Parameter(
			displayName = "Select the SSSI unit name field",
			name = "sssiField",
			datatype = "Field",
			parameterType = "Required",
			direction = "Input")

		# Auto populate parameter with SSSI_NAME field
		sssiField.parameterDependencies = [inFeature.name]
		sssiField.value = "SSSI_NAME" 

		# SSSI units parameter
		sssiName = arcpy.Parameter(
			displayName = "Select SSSI units",
			name = "sssiName",
			datatype = "GPString",
			parameterType = "Required",
			direction = "Input",
			multiValue = True)

		# Create as a multi-select list and intiate empty list
		sssiName.filter.type = "ValueList"
		sssiName.filter.list = []

		# Text search field
		textSearchField = arcpy.Parameter(
			displayName = "Select the text search field",
			name = "textSearchField",
			datatype = "Field",
			parameterType = "Required",
			direction = "Input")

		# Create as a drop down list dependent on fields in the feature layer
		textSearchField.parameterDependencies = [inFeature.name]
		# Auto populate with Cust_Name field 
		textSearchField.value = "Cust_Name"

		# Text search value. Note this is an optional field.
		textSearch = arcpy.Parameter(
			displayName = "Text to search for",
			name = "textSearch",
			datatype = "GPString",
			parameterType = "Optional",
			direction = "Input")

		# Tickbox for whether the search should be case sensitive
		caseSensitive = arcpy.Parameter(
			displayName = "Make search case sensitive",
			name = "caseSensitive",
			datatype = "GPBoolean",
			parameterType = "Optional",
			direction = "input")

		# Create list of all parameters and return
		parameters = [inFeature, sssiField, sssiName, textSearchField, textSearch, caseSensitive]

		return parameters

	def updateParameters(self, parameters):
		# This sets drop down list for sssiName parameter based on the SSSI's found in the feature layer.
		# This is run everytime a parameter is updated so quite expensive.

		# Check SSSI Units field has entry in the tool
		if parameters[1].value:
			# Search cursor searches selected reocrds by defualt. Use WHERE clause to change this
			# Select entries from Feature layer in the column name specified in SSSI Units field
			with arcpy.da.SearchCursor(parameters[0].valueAsText, parameters[1].valueAsText) as rows:
				# Extract just the SSSI name from the search to populate the Select SSSI Units parameter.
				parameters[2].filter.list = sorted(list(set([row[0] for row in rows])))
				# Calculate the number of SSSIs
				parameterLength = len(parameters[2].filter.list)

		# If no entry for SSSI Units in tool, list of SSSI's is empty.
		else:
			parameters[2].filter.list = []

		return parameterLength

	def updateMessages(self, parameters):
		# Update messages. Left blank for this tool
		return

	def execute(self, parameters, messages):
		# The source code of the tool

		# Define variables for input parameters
		inFeatures = parameters[0].valueAsText
		sssiFieldName = parameters[1].valueAsText
		sssiNames = parameters[2].valueAsText
		textFieldName = parameters[3].valueAsText
		# Make search non-case sensitive
		# Escape apostrophe in text search if it exists and convert to lowercase
		case = parameters[5].valueAsText

		#define empty where clause
		clause = []

		#Crete SQL string to be used in search by attributes tool. Sample here:
		# ("SSSI_NAME" = 'Appleby Fells' AND ("Cust_Name" LIKE '%a%' OR "Cust_Name" LIKE 
		# 'a%' OR "Cust_Name" LIKE 'a%')) OR("SSSI_NAME" = 'Allendale Moors' AND 
		# ("Cust_Name" LIKE '%a%' OR "Cust_Name" LIKE 'a%' OR "Cust_Name" LIKE 'a%'))


		# Multivalue stored text (for select SSSI Units field) split by semi-colon. 
		# Need to split this into a list before iterating through
		for units in sssiNames.split(';'):

			# Check unit for apostrophe or single word and clean as appropiate for where clause
			
			# Single word
			if not units.startswith("'"):
				unitsCleaned = "'{unit}'".format(unit = units)
			# Apostrophe
			elif "'" in units[1:len(units)-1]:
				unitsCleaned = "'" + units[1:len(units)-1].replace("'", "''") + "'"
			else:
				unitsCleaned = units

			# Add field delimeters to help with inserting into SQL where clause
			sssiUnitField = arcpy.AddFieldDelimiters(inFeatures, sssiFieldName)
			customerNameField = arcpy.AddFieldDelimiters(inFeatures, textFieldName)

			# Create clause based on whether case sensitivity is selected
			if case == 'true':
				if text == None:
					clause.append("({sssiField} = {sssiUnit})".format(sssiField = sssiUnitField, sssiUnit = unitsCleaned))
				else:
					clause.append("({sssiField} = {sssiUnit} AND ({custField} LIKE '%{textField}' OR {custField} LIKE '%{textField}%' OR {custField} LIKE '{textField}%'))"
								.format(sssiField = sssiUnitField, sssiUnit = unitsCleaned, custField = customerNameField, textField = text))
			else:
				if text == None:
					clause.append("({sssiField} = {sssiUnit})".format(sssiField = sssiUnitField, sssiUnit = unitsCleaned))
				else:
					clause.append("({sssiField} = {sssiUnit} AND (LOWER({custField}) LIKE '%{textField}' OR LOWER({custField}) LIKE '%{textField}%' OR LOWER({custField}) LIKE '{textField}%'))"
								.format(sssiField = sssiUnitField, sssiUnit = unitsCleaned, custField = customerNameField, textField = text.lower()))



		# Create final SQL clause by concatenating all entries in the list
		whereClause = ' OR '.join(clause)


		# Search by attributes
		try:
			arcpy.SelectLayerByAttribute_management(inFeatures, "NEW_SELECTION", whereClause)
			# print message to tool progress dialog
			messages.addMessage('NUMBER OF RECORDS RETURNED: ' + arcpy.GetCount_management(inFeatures).getOutput(0))
		except arcpy.ExecuteError:
			arcpy.AddError(arcpy.GetMessages(2))
			# reset attribute table automatically
			arcpy.SelectLayerByAttribute_management(inFeatures, "CLEAR_SELECTION")


		# If no results are returned, clear the attribute table so the SSSI name is always populated in the tool
		if int(arcpy.GetCount_management(inFeatures).getOutput(0)) == 0:
			arcpy.SelectLayerByAttribute_management(inFeatures, "CLEAR_SELECTION")

		return






