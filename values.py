import json
import pandas as pd
import pdb


class Value:
  def __init__(self, tipo, madre_key, madre_label, hija_key, hija_label, value, label):
    self.tipo = tipo
    self.madre_key = madre_key
    self.madre_label = madre_label
    self.hija_key = hija_key
    self.hija_label = hija_label
    self.value = value
    self.label = label

  def as_dict(self):
    value = {
      'tipo': self.tipo,
      'madre_key': self.madre_key,
      'madre_label': self.madre_label,
      'hija_key': self.hija_key,
      'hija_label': self.hija_label,
      'value': self.value,
      'label': self.label
    }
    return value


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


def get_values(component):
  values = []
  if component['type'] in ['radio', 'survey']:
    for value in component['values']:
      values.append(value)
  elif component['type'] in ['select']:
    pass
  elif component['type'] in ['number', 'textfield']:
    pass
  elif component['type'] in ['button', 'checkbox']:
    value = {'value': None, 'label': None}
    values.append(value)
    pass
  return values


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

with open('encuesta.json') as filein:
  encuesta = json.load(filein)

lista_components = []
lista_components = extraerComponents(encuesta['components'], lista_components)

# tipos de components disponibles
set([component['type'] for component in lista_components])

pregunta_types = ['button', 'checkbox', 'number', 'radio', 'select', 'survey', 'textfield', 'datagrid']
preguntas = [component for component in lista_components if component['type'] in pregunta_types]


values = []
for pregunta in preguntas:
  if pregunta['type'] == 'survey':
    for question in pregunta['questions']:
      for value in get_values(pregunta):
        value = Value('radio', pregunta['key'], pregunta['label'], question['value'], question['label'], value['value'], value['label']).as_dict()
        values.append(value)
  elif pregunta['type'] == 'datagrid':
    for component in pregunta['components']:
      for value in get_values(component):
        value = Value(component['type'], pregunta['key'], pregunta['label'], component['key'], component['label'], value['value'], value['label']).as_dict()
        values.append(value)
  else:
    for value in get_values(pregunta):
      value = Value(pregunta['type'], pregunta['key'], pregunta['label'], None, None, value['value'], value['label']).as_dict()
      values.append(value)
pdb.set_trace()