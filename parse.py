# comparar archivo csv vs json
import json
import pandas as pd
import pdb
import numpy as np

# enumera las datagrids de campo único, para desanidarlas siempre
campo_unico = []

def str2int(value):
  if isinstance(value, str):
    try:
      value = int(value)
    except ValueError:
      pass
  return value

with open('encuesta.json') as filein:
  encuesta = json.load(filein)

def extraerComponents(components, lista):
  for component in components:
    if component['input']:
      lista.append(component)
    else:
      if 'components' in component:
        lista = extraerComponents(component.pop('components'), lista)
      elif 'columns' in component:
        for column in component['columns']:
          lista = extraerComponents(column.pop('components'), lista)
  return lista

lista_components = []
lista_components = extraerComponents(encuesta['components'], lista_components)

# tipos de components disponibles
set([component['type'] for component in lista_components])

pregunta_types = ['button', 'checkbox', 'number', 'radio', 'select', 'survey', 'textfield', 'datagrid']
preguntas = [component for component in lista_components if component['type'] in pregunta_types]

preguntas_new = []
for pregunta in preguntas:
  if pregunta['key'] == 'consultaEspacios':
    components_new = []
    for component in pregunta['components']:
      if component['key'] == 'consultaEspacioCual':
        for suffix in ['_3', '_7']:
          component_new = component.copy()
          component_new['key'] += suffix
          components_new.append(component_new)
      else:
        components_new.append(component)
    pregunta['components'] = components_new
  preguntas_new.append(pregunta)
preguntas = preguntas_new

columns = []
required = {}
for pregunta in preguntas:
  if pregunta['type'] == 'survey':
    is_required = pregunta['validate']['required']
    for question in pregunta['questions']:
      columna = '{}.{}'.format(pregunta['key'], question['value'])
      required[columna] = is_required
      columns.append(columna)
  elif pregunta['type'] == 'datagrid':
    for component in pregunta['components']:
      if component['key'] == 'consultaEspacioOrden':
        is_required = True
      elif 'validate' in component:
        is_required = component['validate']['required']
      else:
        is_required = False
      if len(pregunta['components']) > 1:
        columna = '{}.{}'.format(pregunta['key'], component['key'])
      else:
        columna = component['key']
        campo_unico.append(pregunta['key'])
      required[columna] = is_required
      columns.append(columna)
  else:
    if 'validate' in pregunta:
      is_required = pregunta['validate']['required']
    else:
      is_required = False
    columna = pregunta['key']
    required[columna] = is_required
    columns.append(columna)

###

with open('data.json') as filein:
  json_in = json.load(filein)

data_json = []
for submission in json_in:
  datum = submission['data']
  if ('enviar' in datum) and datum['enviar']:
    data_json.append(datum)

# identificar elementos padre (datagrids)
parents = {}
for datum in data_json:
  for datum_key, datum_value in datum.items():
    if type(datum_value) is list:
      for element in datum_value:
        if type(element) is dict:
          # is datagrid
          if datum_key not in parents:
            parents[datum_key] = set()
          for element_key in element.keys():
            parents[datum_key].add(element_key)

# convertir datagrids de una lista por fila
# a una lista por columna
json_new = []
for datum in data_json:
  datum_new = {}
  for datum_key, datum_value in datum.items():
    if datum_key in parents:
      # is datagrid
      elements = datum_value  # lista de filas, un dict de columnas por fila
      elements_new = {}  # dict de columnas, una lista de filas por columna
      for children_key in parents[datum_key]:
        children_value = []
        for element in elements:
          if children_key in element:
            children_value.append(element[children_key])
          else:
            children_value.append(None)
          elements_new[children_key] = children_value
        if datum_key in campo_unico:
          datum_new[children_key] = children_value  # desanidar: ascender hijos
          continue
      datum_new[datum_key] = elements_new  # no desanidar: conservar padre
    else:
      datum_new[datum_key] = datum_value
  json_new.append(datum_new)
data_json = json_new

# flatten json
json_new = []
for datum in data_json:
  datum_new = {}
  for datum_key, datum_value in datum.items():
    if isinstance(datum_value, dict):
      for dict_key, dict_value in datum_value.items():
        datum_new['{}.{}'.format(datum_key, dict_key)] = dict_value
    else:
      value_new = datum_value
      datum_new[datum_key] = value_new
  json_new.append(datum_new)
data_json = json_new

# if required and '' or None: 'No corresponde'; recorrer listas
json_new = []
values = set()
for datum in data_json:
  datum_new = {}
  for key, is_required in required.items():
    # required tiene consultaEspacioCual dividido pero data_json aún no
    # prefiero dividirlo cuando data_json sea dataframe
    # pero conversión a 'No corresponde' es mejor hacerlo acá
    key = key.split('_')[0]
    if key in datum:
      datum_value = datum[key]
      if isinstance(datum_value, list):
        value_new = []
        for list_value in datum_value:
          if (list_value in ['', None]) and is_required:
            list_value = 'No corresponde'
          list_value = str2int(list_value)
          value_new.append(list_value)
          values.add(list_value)
      else:
        if (datum_value in ['', None]) and is_required:
          datum_value = 'No corresponde'
        value_new = str2int(datum_value)
        values.add(value_new)
      datum_new[key] = value_new
    else:
      datum_new[key] = 'No corresponde'
  json_new.append(datum_new)
