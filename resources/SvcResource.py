from __future__ import print_function
from flask import request
from flask_restful import Resource
from controller.SvcController import SvcController

class SvcResource(Resource):
    def put(self):
        content = request.get_json(silent=True)
        return SvcController().createService(content)

    def get(self):
        content = request.get_json(silent=True)
        return SvcController().getService(content), 200

class SvcResourceByName(Resource):
    def get(self, name=None):
        content = request.get_json(silent=True)
        return SvcController().getServiceByName(content, name), 200

    def delete(self, name=None):
        content = request.get_json(silent=True)
        return SvcController().deleteDeployment(content, name)