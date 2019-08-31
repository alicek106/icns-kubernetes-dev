from __future__ import print_function
from flask import request
from flask_restful import Resource
from controller.DplController import DplController

class DplResource(Resource):
    def put(self):
        content = request.get_json(silent=True)
        return DplController().createDeployment(content)

    def get(self):
        content = request.get_json(silent=True)
        return DplController().getDeployment(content), 200

class DplResourceByName(Resource):
    def get(self, name=None):
        content = request.get_json(silent=True)
        return DplController().getDeploymentByName(content, name), 200

    def delete(self, name=None):
        content = request.get_json(silent=True)
        return DplController().deleteDeployment(content, name)