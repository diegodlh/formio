# comparar archivo csv vs json
import json
import pandas as pd
import pdb

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
for pregunta in preguntas:
  if pregunta['type'] == 'survey':
    for question in pregunta['questions']:
      columns.append('{}.{}'.format(pregunta['key'], question['value']))
  else:
    columns.append(pregunta['key'])

###

with open('data/20190507_0239.json') as filein:
  json_in = json.load(filein)

data_json = []
for submission in json_in:
  data_json.append(submission['data'])

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

# if required and None: 'No corresponde', recorrer listas
json_new = []
values = set()
for datum in data_json:
  datum_new = {}
  for pregunta in preguntas:
    if pregunta['key'] in datum:
      respuesta = datum[pregunta['key']]
      if isinstance(respuesta, list):
        # respuesta_new = []
        for value in respuesta:
          values.add(value)
      elif not isinstance(respuesta, dict):
        # pending normalize before
        value = respuesta
        values.add(value)
pdb.set_trace()

data_json = pd.io.json.json_normalize(data_json)  # así como está sólo desagrega subitems de survey
# del json_in, json_out

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

print('columns in json (enviado) not in csv:')
data_json_enviado = data_json[~data_json.enviar.isna()].dropna(axis='columns', how='all')
print([column for column in data_json_enviado.columns if column not in data_csv.columns])
# sólo sobra columna violentxs.6 si descarto encuestas sin enviar

print('columns in csv not in json:')
print([column for column in data_csv.columns if column not in data_json.columns])

# ordenar preguntas según orden encuesta

