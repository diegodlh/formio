# comparar archivo csv vs json
import json
import pandas as pd
import pdb

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
  # pdb.set_trace()
  for component in components:
    if 'components' in component:
      # pdb.set_trace()
      lista = extraerComponents(component.pop('components'), lista)
    elif 'columns' in component:
      lista = extraerComponents(component.pop('columns'), lista)
    if 'key' in component:
      lista.append(component)
  return lista

lista_components = []
lista_components = extraerComponents(encuesta['components'], lista_components)

# tipos de components disponibles
set([component['type'] for component in lista_components])

pregunta_types = ['button', 'checkbox', 'number', 'radio', 'select', 'survey', 'textfield']
preguntas = [component for component in lista_components if component['type'] in pregunta_types]
columns = []
required = {}
for pregunta in preguntas:
  if pregunta['key'] == 'consultaEspacioOrden':
    pregunta_required = True
  elif 'validate' in pregunta:
    pregunta_required = pregunta['validate']['required']
  else:
    pregunta_required = False
  if pregunta['type'] == 'survey':
    for question in pregunta['questions']:
      required['{}.{}'.format(pregunta['key'], question['value'])] = pregunta_required
      columns.append('{}.{}'.format(pregunta['key'], question['value']))
  else:
    required[pregunta['key']] = pregunta_required
    columns.append(pregunta['key'])

###

with open('data/20190507_0239.json') as filein:
  json_in = json.load(filein)

data_json = []
for submission in json_in:
  datum = submission['data']
  if ('enviar' in datum) and datum['enviar']:
    data_json.append(datum)

parents = {}
for datum in data_json:
  for datum_key, datum_value in datum.items():
    if type(datum_value) is list:
      for element in datum_value:
        if type(element) is dict:
          if datum_key not in parents:
            parents[datum_key] = set()
          for element_key in element.keys():
            parents[datum_key].add(element_key)

json_new = []
for datum in data_json:
  datum_new = {}
  for datum_key, datum_value in datum.items():
    if datum_key in parents:
      elements = datum_value
      for children_key in parents[datum_key]:
        children_value = []
        for element in elements:
          if children_key in element:
            children_value.append(element[children_key])
          else:
            children_value.append(None)
        datum_new[children_key] = children_value
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

# if required and '': 'No corresponde', recorrer listas
json_new = []
values = set()
for datum in data_json:
  datum_new = {}
  for key, is_required in required.items():
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
data_json = data_json.reindex(labels=columns, axis='columns')
data_json.to_csv('data/out.csv')

###

data_csv = pd.read_csv('data/20190507_0239.csv')
columns_new = []
for column in data_csv.columns:
  column = column.split('.')
  try:
    int(column[-1])
    column = '.'.join(column[-2:])
  except ValueError:
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

# mover código de parse acá
# consultaEspacioCual_3
# fixMultiple
# código {} inválido