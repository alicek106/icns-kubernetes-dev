from flask_restful import Resource
from flask import request
from dao.ServiceAccountDao import ServiceAccountDAO
from logger.Logger import logger
import pymysql
from model.Error import Error
import time
from controller.K8sController import K8sController
import json
from flask import Response

# SAC : Service Account Claim
# Input : id, name, comment
class CreateSAC(Resource):
    def post(self):
        content = request.get_json(silent=True)
        print(content)
        logger.info('Create SAC Input Data : %s, %s, %s' %(content['id'], content['name'], content['comment']))

        try:
            serviceAccountDao = ServiceAccountDAO()
            serviceAccountDao.putServiceAccount(content['id'], content['name'], 'pending', int(time.time()))
            serviceAccountDao.putServiceAccount_claim(content['id'], content['name'], content['comment'], int(time.time()))
        except pymysql.err.IntegrityError as e:
            logger.error("Already exist primary key")
            return Error(409, str(e)).serialize(), 409

        return {}, 200

# Input : id, boolean
class UpdateSA(Resource):
    def delete(self):
        content = request.get_json(silent=True)
        logger.info('Delete SA Input Data : %s' % (content['id']))
        K8sController().deleteRoleBinding(content['id'])
        K8sController().deleteServiceAccount(content['id'])
        K8sController().deleteNamespace('%s-namespace' % content['id'])
        ServiceAccountDAO().deleteServiceAccount(content['id'])
        return {'result': 1}, 200

    def put(self):
        content = request.get_json(silent=True)
        logger.info('Update SA Input Data : %s, %s' % (content['id'], content['approval']))

        serviceAccountDao = ServiceAccountDAO()
        if content['approval'] is 1:

            # TODO : replace token to generated token from kubernetes.
            K8sController().createNamespace(content['id'])
            K8sController().createServiceAccount(content['id'])
            ## After created sa, we have to wait about 0.1sec for creating secret
            while True:
                time.sleep(0.1)
                try:
                    token = K8sController().getSecretToken(content['id'])
                    break;
                except TypeError as e:
                    print(str(e))
            # TODO : It will be replaced to real value later.

            K8sController().createRoleBinding(content['id'])
            serviceAccountDao.updateServiceAccount(content['id'], 'registered-initial')
            return {'token':token}, 200

        else:
            serviceAccountDao.updateServiceAccount(content['id'], 'denied')
            return Error(203, 'Permission denied').serialize(), 203

class CheckValidSA(Resource):
    def post(self):
        content = request.get_json(silent=True)
        print(content)
        logger.info('Login SA, Input Data : %s, %s' % (content['id'], content['token']))
        result = K8sController().checkValidUser(content)
        if result is 200:
            logger.info('Login success : ' + content['id'] )
            userName = ServiceAccountDAO().getOneServiceAccount(id=content['id']).fetchone()
            return Response(response=json.dumps({'name':userName['name']}, ensure_ascii=False).encode('utf8'),
                            status=result,
                            content_type='application/json; charset=utf-8')
        else:
            logger.error('Login Failed : ' + content['id'])
            return Error(result, 'Login failed').serialize(), result