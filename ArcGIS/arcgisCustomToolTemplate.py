# Template for writing a custom tool in ArcMap using python / arcpy. 
# This is used to create a tool (see associated documentation in the repository)
# within a Python Toolbox in ArcGIS

# Examples are also presented in the repository

import arcpy

class Toolbox(object):
	def __init__(self):
		# Define the toolbox 
		self.label = "SSSI units and customer name search"
		self.alias = "Uplands"

		# List of tools associated with this toolbox (class name below)
		self.tools = [UplandsSearch]

class UplandsSearch(object):
	def __init__(self):
		#Define the tool (tool name is the name of the class)
		self.label = "SSSI units and customer name search"
		self.description = "Search SSSI units for owner names"
		self.canRunInBackground = False

	def getParameterInfo(self):
		# Define parameter definitions. These are the arguments you see 
		# when you open a tool in ArcMap

		params = None
		return params

	def isLicensed(self):

		# Set whether tool is licensed to execute
		return True

	def updateParameters(self, parameters):
		# Modify the values and properties of parameters based on initial user input.
		# Eg setting up a drop down that is dependent on the selection in a previous drop down.
		# This method is called whenever a parameter has been changed
	
		return

	def updateMessages(self, parameters):
		# Modify the message created by internal validation for each tool parameter.
		# This method is called after internal validation
		return

	def execute(self, parameters, messages):
		# The source code of the tool ie the code that runs the procedure.

		return