data_json = json_new

data_json = pd.read_json(json.dumps(data_json))
# data_json = pd.io.json.json_normalize(data_json)  # así como está sólo desagrega subitems de survey


col_a = 'consultaEspacios.consultaEspacio'
col_b = 'consultaEspacios.consultaEspacioCual'

def fixConsultaEspacioCual(row):
  def where(list_a,list_b,target,if_false):
    list_new = []
    for i, value in enumerate(list_a):
      if value == target:
        list_new.append(list_b[i])
      else:
        list_new.append(if_false)
    return list_new
  
  col_a = 'consultaEspacios.consultaEspacio'
  col_b = 'consultaEspacios.consultaEspacioCual'

  if isinstance(row[col_a], list):
    for i in [3, 7]:
      row['{}_{}'.format(col_b, i)] = where(row[col_a], row[col_b], i, 'No corresponde')
  return row

data_json.insert(data_json.columns.get_loc(col_b), col_b + '_3', data_json[col_b])
data_json.insert(data_json.columns.get_loc(col_b), col_b + '_7', data_json[col_b])
data_json = data_json.apply(fixConsultaEspacioCual, axis=1)
data_json = data_json.drop(col_b, axis='columns')


def fixMultiple(row):
  # remuneradaNombre = row['remuneradas.remuneradaNombre']
  # if isinstance(remuneradaNombre, list):
  #   remuneradaNombre_new = []
  #   for i, value in enumerate(remuneradaNombre):
  #     if isinstance(value, int) and value < 99:
  #       value += (i+1)*100
  #     remuneradaNombre_new.append(value)
  #   row['remuneradas.remuneradaNombre'] = remuneradaNombre_new

  def add(lista, increment):
    if isinstance(lista, list):
      lista_new = []
      for value in lista:
        if isinstance(value, int) and value < 99:
          value += increment
        lista_new.append(value)
    else:
      lista_new = lista
    return lista_new

  additions = [
    ('conoceOrgaCual', 100),
    ('participaOrgaCual', 200),
    ('conoceProgramaCual', 100),
    ('participaProgramaCual', 200)
  ]

  for columna, increment in additions:
    row[columna] = add(row[columna], increment)
  return row

data_json = data_json.apply(fixMultiple, axis=1)
data_json = data_json.reindex(labels=columns, axis='columns')

###

data_csv = pd.read_csv('data/20190507_0239.csv')
columns_new = []
for column in data_csv.columns:
  column = column.split('.')
  try:
    int(column[-1])
    column = '.'.join(column[-2:])
  except ValueError:
    if len(column) > 1:
      if not column[-2] in campo_unico:
        column = '.'.join(column[-2:])
      else:
        column = column[-1]
    else:     
      column = column[-1]
  columns_new.append(column)
data_csv.columns = columns_new

###

print('column in encuesta not in csv')
print([column for column in columns if column not in data_csv.columns])
# sólo draft y enviar están en encuesta pero no en csv

print('columns in json not in csv:')
print([column for column in data_json.columns if column not in data_csv.columns])

print('columns in json[enviar] not in csv:')
data_json_enviado = data_json[~data_json.enviar.isna()].dropna(axis='columns', how='all')
print([column for column in data_json_enviado.columns if column not in data_csv.columns])
# sólo sobra columna violentxs.6 si descarto encuestas sin enviar

print('columns in csv not in json:')
print([column for column in data_csv.columns if column not in data_json.columns])

###

fusionarNS = ['residenciaPartido', 'residenciaCiudad', 'nacimientoPais', 'nacimientoProvincia', 'nacimientoPartido', 'nacimientoCiudad']
for key in fusionarNS:
  data_json.loc[data_json[key+'NS'] == True, key] = 99
  data_json = data_json.drop(key+'NS', axis='columns')

data_json.to_csv('data.csv', index=False)

###
dups = list(data_json.loc[data_json.numencuesta.duplicated(), 'numencuesta'])
for dup in dups:
  df = data_json.loc[data_json.numencuesta == dup].reset_index(drop=True)
  # pdb.set_trace()
  for i in range(len(df)-1):
    if df.loc[0].equals(df.loc[i+1]):
      print('numencuesta {}: duplicada igual!'.format(dup))
      break
    else:
      print('numencuesta {}: duplicada diferente!'.format(dup))

###

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

anidadas = []
columns_new = []
for column in data_json.columns:
  column = column.split('.')
  try:
    int(column[-1])
    column = '.'.join(column[-2:])
  except ValueError:
    column = column[-1]
    anidadas.append(column)
  columns_new.append(column)
data_json.columns = columns_new

for key in codigos.key.unique():
  for _, row in data_json.iterrows():
    cell = row[key]
    if type(cell) is not list:
      cell = [cell]
    for value in cell:
      if value == 'No corresponde':
        continue
      if not value in set(codigos[codigos.key == key].value):
        print('numencuesta {} ({}), {}: código {} inválido!'.format(
          row['numencuesta'], row['cargadorx'], key, value)
        )
    if (99 in cell) and (len(cell) > 1) and (not key in anidadas):
      print('numencuesta {} ({}), {}: indica 99 y otras opciones!'.format(
        row['numencuesta'], row['cargadorx'], key)
      )

# incorporar checkpoints a pregunta principal
# incluir detección de duplicados