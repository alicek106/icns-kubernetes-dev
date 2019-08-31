from kubernetes import client, config
from logger.Logger import logger
import hashlib
import re
import json
from controller.DplController import DplController

class K8sController:
    __configuration = config.load_incluster_config()
    __api_instance = client.CoreV1Api(client.ApiClient(__configuration))
    __rbac_api_instance = client.RbacAuthorizationV1Api(client.ApiClient(__configuration))

    def getNodeList(self):
        api_instance = client.CoreV1Api(client.ApiClient(self.__configuration))
        include_uninitialized = True  # bool | If true, partially initialized resources are included in the response. (optional)
        label = 'node-role.kubernetes.io/node'
        api_response = api_instance.list_node(label_selector=label,
                                              include_uninitialized=include_uninitialized)
        return api_response;

    def getAvailableResourceAllNodes(self, nodeList):
        # fieldSelector = 'spec.nodeName=icns-123,status.phase!=Failed,status.phase!=Succeeded'
        # fieldSelctor 'or' cannot applied, so I filtered in for statement whether it is worker node.
        v1 = client.CoreV1Api()
        api_response = v1.list_pod_for_all_namespaces()
        resources = {}

        for i in nodeList.items:
            resources[i.metadata.name] = \
        {
            'cpu': i.status.allocatable['cpu'],
            'memory': i.status.allocatable['memory'],
            'cpu_request':0,
            'memory_request':0,
            'cpu_limit':0,
            'memory_limit':0,
            'unlimited_pod':0
        }

        for i in api_response.items:
            if i.spec.node_name in resources:
                for j in i.spec.containers:
                    if j.resources.requests is not None:
                        # CPU Limit
                        resources[i.spec.node_name]['cpu_request'] += int(re.sub("\D", "", j.resources.requests['cpu']))
                        # Memory Limit
                        if 'G' in j.resources.requests['memory']:
                            resources[i.spec.node_name]['memory_request'] += int(
                                re.sub("\D", "", j.resources.requests['memory'])) * 1024
                        elif 'M' in j.resources.requests['memory']:
                            resources[i.spec.node_name]['memory_request'] += int(
                                re.sub("\D", "", j.resources.requests['memory']))

                    if j.resources.limits is not None:
                        # CPU Limit. Sometimes, limits.cpu doesn't exist but memory exist. so I added if statement
                        if 'cpu' in j.resources.limits:
                            resources[i.spec.node_name]['cpu_limit'] += int(re.sub("\D", "", j.resources.limits['cpu']))
                        # Memory Limit
                        if 'G' in j.resources.limits['memory']:
                            resources[i.spec.node_name]['memory_limit'] += int(
                                re.sub("\D", "", j.resources.limits['memory'])) * 1024
                        elif 'M' in j.resources.limits['memory']:
                            resources[i.spec.node_name]['memory_limit'] += int(
                                re.sub("\D", "", j.resources.limits['memory']))
                    else:
                        resources[i.spec.node_name]['unlimited_pod'] += 1

            else:
                continue

        return resources

    def createNamespace(self, id):
        body = client.V1Namespace(api_version='v1',
                                  kind='Namespace',
                                  metadata=client.V1ObjectMeta(name='%s-namespace' % id))
        self.__api_instance.create_namespace(body)
        logger.info('Created Namespace : %s-namespace' % id)
        return

    def createServiceAccount(self, id):
        namespace = '%s-namespace' % id
        body = client.V1ServiceAccount(api_version='v1',
                                       kind='ServiceAccount',
                                       metadata=client.V1ObjectMeta(name=id, namespace=namespace))
        self.__api_instance.create_namespaced_service_account(namespace, body)
        logger.info('Created Servie Account : %s' % id)
        return

    def getSecretToken(self, id):
        namespace = '%s-namespace' % id
        sa_response = self.__api_instance.read_namespaced_service_account(id, namespace, exact=True, export=True)
        secret_response = self.__api_instance.read_namespaced_secret(sa_response.secrets[0].name, namespace, exact=True, export=True)
        logger.info('Returned Secret Token : %s' % (secret_response.data['token'][:10] + '...'))
        return secret_response.data['token']

    def createRoleBinding(self, id):
        namespace = '%s-namespace' % id
        roleName = hashlib.sha1(str.encode(id)).hexdigest()[:8] # $ID-role trigger bug! HaHa
        bindingName = "%s-binding" % roleName

        body = client.V1Role(api_version='rbac.authorization.k8s.io/v1',
                             kind='Role',
                             metadata=client.V1ObjectMeta(name=roleName, namespace=namespace),
                             rules=[client.V1PolicyRule(api_groups=['*'], resources=['*'], verbs=['*'])])
        self.__rbac_api_instance.create_namespaced_role(namespace=namespace, body=body)
        logger.info('Created Role : %s' % roleName)

        role_binding = client.V1RoleBinding(
        metadata=client.V1ObjectMeta(namespace=namespace, name=bindingName),
                                subjects=[client.V1Subject(name=id, kind="ServiceAccount", api_group="")],
                                role_ref=client.V1RoleRef(kind="Role", api_group="rbac.authorization.k8s.io",
                                name=roleName))
        self.__rbac_api_instance.create_namespaced_role_binding(namespace=namespace, body=role_binding)
        logger.info('Created Role Binding : %s' % bindingName)

    def checkValidUser(self, content):
        content['namespace'] = content['id'] + '-namespace'
        try:
            result = DplController().getDeployment(content)
            print(result)
            if '401' in json.dumps(result) and 'Unauthorized' in json.dumps(result): # error 401
                return 404
            else: # Success
                return 200
        except: # base64 Error
            return 500

    ## IMPORTANT! Below functions will not be used. Just for test!
    def deleteNamespace(self, namespace):
        self.__api_instance.delete_namespace(namespace, client.V1DeleteOptions())

    def deleteServiceAccount(self, id):
        namespace = '%s-namespace' % id
        self.__api_instance.delete_namespaced_service_account(id, namespace, client.V1DeleteOptions())

    def deleteRoleBinding(self, id):
        namespace = '%s-namespace' % id
        roleName = hashlib.sha1(str.encode(id)).hexdigest()[:8]  # $ID-role trigger bug! HaHa
        bindingName = "%s-binding" % roleName
        self.__rbac_api_instance.delete_namespaced_role(name=roleName, namespace=namespace, body=client.V1DeleteOptions())
        self.__rbac_api_instance.delete_namespaced_role_binding(name=bindingName, namespace=namespace, body=client.V1DeleteOptions())

if __name__ == '__main__':
    id = 'alicek107'
    # print(K8sController().getAvailableResourceAllNodes(K8sController().getNodeList()))
    # K8sController().deleteRoleBinding(id)
    # K8sController().createRoleBinding(id)
    # K8sController().createNamespace(id)
    # K8sController().createServiceAccount(id)
    # print(K8sController().deleteServiceAccount('alicek107'))
    # print(K8sController().deleteNamespace('%s-namespace' % 'alicek107'))