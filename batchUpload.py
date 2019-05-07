import json
import requests

api = 'http://api.relevamientotrans.tk'
form_path = 'encuesta'

url = '/'.join([api, form_path, 'submission'])

filein = 'data/20190507_fixed.json'
token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjp7Il9pZCI6IjVjNzYwNmNlZmNhMDllMjU1YzFjMzkzZiJ9LCJmb3JtIjp7Il9pZCI6IjVjNzYwMWU1ZTE3YjMzMjI3MDk3MWY2OCJ9LCJpYXQiOjE1NTcxOTQ5NDAsImV4cCI6MTU1NzIwOTM0MH0.7JozAtXNBKJlob75ad4RQMSIjja7yfk2E0LYDyLBTME'

# filein = input('filein: ')
# token = input('token: ')

headers = {
  'x-jwt-token': token
}

with open(filein) as filein:
  json_in = json.load(filein)

failed = []

for submission in json_in:
  numencuesta = None

  submission_id = submission['_id']
  submission_data = submission['data']

  if 'numencuesta' in submission_data:
    numencuesta = submission_data['numencuesta']

  exists = requests.get(
    '/'.join([api, form_path, 'exists']),
    params={'data.numencuesta': numencuesta}
  )

  # if exists.ok:
  if True:
    overwrite = None
    overwrite = 'y'
    while overwrite not in ['y', 'n']:
      overwrite = input(
        'numencuesta {} already exists. Overwrite? y/n: '.format(numencuesta)
      )
    if overwrite == 'y':
      response = requests.put('/'.join([url, submission_id]), headers=headers, json=submission)
    else:
      continue
  else:
    response = requests.post(url, headers=headers, json=submission)
  if response.ok:
    print('Success! numencuesta: {} ({})'.format(numencuesta, response.request.method))
  else:
    print('Failed! numencuesta: {} ({})'.format(numencuesta, response.request.method))
    try:
      response_json = response.json()
      response_details = response_json['details']
      for detail in response_details:
        print(detail['message'])
    except:
      print('Unknown failure')
    print()
    failed.append(submission)

with open('failed.json', 'w') as fileout:
  json.dump(failed, fileout)
