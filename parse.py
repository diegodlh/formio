import json
import pandas as pd

# with open('data/20190507_2048.json') as filein:
#   json_in = json.load(filein)

# json_out = []
# for submission in json_in:
#   json_out.append(submission['data'])

# df = pd.io.json.json_normalize(json_out)

df = pd.read_csv('data/20190507_2048.csv')
df.columns = df.columns.str.replace('.', '_')
df = df.apply(lambda x: x.str.replace('"','').str.split(','),axis=1)
