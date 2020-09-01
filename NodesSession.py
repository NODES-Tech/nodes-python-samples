__author__ = 'steinarruneeriksen'
from rauth import OAuth2Service
from enum import Enum
import json

class Environment(Enum):  #Old fashion Python 2.7 enum
    MockData=1
    DevTest=2
    ExtTest=3
    Production=4

base_urls={
    Environment.MockData:"https://api-test-mock.nodesmarket.com",
    Environment.DevTest:"https://api-test.nodesmarket.com",
    Environment.ExtTest:"https://api-extern-test.nodesmarket.com",
    Environment.Production:"https://api.nodesmarket.com"
}

access_token_urls={
    Environment.MockData:"https://login.microsoftonline.com/nodestechdev.onmicrosoft.com/oauth2/v2.0/token/",
    Environment.DevTest:"https://login.microsoftonline.com/nodestechdev.onmicrosoft.com/oauth2/v2.0/token/",
    Environment.ExtTest:"https://login.microsoftonline.com/nodestechprd.onmicrosoft.com/oauth2/v2.0/token/",
    Environment.Production:"https://login.microsoftonline.com/nodestechprd.onmicrosoft.com/oauth2/v2.0/token/"

}

scopes={
    Environment.MockData:"https://nodestechdev.onmicrosoft.com/devNodesApi/.default",
    Environment.DevTest:"https://nodestechdev.onmicrosoft.com/devNodesApi/.default",
    Environment.ExtTest:"https://nodestechprd.onmicrosoft.com/apinodesmarket/.default",
    Environment.Production:"https://nodestechprd.onmicrosoft.com/apinodesmarket/.default"
}

class NodesSession:

    def __init__(self, envir_id, client_id, client_secret):
        print "Authenticaitng against " + access_token_urls[envir_id]
        self.envir_id=envir_id
        self.service = OAuth2Service(client_id=client_id,
                        client_secret=client_secret,
                        access_token_url=access_token_urls[envir_id])
        try:
            self.session=self.service.get_auth_session(data={'grant_type': 'client_credentials',"scope": scopes[envir_id]}, decoder=json.loads)
            print "Authentication OK"
        except:
            print "Could not authenticate " + client_id

    def getHeader(self):
        return {'Authorization': 'Bearer','Accept': 'application/json'}
    def getPostHeader(self):
        return {'Authorization': 'Bearer','DataServiceVersion':'3.0','Content-Type':'application/json'}
    def getBaseUrl(self):
        return base_urls[self.envir_id]

    def getHandle(self):
        return self.session
