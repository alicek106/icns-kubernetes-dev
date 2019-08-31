from __future__ import print_function
import urllib3, base64, os
from kubernetes import client
import json
from requests import get
from kubernetes.client.rest import ApiException
from model.DeploymentMessage import DeploymentMessage
from model.Error import Error
import pprint
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class DplController:
    def __getApiInstance(self, decodedToken):
        configuration = client.Configuration()
        configuration.host = ("https://" + os.environ['KUBERNETES_PORT_443_TCP_ADDR'])
        configuration.verify_ssl = False
        configuration.api_key = {"authorization": "Bearer " + decodedToken}
        client.Configuration.set_default(configuration)
        v1 = client.AppsV1Api(client.ApiClient(configuration))
        return v1

    def getDeployment(self, content):
        decodedToken = base64.decodebytes(str.encode(content['token'])).decode()
        namespace = content['namespace']
        headers = {'Authorization': 'Bearer %s' % decodedToken}
        url = 'https://%s%s' % (os.environ['KUBERNETES_PORT_443_TCP_ADDR'],
                                '/apis/apps/v1beta1/namespaces/%s/deployments' % namespace);
        output = json.loads(get(url, headers=headers, verify=False).content.decode('utf-8'))
        return output

    # TODO : replcase 'default' namespace to corresponding namespace, 2018 09 19 23:21 (Complete)
    def getDeploymentByName(self, content, name):
        decodedToken = base64.decodebytes(str.encode(content['token'])).decode()
        namespace = content['namespace']
        fieldSelector = 'metadata.name=%s' % name
        headers = {'Authorization': 'Bearer %s' % decodedToken}
        url = 'https://%s%s';
        url = url % (os.environ['KUBERNETES_PORT_443_TCP_ADDR'], ('/apis/apps/v1beta1/namespaces/%s/deployments' % namespace)
                     + '?fieldSelector=' + fieldSelector)
        output = json.loads(get(url, headers=headers, verify=False).content.decode('utf-8'))
        return output

    # TODO : Implement Persistent Storage Mount, 2018 09 19 23:33 (Complete)
    # TODO : Add exception for not using PVC in requested json content, 2018 09 20 23:40
    def createDeployment(self, content):

        dplMessage = DeploymentMessage(content)
        decodedToken = base64.decodebytes(str.encode(content['token'])).decode()
        api_instance = self.__getApiInstance(decodedToken)

        generalLabel = {'icns.k8s.cloud/uuid': dplMessage.deploymentName}
        for key in dplMessage.labels:
            generalLabel['icns.k8s.cloud/'+ key] = dplMessage.labels[key]

        envList = []
        for env in dplMessage.env:
            envList.append(client.V1EnvVar(name=env['name'], value=env['value']))

        portList = []
        for port in dplMessage.ports:
            portList.append(client.V1ContainerPort(name=port['name'], container_port=int(port['port'])))
        if 'true' in dplMessage.sshEnabled:
            portList.append(client.V1ContainerPort(name='ssh',container_port=22))

        ######## Objects
        metadata = client.V1ObjectMeta(
            namespace=dplMessage.namespace,
            name=dplMessage.deploymentName,
            labels=generalLabel)

        ## 2018.10.15 12:49 Containers object is seperated from spec, because of volume mount enable
        podSpec = client.V1PodSpec(
            containers=[
                client.V1Container(
                    name=dplMessage.deploymentName,
                    image=dplMessage.image,
                    env=envList,
                    ports=portList,
                    image_pull_policy="Always",
                    resources=client.V1ResourceRequirements(
                        limits=dplMessage.resources['limit'],
                        requests=dplMessage.resources['request']
                    )
                )
            ]
        )

        # TODO : Add exception for object-removal. 2018.12.25 21:33
        # Because image is too big, percvlab/objectremoval:0.1 image exist only in icns-128.
        if content['type'] == 'object-removal':
            podSpec.node_selector = {"kubernetes.io/hostname":"icns-128"}


        if dplMessage.pv['enabled'] == 'true':
            podSpec.volumes = [client.V1Volume(
                name='%s-%s' % (dplMessage.userName, dplMessage.pv['pvName']),
                persistent_volume_claim=client.V1PersistentVolumeClaimVolumeSource(
                    claim_name='%s-%s' % (dplMessage.userName, dplMessage.pv['pvName'])
                )
            )]
            podSpec.containers[0].volume_mounts = [client.V1VolumeMount(
                mount_path=dplMessage.pv['mountPath'],
                name='%s-%s' % (dplMessage.userName, dplMessage.pv['pvName']),
                read_only=eval(dplMessage.pv['readOnly'])
            )]

        spec = client.V1beta2DeploymentSpec(
            replicas=dplMessage.replicas,
            selector=client.V1LabelSelector(
                match_labels={'icns.k8s.cloud/uuid': dplMessage.deploymentName},
            ),

            template=client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(labels=generalLabel),
                spec=podSpec
            )
        )

        body = client.AppsV1beta1Deployment(
            kind='Deployment',
            metadata=metadata,
            spec=spec
        )

        try:
            api_instance.create_namespaced_deployment(namespace=dplMessage.namespace, body=body)
            return Error(200, 'success').serialize(), 200
        except ApiException as e:
            error = json.loads(e.body)
            return Error(409, 'Reason: %s, %s' % (error['reason'], error['message'])).serialize(), 409

    def deleteDeployment(self, content, name):
        decodedToken = base64.decodebytes(str.encode(content['token'])).decode()
        namespace = content['namespace']
        deleteOptions = client.V1DeleteOptions() # https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/V1DeleteOptions.md
        api_instance = self.__getApiInstance(decodedToken)
        try:
            api_response = api_instance.delete_namespaced_deployment(
                name=name,
                namespace=namespace,
                body=deleteOptions
            )
            return Error(200, 'success').serialize(), 200
        except ApiException as e:
            error = json.loads(e.body)
            return Error(e.status, 'Reason: %s, %s' % (error['reason'], error['message'])).serialize(), e.status

## TODO 2018. 09. 18 00:16. Convert main function (create Deployment) to member function of DplController!! (Complete)
## TODO 2018. 09. 21 00:06. Implement Service Object for exposing Deployment to external world.
if __name__ == '__main__':
    print('test')
    a = 'True'
    print(type(a))
    print(type(eval(a)))