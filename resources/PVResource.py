from __future__ import print_function
from flask import request
from flask_restful import Resource
from controller.PVController import PVController

class PVResource(Resource):
    def get(self):
        content = request.get_json(silent=True)
        return PVController().getPersistentVolumeClaim(content)

    def put(self):
        content = request.get_json(silent=True)
        return PVController().createPersistentVolumeClaim(content)

class PVResourceByName(Resource):
    def delete(self, name=None):
        content = request.get_json(silent=True)
        return PVController().deletePersistentVolume(content, name)