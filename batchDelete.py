import requests
import pdb

api = 'http://api.relevamientotrans.tk'
form_path = 'encuesta-ok'

url = '/'.join([api, form_path, 'submission'])

token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjp7Il9pZCI6IjVjNzYwNmNlZmNhMDllMjU1YzFjMzkzZiJ9LCJmb3JtIjp7Il9pZCI6IjVjNzYwMWU1ZTE3YjMzMjI3MDk3MWY2OCJ9LCJpYXQiOjE1NTcxOTQ5NDAsImV4cCI6MTU1NzIwOTM0MH0.7JozAtXNBKJlob75ad4RQMSIjja7yfk2E0LYDyLBTME'
# token = input('token: ')

headers = {'x-jwt-token': token}

submissions = requests.get(url, headers=headers, params={'limit': 1000}).json()
# pdb.set_trace()

for submission in submissions:
  submission_id = submission['_id']
  submission_data = submission['data']
  numencuesta = None
  if 'numencuesta' in submission_data:
    numencuesta = submission_data['numencuesta']

  response = requests.delete('/'.join([url, submission_id]), headers=headers)
  if response.ok:
    print('Deleted numencuesta {}'.format(numencuesta))
  else:
    pdb.set_trace()
    print('Failed to delete numencuesta {}'.format(numencuesta))
