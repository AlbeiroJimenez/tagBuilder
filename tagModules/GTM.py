from apiclient.discovery import build
from google_auth_oauthlib import flow
from oauth2client import client
from oauth2client import file
from oauth2client import tools
from google.cloud import bigquery

import httplib2

from os import path
import samples_util as g_util

GTM_      = ['https://www.googleapis.com/auth/tagmanager.edit.containers', 'tagmanager', 'v2']

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
        """Establish and set up a conection with Google Cloud Services

        Args:
            parameters_ (_type_): _description_

        Returns:
            Service Object: GTM, DV360, ADH or BigQuery Service object.
        """
        client_secrets_path = path.abspath(CREDENTIALS)
        flow_ = client.flow_from_clientsecrets(client_secrets_path, scope=parameters_[0],message=tools.message_if_missing(client_secrets_path))
        storage = file.Storage(parameters_[1] + '.dat')
        credentials = storage.get()
        if credentials is None or credentials.invalid:
            credentials = tools.run_flow(flow_, storage)
        http = credentials.authorize(http=httplib2.Http())
        return build(parameters_[1], parameters_[2], http=http)
    
    def gtmService(self):
        return self.getService(GTM_)
    
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
        """_summary_

        Returns:
            _type_: _description_
        """
        return self.getService(DV360)
    
    def adhService(self):
        pass

class GTM:
    def __init__(self):
        """Constructor Method of the GTM Class"""
        self.gtm_service = googleCloudServices().gtmService()
        self.accountList = self.getAccounts()
    
    def getAccounts(self):
        """This method retrieves all accounts that the user have in his GTM Account.

        Returns:
            List: A list of dictionaries that represents each account in the GTM's account.
        """
        accounts = self.gtm_service.accounts().list().execute()
        return accounts['account']
     
    def getContainers(self, accountID):
        """This methods retrieves all containers associatives to a specific client account.

        Args:
            accountID (string): ID that identify the client account in GTM.

        Returns:
            List: All containers associatives to a an account in dictionary format.
        """
        accountID = 'accounts/'+accountID
        containers = self.gtm_service.accounts().containers().list(parent=accountID).execute()
        return containers['container']
    
    def getWorkSpaces(self, accountID, containerID):
        """This method retrieves all workspaces that owns to specify container.

        Args:
            accountID (string): ID that identifies the client account in GTM.
            containerID (string): ID that identifies a specific container. 

        Returns:
            List: List of all workspaces that owns to a specific container in dictionary format. 
        """
        containerID = 'accounts/'+accountID+'/containers/'+containerID
        workspaces  = self.gtm_service.accounts().containers().workspaces().list(parent=containerID).execute()
        return workspaces['workspace']
    
    def getTag(self):
        pass
    
    def getAllTags(self, accountID, containerID, workspaceID):
        """This method retrieve all tags that owns to a specific workspace in a container. 

        Args:
            accountID (string): ID that identifies the client account in GTM.
            containerID (string): ID that identifies a specific container.
            workspaceID (string): Workspace ID.

        Returns:
            List: Dictionary list with all tags in a specific worspace. 
        """
        workspaceID = 'accounts/%s/containers/%s/workspaces/%s'%(accountID, containerID, workspaceID)
        tags = self.gtm_service.accounts().containers().workspaces().tags().list(parent=workspaceID).execute()
        return tags['tag']
    
    def getTrigger(self):
        pass
    
    def getAllTriggers(self, accountID, containerID, workspaceID):
        """This method retrieve all triggers that owns to a specific workspace in a container.

        Args:
            accountID (string): ID that identifies the client account in GTM.
            containerID (string): ID that identifies a specific container.
            workspaceID (string): Workspace ID.

        Returns:
            list: Dictionary list with all triggers in a specific worspace.
        """
        workspaceID = 'accounts/%s/containers/%s/workspaces/%s'%(accountID, containerID, workspaceID)
        triggers = self.gtm_service.accounts().containers().workspaces().triggers().list(parent=workspaceID).execute()
        return triggers['trigger']
    
    def getVariable(self):
        pass
    
    def getAllVariables(self, accountID, containerID, workspaceID):
        """This method retrieve all variables that own to a specific workspace in a container.

        Args:
            accountID (string): ID that identifies the client account in GTM.
            containerID (string): ID that identifies a specific container.
            workspaceID (string): Workspace ID.

        Returns:
            list: Dictionary list with all variables in a specific worspace.
        """
        workspaceID = 'accounts/%s/containers/%s/workspaces/%s'%(accountID, containerID, workspaceID)
        variables = self.gtm_service.accounts().containers().workspaces().variables().list(parent=workspaceID).execute()
        return variables['variable']
    
    def getFolder(self):
        pass
    
    def getAllFolders(self, accountID, containerID, workspaceID):
        """This method retrieve all folders that own to a specific workspace in a container.

        Args:
            accountID (string): ID that identifies the client account in GTM.
            containerID (string): ID that identifies a specific container.
            workspaceID (string): Workspace ID.

        Returns:
            list: Dictionary list with all folders in a specific worspace.
        """
        workspaceID = 'accounts/%s/containers/%s/workspaces/%s'%(accountID, containerID, workspaceID)
        folders = self.gtm_service.accounts().containers().workspaces().folders().list(parent=workspaceID).execute()
        return folders['folder']
    
    def getTemplate(self):
        pass
    
    def getAllTemplates(self, accountID, containerID, workspaceID):
        """This method retrieve all templates that own to a specific workspace in a container.

        Args:
            accountID (string): ID that identifies the client account in GTM.
            containerID (string): ID that identifies a specific container.
            workspaceID (string): Workspace ID.

        Returns:
            list: Dictionary list with all templates in a specific worspace.
        """
        workspaceID = 'accounts/%s/containers/%s/workspaces/%s'%(accountID, containerID, workspaceID)
        templates = self.gtm_service.accounts().containers().workspaces().templates().list(parent=workspaceID).execute()
        return templates['template']
    
    def createAccount(self):
        pass
    
    def createContainer(self):
        pass
    
    def createTag(self):
        pass

if __name__ == '__main__':
    #g_util.get_credentials()
    gtm = GTM()
    gtm.createAccount()
    googleCloud = googleCloudServices()
    #gtm = googleCloud.gtmService()
