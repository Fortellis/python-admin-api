from flask import Flask, request
from flask_restful import Resource, Api, reqparse, abort

import jwt 

from jwt import PyJWKClient

import json

import jsonschema
from jsonschema import validate

PREFIX = 'Bearer '

app = Flask(__name__)
api = Api(app)

class Health(Resource):
    def get(self):
        return {'status': 'up'}

api.add_resource(Health, '/health')

class Activate(Resource):
    def post(self):
        app.logger.debug('Headers: %s', request.headers)
        app.logger.debug('Body: %s', request.get_data().decode())

        token = request.headers['Authorization'][len(PREFIX):]

        url = "https://identity.fortellis.io/oauth2/aus1p1ixy7YL8cMq02p7/v1/keys"

        app.logger.debug('This is the URL: %s', url)

        jwks_client = PyJWKClient(url)

        app.logger.debug('This is the jwks_client: %s', jwks_client)

        signing_key = jwks_client.get_signing_key_from_jwt(token)

        app.logger.debug('This is the signing_key: %s', signing_key)

        unverified_header = jwt.get_unverified_header(token)

        app.logger.debug('This is the unverified_header: %s', unverified_header)

        data = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience="fortellis",
            options={"verify_exp": True},
        )

        print(data)

        with open('schema.json') as json_file:
            payloadSchema = json.load(json_file)
            validate(instance=request.get_data().decode(), schema=payloadSchema)

        entry = json.loads(request.get_data().decode())

        with open('connectionRequests.json', 'r+') as file:
            file_data = json.load(file)
            file_data['connectionRequests'].append(entry)
            file.seek(0)
            json.dump(file_data, file, indent = 2)
        


        return {"links":[{"href":"string","rel":"string","method":"string","title":"string"}]}
    
api.add_resource(Activate, '/activate')

class Deactivate(Resource):
    def post(self, connectionId):
        app.logger.debug('Headers: %s', request.headers)
        app.logger.debug('Body: %s', request.get_data().decode())
        app.logger.debug('This is the path parameter: %s', connectionId)

        token = request.headers['Authorization'][len(PREFIX):]

        url = "https://identity.fortellis.io/oauth2/aus1p1ixy7YL8cMq02p7/v1/keys"

        app.logger.debug('This is the URL: %s', url)

        jwks_client = PyJWKClient(url)

        app.logger.debug('This is the jwks_client: %s', jwks_client)

        signing_key = jwks_client.get_signing_key_from_jwt(token)

        app.logger.debug('This is the signing_key: %s', signing_key)

        unverified_header = jwt.get_unverified_header(token)

        app.logger.debug('This is the unverified_header: %s', unverified_header)

        data = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience="fortellis",
            options={"verify_exp": True},
        )

        print(data)

        entry = connectionId

        with open('deactivationRequests.json', 'r+') as file:
            file_data = json.load(file)
            file_data['deactivationRequests'].append(entry)
            file.seek(0)
            json.dump(file_data, file, indent = 2)
        
        return {"links":[{"href":"string","rel":"string","method":"string","title":"string"}]}
    
api.add_resource(Deactivate, '/deactivate/<string:connectionId>')

class Delete(Resource):
    def post(self):
        with open('connectionRequests.json', 'r+') as file:
            parsed = json.load(file)
            print(json.dumps(parsed, indent=2, sort_keys=True))
            app.logger.debug('These are the current connection requests: %s', parsed)
            app.logger.debug('You have requested to delete the following subscription from the JSON file: %s', request.get_data().decode())
            app.logger.debug('This is the `subscriptionId` in the body: %s', request.json['subscriptionId'])
            subscriptionIdInRequest = request.json['subscriptionId']
            app.logger.debug('This is the subscriptionRequestId: %s', subscriptionIdInRequest)
            generatorList = parsed['connectionRequests']
            # Getting the dictionary in the list using the subscriptionIdInRequest
            generator = next(item for item in generatorList if item["subscriptionId"] == subscriptionIdInRequest)
            app.logger.debug('This is the generator: %s', generator)
            # Getting the index of the dictionary in the list. 
            generatorIndex = next((i for i, item in enumerate(generatorList) if item["subscriptionId"] == subscriptionIdInRequest), None)
            app.logger.debug('This is the index for the generator: %s', generatorIndex)
            file.truncate(0)

            newListOfConnectionRequests = {"connectionRequests" : [i for i in generatorList if not (i['subscriptionId'] == subscriptionIdInRequest)]} 
            app.logger.debug('This is the new list after removing the item in the request: %s', newListOfConnectionRequests)
            file.seek(0)
            json.dump(newListOfConnectionRequests, file, indent=2)


        return {"status": "200 - Success"}

api.add_resource(Delete, '/delete' )

class ConnectionRequests(Resource):
    def get(self):
        with open('connectionRequests.json', 'r+') as file:
            parsed = json.load(file)

        return parsed

api.add_resource(ConnectionRequests, '/connectionRequests')

class DeactivationRequests(Resource):
    def get(self):
        with open('deactivationRequests.json', 'r+') as file:
            parsed = json.load(file)

        return parsed

api.add_resource(DeactivationRequests, '/deactivationRequests')

if __name__ == '__main__':
    app.run(debug=True)