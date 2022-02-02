from apiclient.discovery import build
from google_auth_oauthlib import flow
from oauth2client import client
from oauth2client import file
from oauth2client import tools
from google.cloud import bigquery

import httplib2

from os import path
import samples_util as g_util

GTM      = ['https://www.googleapis.com/auth/tagmanager.edit.containers', 'tagmanager', 'v2']

DV360    = ['https://www.googleapis.com/auth/display-video', 'displayvideo', 'v1']

BIGQUERY = ['https://www.googleapis.com/auth/bigquery', 'api-ops-xaxis']

CREDENTIALS = 'client_secrets.json' 

"""This class generate the differents services and clients of the google services.
    GTM, DV360: Handle through service and google client library. 
    BIGQUERY: Handle through client and google cloud library. 
    ADH: TBD
    Returns:
        None: None
"""
class googleCloudServices:
    def __init__(self):
        pass
    
    def getService(self, parameters_):
        client_secrets_path = path.abspath(CREDENTIALS)
        flow_ = client.flow_from_clientsecrets(client_secrets_path, scope=parameters_[0],message=tools.message_if_missing(client_secrets_path))
        storage = file.Storage(parameters_[1] + '.dat')
        credentials = storage.get()
        if credentials is None or credentials.invalid:
            credentials = tools.run_flow(flow_, storage)
        http = credentials.authorize(http=httplib2.Http())
        return build(parameters_[1], parameters_[2], http=http)
    
    def gtmService(self):
        return getService(GTM)
    
    def bigqueryService(self, parameters_, launch_browser=True):
        client_secrets_path = path.abspath(CREDENTIALS)
        appflow = flow.InstalledAppFlow.from_client_secrets_file(client_secrets_path, scopes=BIGQUERY[0])
        if launch_browser:
            appflow.run_local_server()
        else:
            appflow.run_console()
        credentials = appflow.credentials
        return bigquery.Client(project=BIGQUERY[1], credentials=credentials) # Return a Client

    def dv360Service(self):
        return getService(DV360)
    
    def adhService(self):
        pass

class containerGTM:
    def __init__(self):
        pass  

if __name__ == '__main__':
    g_util.get_credentials()
    print("Todo Ok")