'''
Copyright 03/01/2014 Jules Barnes

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

import os
import re
import yaml
from robot.libraries.BuiltIn import BuiltIn


class keywords (object):

    def __init__(self, baseDir, envDir=None):
        # Get the base working directory
        self.baseDir = baseDir.replace("\\", "/")

        # Get the directory that stores the test environment resources
        if envDir != None:
            self.envDir = envDir.replace("\\", "/")

        # Get an instances of the RF BuildIn Functions
        self.robotBuiltIn = BuiltIn()

    def get_data(self, environments=None):
        # Gets the full location on this file
        self.me = os.path.abspath(__file__)[:-1].replace("\\", "/")
        self.robotBuiltIn.log("File Path: %s" % self.me)

        # Gets the current test suite source
        suiteSource = self.robotBuiltIn.get_variable_value('${SUITE SOURCE}').replace("\\", "/")
        charPos = len(suiteSource) - suiteSource.rfind("/")
        # Removes the last \\ from the suite source
        suiteSourceDir = suiteSource[:-charPos]
        self.robotBuiltIn.log("Suite Directory: %s" % suiteSourceDir)

        # Gets the current test name
        testCaseName = self.robotBuiltIn.get_variable_value('${TEST_NAME}')
        suiteKey = self._get_suite_key()

        # If testCaseName is none, then set suite and environment variables
        if testCaseName == None:
            self.robotBuiltIn.log("Test Case Name is None")

            # Gets the environment level variables
            if environments != None:
                self.robotBuiltIn.log("Environment variable has been passed")

                # Get the environment value if a RF variable has been passed
                patternRFVar = re.compile(r'''\${(.*?)}''', re.UNICODE |
                                                            re.VERBOSE |
                                                            re.S)
                if patternRFVar.search(environments):
                    self.robotBuiltIn.log("Environment variable is a RF variable")
                    environments = self.robotBuiltIn.get_variable_value(environments)

                # Split the env string to get each env that was passed
                envList = environments.split(":")

                # Read the contents of each env yaml and create the variables
                for envFile in envList:
                    self.robotBuiltIn.log("Importing Environment Variables for: %s" % envFile)
                    varFile = os.path.join(self.baseDir, self.envDir, envFile).replace("\\", "/")
                    self.robotBuiltIn.import_variables(self.me, varFile, "env")

            # Gets the suite test data variables and imports variables
            varFile = os.path.join(suiteSourceDir, suiteKey).replace("\\", "/")
            if suiteKey != None:
                self.robotBuiltIn.log("Trying to import suite variables: %s" % varFile)
                if os.path.isfile(varFile + ".yaml"):
                    self.robotBuiltIn.log("File found, importing.")
                    self.robotBuiltIn.import_variables(self.me, varFile)
                else:
                    self.robotBuiltIn.log("File not found. Not importing.")

        # if testCaseName is not none, then set test case variables
        if testCaseName != None:

            # Gets the test case data variables and imports variables
            testKey = self._get_test_key()
            #varFile = (suiteSourceDir + "/" + suiteKey + "-" + testKey)
            varFile = (suiteSourceDir + "/" + testKey)
            print varFile
            if testKey != None:
                if os.path.isfile(varFile + ".yaml"):
                    self.robotBuiltIn.import_variables(self.me, varFile)

    def get_data_service(self, keyword):
        keywordArray = keyword.split("|")
        print keywordArray
        keywordArrayLen = len(keywordArray)
        #print keywordArrayLen
        if keywordArrayLen == 1:
            runKeyword = keywordArray[0]
        else:
            runKeyword = keywordArray.pop(0)

        result = self.robotBuiltIn.run_keyword_and_ignore_error('Keyword Should Exist', runKeyword)
        if result[0] == 'PASS':
            if keywordArrayLen == 1:
                # Gets the return value from the keyword
                testData = self.robotBuiltIn.run_keyword_and_ignore_error(runKeyword)
            else:
                # Gets the return value from the keyword
                testData = self.robotBuiltIn.run_keyword_and_ignore_error(runKeyword, *keywordArray)

        # Run if the keyword runs to PASS and has returned values
        if testData[0] == 'PASS' and testData[1] != None:
            for key, value in testData[1].items():
                variableName = ("${%s}" % key)
                # If the variable is not set the set the variable
                if self.robotBuiltIn.get_variable_value(variableName) == None:
                    self.robotBuiltIn.set_suite_variable(variableName, value.strip())

    def _contains(self, string, char):
        listVar = []
        for i in range(0, len(string)):
            if string[i] == char:
                listVar = listVar + [i]
        return listVar

    def _get_suite_key(self):
        suiteName = self.robotBuiltIn.get_variable_value('${SUITE_NAME}')
        tmp1 = self._contains(suiteName, '-')
        try:
            tmp2 = suiteName[:tmp1[0]]
            tmp3 = tmp2.split(".")
            key = tmp3[len(tmp3) - 1]
            self.robotBuiltIn.log("Suite Key: %s" % key.strip())
            return key.strip()
        except:
            raise Exception("Could not find symbol '-' for expected test suite data setup.")
            return None

    def _get_test_key(self):
        testName = self.robotBuiltIn.get_variable_value('${TEST_NAME}')
        tmp1 = self._contains(testName, ':')
        try:
            key = testName[:tmp1[0]]
            self.robotBuiltIn.log("Test Key: %s" % key.strip())
            return key.strip()
        except:
            raise Exception("Could not find symbol ':' for expected test case data setup.")

            return None


def _open_yaml_file(fileName):
    try:
        fileName += ".yaml"
        f = open(fileName)
    except IOError:
        raise Exception(("Unable to open %s") % (fileName))
    # use safe_load instead load
    fileContents = yaml.safe_load(f)
    f.close()
    return fileContents


def get_variables(testDataFile, testDataFileType="local"):
    robotBuiltIn = BuiltIn()
    #oraConnection = OracleLibrary.keywords()

    robotBuiltIn.log("Importing Data File: %s" % testDataFile)

    if testDataFileType == "env":
        envData = _open_yaml_file(testDataFile)
        variables = {}

        # Following Code adds the servers from each group to the Global Variables DICT
        if "applicationGroups" in envData:
            for applicationGroup in envData['applicationGroups'].keys():
                variables["LIST__" + applicationGroup] = envData['applicationGroups'][applicationGroup]['servers'].keys()
                for value, server in enumerate(envData['applicationGroups'][applicationGroup]['servers'].keys()):
                    variables[applicationGroup + str(value)] = server

        # The following Code will parse for environment variables and it them to the Global Variables DICT
        if "environment" in envData:
            for envVarKey, envVarValue in envData['environment'].items():
                if isinstance(envVarValue, basestring) or isinstance(envVarValue, dict):
                    variables[envVarKey] = envVarValue
                if isinstance(envVarValue, list):
                    variables["LIST__" + envVarKey] = envVarValue

    else:
        variables = _open_yaml_file(testDataFile)
        patternSQL = re.compile(r'''^SELECT(.+?)WHERE''', re.UNICODE |
                                                          re.VERBOSE)

        patternRFVar = re.compile(r'''\${(.*?)}''', re.UNICODE |
                                                    re.VERBOSE |
                                                    re.S)

        patternRFKeyword = re.compile(r'''\Get.Data''', re.UNICODE |
                                                        re.VERBOSE)

        for key, item in variables.items():

            """
            THIS CODE IS USED FOR SQL EXECUTION.
            DUE TO CROSS PLATFORM ISSUES THIS HAS BEEN DISABLED.

            if isinstance(item, list):
                dbName = item[0]
                dbQuery = item[1]

                if patternSQL.match(dbQuery): # If an SQL pattern is found, then run it to get the data
                    if patternRFVar.search(dbQuery):
                        for match in patternRFVar.finditer(dbQuery):
                            rfVarValue = robotBuiltIn.get_variable_value(match.group(0))
                            dbQuery = dbQuery.replace(match.group(0), rfVarValue)

                    result = oraConnection.ora_execute_sql(dbQuery, dbName)

                    if isinstance(result, basestring):
                        variables[key] = result

                    if isinstance(result, list):
                        del variables[key] # Delete the key from the dict
                        listKey = "LIST__" + key # Create a new key with LIST__ at the front

                        # The returned result set from the oracle query is not in the correct format
                        # The below code corrects the format.
                        resultList = []
                        for resultLine in result:
                            for resultLineItem in resultLine:
                                resultList.append(resultLineItem)

                        variables[listKey] = resultList # Updates the dict with the results and new key value
            """
            if isinstance(item, basestring):
                if patternRFVar.search(item):
                    rfVar = patternRFVar.search(item).group()
                    rfVarValue = robotBuiltIn.get_variable_value(rfVar)
                    variables[key] = item.replace(rfVar, rfVarValue)
                    item = variables[key]

                if patternRFKeyword.match(item):
                    itemList = item.split("|")
                    keywordName = itemList[0]
                    itemList.pop(0)
                    itemListLen = len(itemList)

                    if itemListLen == 0:
                        results = robotBuiltIn.run_keyword(keywordName)
                    else:
                        results = robotBuiltIn.run_keyword(keywordName, *itemList)

                    if isinstance(results, basestring):
                        variables[key] = results

                    if isinstance(results, list):
                        del variables[key]
                        listKey = "LIST__" + key
                        variables[listKey] = results

    return variables
