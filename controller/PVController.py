from __future__ import print_function
import urllib3, base64, os
from kubernetes import *
import pprint
from model.Error import Error
from kubernetes.client.rest import *
from requests import get
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class PVController:
    def getPersistentVolumeClaim(self, content):
        decodedToken = base64.decodebytes(str.encode(content['token'])).decode()
        namespace = content['namespace']
        headers = {'Authorization': 'Bearer %s' % decodedToken}
        url = 'https://%s%s' % (os.environ['KUBERNETES_PORT_443_TCP_ADDR'],
                                '/api/v1/namespaces/%s/persistentvolumeclaims' % namespace);
        output = json.loads(get(url, headers=headers, verify=False).content.decode('utf-8'))
        return output, 200

    def createPersistentVolumeClaim(self, content):
        pvName = '%s-%s' % (content['userName'], content['metadata']['name'])
        labels = {'icns.k8s.cloud.pv/uuid': pvName}
        for key in content['metadata']['labels']:
            labels['icns.k8s.cloud.pv/' + key] = content['metadata']['labels'][key]

        ## Step 1. Create PV using admin(default) Service Account for NFS
        if content['type'] == 'nfs':
            # TODO : NFS Volume Provisioner ! 2018. 09. 20
            labels['icns.k8s.cloud.pv/pv-type'] = 'nfs'
            admin_configuration = config.load_incluster_config()
            admin_api_instance = client.CoreV1Api(client.ApiClient(admin_configuration))
            spec = client.V1PersistentVolumeSpec(
                capacity={'storage':content['metadata']['capacity']},
                access_modes=['ReadWriteMany'],
                nfs=client.V1NFSVolumeSource(
                    path=content['metadata']['path'],
                    server=content['metadata']['server']
                )
            )
            body = kubernetes.client.V1PersistentVolume(
                kind='PersistentVolume',
                metadata=client.V1ObjectMeta(name=pvName, labels=labels),
                spec=spec
            )
            try:
                admin_api_instance.create_persistent_volume(body=body)
            except ApiException as e:
                error = json.loads(e.body)
                return Error(e.status, 'Reason: %s, %s' % (error['reason'], error['message'])).serialize(), e.status

        ## Step 2. Bind PV with PVC
        decodedToken = base64.decodebytes(str.encode(content['token'])).decode()
        api_instance = self.__getCoreApiInstance(decodedToken)
        body = kubernetes.client.V1PersistentVolumeClaim(
            kind='PersistentVolumeClaim',
            metadata=client.V1ObjectMeta(name=pvName, namespace=content['namespace'], labels=labels),
            spec=client.V1PersistentVolumeClaimSpec(
                access_modes=['ReadWriteMany'],
                resources=client.V1ResourceRequirements(
                    requests={'storage':content['metadata']['capacity']}
                ),
                volume_name=pvName
            )
        )
        try:
            api_instance.create_namespaced_persistent_volume_claim(body=body,namespace=content['namespace'])
            return Error(200, 'success').serialize(), 200
        except ApiException as e:
            error = json.loads(e.body)
            return Error(e.status, 'Reason: %s, %s' % (error['reason'], error['message'])).serialize(), e.status

    def deletePersistentVolume(self, content, name):
        # for PVC
        name = '%s-%s' % (content['userName'], name)
        decodedToken = base64.decodebytes(str.encode(content['token'])).decode()
        api_instance = self.__getCoreApiInstance(decodedToken)
        namespace = content['namespace']

        # for PV
        admin_configuration = config.load_incluster_config()
        admin_api_instance = client.CoreV1Api(client.ApiClient(admin_configuration))

        try:
            api_instance.delete_namespaced_persistent_volume_claim(
                name=name, namespace=namespace,body=client.V1DeleteOptions()
            )
            admin_api_instance.delete_persistent_volume(name=name, body=client.V1DeleteOptions())
            return Error(200, 'success').serialize(), 200
        except ApiException as e:
            error = json.loads(e.body)
            return Error(e.status, 'Reason: %s, %s' % (error['reason'], error['message'])).serialize(), e.status


    def __getCoreApiInstance(self, decodedToken):
        configuration = client.Configuration()
        configuration.host = ("https://" + os.environ['KUBERNETES_PORT_443_TCP_ADDR'])
        configuration.verify_ssl = False
        configuration.api_key = {"authorization": "Bearer " + decodedToken}
        client.Configuration.set_default(configuration)
        v1 = client.CoreV1Api(client.ApiClient(configuration))
        return v1

if __name__ == '__main__':
    PVController().getPersistentVolumeClaim(None)