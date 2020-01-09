import kubernetes
import time

print('Started ready check for Pods')

# ------------------------------------

kubernetes.config.load_incluster_config()
api_instance = kubernetes.client.CoreV1Api()


def fetch_pod_status():
   status = True
   api_response = api_instance.list_pod_for_all_namespaces(watch=False)

   for i in api_response.items:
      if i.status.phase == "Running":
         pass
      elif i.status.phase == "Succeeded":
         pass
      else:
         status = False         

   return status 

# ------------------------------------

setup_wait = True
while setup_wait:
   print('Waiting for pods to become ready')
   time.sleep(20)
                    
   if fetch_pod_status() == True:
      time.sleep(20)
      if fetch_pod_status() == True:
         print('All Pods are ready, continuing with next step')
         setup_wait = False
         time.sleep(10)