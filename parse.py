import json
import pandas as pd
import numpy as np
import pdb

# with open('data/20190507_0239.json') as filein:
#   json_in = json.load(filein)

# json_out = []
# for submission in json_in:
#   json_out.append(submission['data'])

# df = pd.io.json.json_normalize(json_out)

codigos = pd.DataFrame()
for _, df in pd.read_excel('manual_codigos.xlsx', sheet_name=None).items():
  keys = df.columns[0]
  if keys:
    try:
      df.columns = ['value', 'label']
    except:
      pdb.set_trace()
    for key in keys.split(','):
      df['key'] = key
      codigos = codigos.append(df, ignore_index=True)
# codigos.value = codigos.value.astype(int)

data = pd.read_csv('data/20190508.csv')

# mejorar filtro de encuestas sin enviar
data = data[~data.numencuesta.isin(['95','91','2',None])].reset_index(drop=True).copy()

columns_new = []
for column in data.columns:
  column = column.split('.')
  try:
    int(column[-1])
    column = '.'.join(column[-2:])
  except ValueError:
    column = column[-1]
  columns_new.append(column)
data.columns = columns_new

# ojo! no puedo aplicar a todas las columnas! pierdo al menos nro de encuesta
data = data.apply(lambda x: x.str.replace('"','').str.split(','), axis=1)

data['consultaEspacioCual_3'] = data['consultaEspacioCual']
data['consultaEspacioCual_7'] = data['consultaEspacioCual']
data = data.drop('consultaEspacioCual', axis='columns')
# terminar: quitar valores de la lista que no correspondan



# remuneradaNombre (+100, etc)
# 8.1.1, 8.2.1, 8.3.1, 8.4.1

for key in codigos.key.unique():
  for _, row in data.iterrows():
    # pdb.set_trace()
    cell = row[key]
    if type(cell) is not list:
      cell = [cell]
    for value in cell:
      if not value:
        # vacío
        continue
      try:
        value = float(value)
        if np.isnan(value):
          continue
        # tengo que filtrar por 99 inválido
        if not value in set(codigos[codigos.key == key].value):
          # pdb.set_trace()
          print('numencuesta {}, {}: código {:g} inválido!'.format(
            row['numencuesta'], key, value)
          )
      except:
        print('numencuesta {}, {}: código {} inválido!'.format(
          row['numencuesta'], key, value)
        )