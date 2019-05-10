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

data = pd.read_csv(
  'data/20190508.csv',
  keep_default_na=False,
  dtype='str'
)

# mejorar filtro de encuestas sin enviar
data = data[~data.numencuesta.isin(['95','91','2',''])].reset_index(drop=True).copy()

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


def splitCell(series):
  if series.dtype == 'object':
    return series.str.replace('"', '').str.split(',')
  else:
    return series

data = data.apply(splitCell)


def fixConsultaEspacioCual(row):
  consultaEspacio = np.array(row.consultaEspacio)
  consultaEspacioCual = np.array(row.consultaEspacioCual)
  row.consultaEspacioCual_3 = list(np.where(consultaEspacio=='3',consultaEspacioCual,''))
  row.consultaEspacioCual_7 = list(np.where(consultaEspacio=='7',consultaEspacioCual,''))
  return row

data['consultaEspacioCual_3'] = data['consultaEspacioCual']
data['consultaEspacioCual_7'] = data['consultaEspacioCual']

data = data.apply(fixConsultaEspacioCual, axis=1)
data = data.drop('consultaEspacioCual', axis='columns')

def fixMultiple(row):
  remuneradaNombre = row.remuneradaNombre
  remuneradaNombre_new = []
  for i, value in enumerate(remuneradaNombre):
    if value != '99':
      try:
        value_new = str(int(value) + (i+1)*100)
      except:
        value_new = value
    else:
      value_new = value
    remuneradaNombre_new.append(value_new)
  row.remuneradaNombre = remuneradaNombre_new

  def add(list, increment):
    list_new = []
    for value in list:
      if value != '99':
        try:
          value_new = str(int(value) + int(increment))
        except:
          value_new = value
      else:
        value_new = value
      list_new.append(value_new)
    return list_new

  row.conoceOrgaCual = add(row.conoceOrgaCual, 100)
  row.participaOrgaCual = add(row.participaOrgaCual, 100)
  row.conoceProgramaCual = add(row.conoceProgramaCual, 100)
  row.participaProgramaCual = add(row.participaProgramaCual, 100)
  return row

data = data.apply(fixMultiple, axis=1)
pdb.set_trace()

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
          print('numencuesta {} ({}), {}: código {:g} inválido!'.format(
            row['numencuesta'][0], row['cargadorx'][0], key, value)
          )
      except:
        print('numencuesta {}, {}: código {} inválido!'.format(
          row['numencuesta'][0], key, value)
        )