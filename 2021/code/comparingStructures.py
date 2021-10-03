# Developed by: Eliana Corredor Caro and Carlos Manrique
# This file compares all the json and csv files exported from the APIs and generates a file to check the connections between variables.

#%%
import os
import pandas as pd
import json

#------------------------------------
#%%
path = os.getcwd()
#we shall store all the file names in this list
filelist = []

for root, dirs, files in os.walk(path):
	for file in files:
		#append the file name to the list
		filelist.append(os.path.join(root,file))

#print all the file names
for name in filelist:
	print(name)
#------------------------------------


#------------------------------------
# %%
jsonFiles = [match for match in filelist if "json" in match]
print(jsonFiles)

csvFiles = [match for match in filelist if "csv" in match]
print(csvFiles)
#------------------------------------

#------------------------------------
# %%
step0_df = pd.DataFrame()

for file in jsonFiles:
	#df = pd.read_json(file)

	with open(file) as project_file:
		data = json.load(project_file)
	df = pd.json_normalize(data)

	tmpDf = pd.DataFrame({'api_name': file), 'variables': df.columns})
	step0_df = step0_df.append(tmpDf, ignore_index=True)
#------------------------------------


#------------------------------------
# %%
for file in csvFiles:
	df = pd.read_csv(file, low_memory=False)
	tmpDf = pd.DataFrame({'api_name': file, 'variables': df.columns})
	step0_df = step0_df.append(tmpDf, ignore_index=True)
#------------------------------------

# %%
step0_df['variables'].value_counts().loc[lambda x : x>1]

# %%
resultsVariables = pd.crosstab(step0_df['variables'], step0_df['api_name'])
resultsVariables['total'] = resultsVariables.sum(axis=1)
resultsVariables = resultsVariables.reset_index()

#%%
a = resultsVariables.columns.tolist()
resA = [sub.replace('\\', '_') for sub in a]
resA = [sub.replace('c:_Users_suilu_Documents_Research_nasa_ontologies_sources_api_', '') for sub in resA]
resultsVariables.columns = resA


# %%
# Exporting info
resultsVariables.to_csv('commonVariables.csv', index=False)
# %%
