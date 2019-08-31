class DeploymentMessage:
    deploymentName = None
    userName = None
    image = None
    replicas = None
    sshEnabled = None
    namespace = None
    ports = [] # list
    env = [] # list
    labels = [] # list
    resources = [] # extra
    pv = [] # extra

    def __init__(self, content):
        self.namespace = content['namespace']
        self.deploymentName = content['deploymentName']
        self.userName = content['userName']
        self.image = content['image']
        self.replicas = content['replicas']
        self.sshEnabled = content['sshEnabled']
        self.ports = content['ports'] # Array
        self.env = content['env'] # Array
        self.labels = content['labels'] # Array
        self.resources = content['resources']
        self.pv = content['pv']