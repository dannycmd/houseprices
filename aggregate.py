# code to aggregate SQL data
from pathlib import Path
import os
import pandas as pd
import json
import itertools

### Load data
appDir = Path(os.path.abspath(''))
summary = pd.read_csv(appDir / 'app/summary.csv', encoding='utf-8', delimiter=',')
summary = summary[(~summary['Outcode'].isnull())]
summary = summary.rename(columns={"range_": "range"})

### Get polygon coordinates (GeoJSON) of each PostcodeArea
geojsonDir = appDir / 'districts'
# combine all PostcodeArea datasets, one for each PostcodeArea
geojsonDict = {}
for file in geojsonDir.glob('*.geojson'):
    with open(file, 'r') as f:
        geojsonDict[str(file).split('\\')[-1][:-8]] = json.load(f)
# add id string to link to summary data
for key in geojsonDict.keys():
    geojsonDict[key]['features'][0]['id'] = key
# changing format of geojsonDict to meet required format for Choropleth function
geojsonList = []
uniqueOutcodes = summary['Outcode'].unique().tolist()
for outcode in geojsonDict.keys():
    features = geojsonDict[outcode]['features']
    if outcode in uniqueOutcodes:
        geojsonList.append(features[0])
geojsonDict = {}
geojsonDict['type'] = 'FeatureCollection'
geojsonDict['features'] = geojsonList

### make sure summary data has a row for every Outcode and YearBin - set aggregate values to null if missing
uniqueYearBins = summary['YearBin'].unique().tolist()
crossJoin = list(itertools.product(uniqueOutcodes, uniqueYearBins))
crossJoin = pd.DataFrame(crossJoin, columns=["Outcode", "YearBin"])
summary = pd.merge(crossJoin, summary, how="left", on=["Outcode", "YearBin"])

# export as geojson dictionary as json file
with open(appDir / 'app/OutcodeCoordinates.json', 'w') as fp:
    json.dump(geojsonDict, fp)

# export summary dataframe as csv
summary.to_csv(appDir / 'app/summary.csv', index=False)