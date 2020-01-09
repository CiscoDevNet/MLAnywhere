import requests
import json
import os
import time

print('Started ready check for notebooks')

# ------------------------------------

def get_notebooks():
   url = 'http://{ip}:{port}/jupyter/api/namespaces/ciscodemo/notebooks'.format(
      ip = os.environ['INGRESS_HOST'],
      port = os.environ['INGRESS_PORT']
   )
   nblist = requests.get(url, verify=False)
   nblist = json.loads(nblist.content)
   return nblist['notebooks']

# ------------------------------------           

nb_wait = True
counter = 0
while nb_wait:
   print('Waiting for notebooks to become ready')
   time.sleep(20)
              
   counter += 1
   loop_ready = True
   for nb in get_notebooks():
      if nb['status'] != 'running':
         loop_ready = False
         
   if loop_ready == True:
      print('Notebooks are ready, continuing with the next step')
      nb_wait = False
                
   if counter > 1000:
      print('Timeout error, aborting')
      nb_wait = False


   