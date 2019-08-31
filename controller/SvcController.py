from __future__ import print_function
import urllib3, base64, os
from kubernetes import client
import json
from requests import get
from kubernetes.client.rest import ApiException
from model.DeploymentMessage import DeploymentMessage
from model.Error import Error
from model.ServiceMessage import ServiceMessage
import pprint
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class SvcController:
    def __getApiInstance(self, decodedToken):
        configuration = client.Configuration()
        configuration.host = ("https://" + os.environ['KUBERNETES_PORT_443_TCP_ADDR'])
        configuration.verify_ssl = False
        configuration.api_key = {"authorization": "Bearer " + decodedToken}
        client.Configuration.set_default(configuration)
        v1 = client.CoreV1Api(client.ApiClient(configuration))
        return v1

    # 2018. 10. 04. 13:52 It works well
    def getService(self, content):
        decodedToken = base64.decodebytes(str.encode(content['token'])).decode()
        namespace = content['namespace']
        headers = {'Authorization': 'Bearer %s' % decodedToken}
        url = 'https://%s%s' % (os.environ['KUBERNETES_PORT_443_TCP_ADDR'],
                                '/api/v1/namespaces/%s/services' % namespace);
        output = json.loads(get(url, headers=headers, verify=False).content.decode('utf-8'))
        return output

    # 2018. 10. 04. 13:52 It works well
    def getServiceByName(self, content, name):
        decodedToken = base64.decodebytes(str.encode(content['token'])).decode()
        namespace = content['namespace']
        fieldSelector = 'metadata.name=%s' % name
        headers = {'Authorization': 'Bearer %s' % decodedToken}
        url = 'https://%s%s';
        url = url % (os.environ['KUBERNETES_PORT_443_TCP_ADDR'], ('/api/v1/namespaces/%s/services' % namespace)
                     + '?fieldSelector=' + fieldSelector)
        output = json.loads(get(url, headers=headers, verify=False).content.decode('utf-8'))
        return output

    # 2018. 10. 04 15:41 It works well
    def createService(self, content):
        serviceMessage = ServiceMessage(content)
        decodedToken = base64.decodebytes(str.encode(content['token'])).decode()
        api_instance = self.__getApiInstance(decodedToken)

        body = client.V1Service(
            api_version='v1',
            kind='Service',
            metadata=client.V1ObjectMeta(name=serviceMessage.name, namespace=serviceMessage.namespace),
            spec=client.V1ServiceSpec(
                type=serviceMessage.type,
                selector={serviceMessage.selector['key']: serviceMessage.selector['value']},
                ports=serviceMessage.ports
            )
        )

        try:
            api_response = api_instance.create_namespaced_service(serviceMessage.namespace, body)
            return Error(200, 'success').serialize(), 200
        except ApiException as e:
            print(e.body)
            error = json.loads(e.body)
            return Error(e.status, 'Reason: %s, %s' % (error['reason'], error['message'])).serialize(), e.status

    # 2018. 10. 04 16:20 Test Complete.
    # 2018. 10. 04 16:38 Success integration test with deployment API!
    # TODO : ADD exception to deployment for not using PV and ssh
    def deleteDeployment(self, content, name):
        decodedToken = base64.decodebytes(str.encode(content['token'])).decode()
        namespace = content['namespace']
        body = client.V1DeleteOptions()
        api_instance = self.__getApiInstance(decodedToken)

        try:
            api_response = api_instance.delete_namespaced_service(name, namespace, body)
            return Error(200, 'success').serialize(), 200
        except ApiException as e:
            error = json.loads(e.body)
            return Error(e.status, 'Reason: %s, %s' % (error['reason'], error['message'])).serialize(), e.status

if __name__ == '__main__':
    rawToken = "ZXlKaGJHY2lPaUpTVXpJMU5pSXNJblI1Y0NJNklrcFhWQ0o5LmV5SnBjM01pT2lKcmRXSmxjbTVsZEdWekwzTmxjblpwWTJWaFkyTnZkVzUwSWl3aWEzVmlaWEp1WlhSbGN5NXBieTl6WlhKMmFXTmxZV05qYjNWdWRDOXVZVzFsYzNCaFkyVWlPaUprWldaaGRXeDBJaXdpYTNWaVpYSnVaWFJsY3k1cGJ5OXpaWEoyYVdObFlXTmpiM1Z1ZEM5elpXTnlaWFF1Ym1GdFpTSTZJbVJsWm1GMWJIUXRkRzlyWlc0dGRHSnVabVFpTENKcmRXSmxjbTVsZEdWekxtbHZMM05sY25acFkyVmhZMk52ZFc1MEwzTmxjblpwWTJVdFlXTmpiM1Z1ZEM1dVlXMWxJam9pWkdWbVlYVnNkQ0lzSW10MVltVnlibVYwWlhNdWFXOHZjMlZ5ZG1salpXRmpZMjkxYm5RdmMyVnlkbWxqWlMxaFkyTnZkVzUwTG5WcFpDSTZJbUpsTUdVNE5HTTNMV00yWTJRdE1URmxPQzFoT1RZMExUazROR0psTVRkbU1ERXhNeUlzSW5OMVlpSTZJbk41YzNSbGJUcHpaWEoyYVdObFlXTmpiM1Z1ZERwa1pXWmhkV3gwT21SbFptRjFiSFFpZlEubTBiZGRKUzMwTENkZ29LWndfVk5tTFgyMWJBV2lJTFdVZFdrcm5rNGNheURvemJ5M2Z3ZUdRbnY2NWpDS2NKc3UwVjVERld3UTlLcmpsM1RIMVAzblZ4Rm5YRmpROVlVMVBoeG5yY3RWYUxpLVJKS0FXdWpqN05TdGJyaUZfU1FiTW80YXZYbVZkbzZwU3BibHppSTRka3h6NEZ4N0k4UUhTNFR6eEdWa1c0VWlIcEswOG54djFpNnlRRkhrWTJsbEdkZ0RZanF2THdRaENENzJNeXBGS1FablBLNjFRZXd3SDVKa0k5Mnh5dXNNQlRaZkllVlRzTzg1X2t0RDNsNU83anlUSDdSRDljQUZRbGd4U3pBMmdYMTFhV0Ytc1B6a2VnSW94QXBibmhaMjJoaTZodW5pYVByemI4SnotMkhEeFpCMldMMVNuOTlsVk9WeE5kSHpR"
    decodedToken = base64.decodebytes(str.encode(rawToken)).decode()
    configuration = client.Configuration()
    configuration.host = ("https://" + os.environ['KUBERNETES_PORT_443_TCP_ADDR'])
    configuration.verify_ssl = False
    configuration.api_key = {"authorization": "Bearer " + decodedToken}
    client.Configuration.set_default(configuration)
    api_instance = client.CoreV1Api(client.ApiClient(configuration))

    namespace = 'default'
    body = client.V1Service(
        api_version='v1',
        kind='Service',
        metadata=client.V1ObjectMeta(name='mysvc', namespace='default'),
        spec=client.V1ServiceSpec(
            type="NodePort",
            selector={"app":"myserviceapp"},
            ports=[
                client.V1ServicePort(name='ssh', port=22, target_port=22, protocol='TCP')
            ]
        )
    )

    try:
        api_response = api_instance.create_namespaced_service(namespace, body)
        pprint.pprint(api_response)
    except ApiException as e:
        print("Exception when calling CoreV1Api->create_namespaced_service: %s\n" % e)