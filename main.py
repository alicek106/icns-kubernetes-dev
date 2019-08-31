from flask import Flask
from flask_restful import Api
from resources.SAResource import *
from resources.DplResource import *
from resources.PVResource import *
from resources.SvcResource import *

app = Flask(__name__)
api = Api(app)

if __name__ == '__main__':
    api.add_resource(CreateSAC, '/v1/api/user')
    api.add_resource(UpdateSA, '/v1/api/user')
    api.add_resource(CheckValidSA, '/v1/api/user/validation')

    api.add_resource(DplResource, '/v1/api/deployment')
    api.add_resource(DplResourceByName, '/v1/api/deployment/<string:name>')

    api.add_resource(PVResource, '/v1/api/pvc')
    api.add_resource(PVResourceByName, '/v1/api/pvc/<string:name>')

    api.add_resource(SvcResource, '/v1/api/svc')
    api.add_resource(SvcResourceByName, '/v1/api/svc/<string:name>')

    app.run(host='0.0.0.0', port=80)