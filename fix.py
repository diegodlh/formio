import json
import pdb

filein = 'data/20190507.json'
fileout = 'data/20190507_fixed.json'

with open(filein) as filein:
  json_in = json.load(filein)

json_out = []

def toArray(key, data):
  if key in data:
    value = data[key]
    if not (isinstance(value, list)):
      data[key] = [value]
  return data

for submission in json_in:
  data = submission['data']
  try:
    data = toArray('noDenunciaMotivo', data)
    data = toArray('consultaEspacioPrincipalUbicacion', data)
  except:
    pdb.set_trace()
  submission['data'] = data
  json_out.append(submission)

with open(fileout, 'w') as fileout:
  json.dump(json_out, fileout)