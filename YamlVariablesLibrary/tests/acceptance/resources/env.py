import os

def get_variables():
    
    variables = {}
    
    variables["ROOT_DIR"] = os.path.abspath(os.path.join(__file__, '..','..')).replace("\\", "/")
    variables["RESOURCES_DIR"] = "/".join((variables["ROOT_DIR"], "resources"))
    variables["ENVIRONMENT_RESOURCES_DIR"] = "/".join((variables["ROOT_DIR"],  "resources", "environments"))
  
    variables['singleEnv'] = "TestEnv02Type01"
    variables['multiEnv'] = "TestEnv01Type01:TestEnv01Type02"
    
    variables['suiteGlobalVariableTestString'] = "This string is defined in the env.py file."
    variables['suiteLevelString3'] = "This should be changed by the suite level"
    
    return variables
