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
    try:
      self.value = int(value)
    except:
      pass

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


def get_values(component, codigos):
  values = [{'value': None, 'label': None}]
  if component['type'] in ['radio', 'survey']:
    values = component['values']
  elif component['type'] in ['select']:
    dataSrc = component['dataSrc']
    if dataSrc == 'url':
      pass
    elif dataSrc in ['values', 'json']:
      values = component['data'][dataSrc]
  elif component['type'] in ['number', 'textfield']:
    if component['key'] in codigos.key.values:
      values = codigos.loc[
        codigos['key'] == component['key'],
        ['value', 'label']
      ].to_dict(orient='records')
    else:
      pass
      # print('number/textfield sin manual de códigos: ' + component['key'])
  elif component['type'] in ['button', 'checkbox']:
    pass
  # pdb.set_trace()
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
intervenciones =  [
  {"value": "1", "label": "Inyección de siliconas"},
  {"value": "2", "label": "Implante de prótesis"},
  {"value": "3", "label": "Tratamiento hormonal"},
  {"value": "4", "label": "Intervención quirúrgica genital"},
  {"value": "5", "label": "Mastectomía"},
  {"value": "6", "label": "Intervención quirúrgica facial"},
  {"value": "7", "label": "Otras"}
]
intervenciones = pd.DataFrame(intervenciones)
intervenciones['key'] = 'intervencion'
codigos = codigos.append(intervenciones, ignore_index=True, sort=False)

with open('encuesta.json') as filein:
  encuesta = json.load(filein)

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

values = []
for pregunta in preguntas:
  if pregunta['type'] == 'survey':
    for question in pregunta['questions']:
      for value in get_values(pregunta, codigos):
        value = Value('radio', pregunta['key'], pregunta['label'], question['value'], question['label'], value['value'], value['label']).as_dict()
        values.append(value)
  elif pregunta['type'] == 'datagrid':
    for component in pregunta['components']:
      for value in get_values(component, codigos):
        hija_key = hija_label = None
        if len(pregunta['components']) > 1:
          hija_key = component['key']
          hija_label = component['label']
        else:
          pregunta['key'] = component['key']
          pregunta['label'] = component['label']
        value = Value(component['type'], pregunta['key'], pregunta['label'], hija_key, hija_label, value['value'], value['label']).as_dict()
        values.append(value)
  else:
    for value in get_values(pregunta, codigos):
      value = Value(pregunta['type'], pregunta['key'], pregunta['label'], None, None, value['value'], value['label']).as_dict()
      values.append(value)

values = pd.DataFrame(values, columns=['tipo', 'madre_key', 'madre_label', 'hija_key', 'hija_label', 'columna', 'value', 'label'])
values['columna'] = values.apply(lambda x: '.'.join(filter(None, (x['madre_key'], x['hija_key']))), axis=1)
values.to_excel('values.xlsx', index=False)