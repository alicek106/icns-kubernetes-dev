from kubernetes import client

class ServiceMessage:
   name = None
   type = None # 'NodePort' or 'ClusterIP'
   namespace = None
   selector = {'key':None, 'value':None}
   ports = []

   def __init__(self, content):
       self.name = content['name']
       self.type = content['type']
       self.namespace = content['namespace']
       self.selector['key'] = content['selector']['key']
       self.selector['value'] = content['selector']['value']
       self.ports = []
       for port in content['ports']:
           self.ports.append(
               client.V1ServicePort(
                   name=port['name'],
                   port=port['port'],
                   target_port=port['targetPort'],
                   protocol='TCP'
               )
           )