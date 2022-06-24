from apiclient.discovery import build
from google_auth_oauthlib import flow
from oauth2client import client
from oauth2client import file
from oauth2client import tools
from google.cloud import bigquery

import httplib2

from os import path
from datetime import date as dt
from tagModules.tagBuilderTools import Naming

#import samples_util as g_util

GTM_      = ['https://www.googleapis.com/auth/tagmanager.edit.containers', 'tagmanager', 'v2']

DV360    = ['https://www.googleapis.com/auth/display-video', 'displayvideo', 'v1']

BIGQUERY = ['https://www.googleapis.com/auth/bigquery', 'api-ops-xaxis']

CREDENTIALS = 'client_secrets.json' 

FOLDER_NAME = ''

namingTools = Naming()
class googleCloudServices:
    """This class generate the differents services and clients of the google services.
    GTM, DV360: Handle through service and google client library. 
    BIGQUERY: Handle through client and google cloud library. 
    ADH: TBD
    """
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
    
    def getAccount(self, name):
        for account in self.accountList:
            if account['name'] == name:
                return account
        else:
            return 404
     
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
    
    def getContainer(self, accountID, gtmID):
        for container in self.getContainers(accountID):
            if container['publicId'] == gtmID:
                return container
        else:
            return 404
    
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
    
    def getWorkSpace(self, accountID, containerID, name):
        for workspace in self.getWorkSpaces(accountID, containerID):
            if workspace['name'] == name:
                return workspace
        else:
            return 404
    
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
    
    def getFolder(self, path):
        """This method return a folder entity from a specific workspace.

        Args:
            path (string): GTM Folder's API relative path. Example: accounts/{account_id}/containers/{container_id}/workspaces/{workspace_id}/folders/{folder_id}

        Returns:
            folder: dictionary with all information about folder entity.
        """
        return self.gtm_service.accounts().containers().workspaces().folders().get(path=path).execute()
    
    def getAllFolders(self, parent):
        """This method lists all GTM Folders of a Container.

        Args:
            parent (string): GTM Workspace's API relative path. Example: accounts/{account_id}/containers/{container_id}/workspaces/{workspace_id}

        Returns:
            Folders: Dictionary list with all folders in a specific worspace.
        """
        folders = self.gtm_service.accounts().containers().workspaces().folders().list(parent=parent).execute()
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
    
    def createContainer(self):
        pass
    
    def createVariable(self, accountID, containerID, workspaceID, body):
        """This method implements a variable in GTM Platform

        Args:
            accountID (string): ID that identifies the client account in GTM.
            containerID (string): ID that identifies a specific container.
            workspaceID (string): Workspace ID.
            body (Variable Dictionary): A dictionary that contains the set-up information about the variable.

        Returns:
            Tag: The variable element that was created.
        """
        workspaceID = 'accounts/%s/containers/%s/workspaces/%s'%(accountID, containerID, workspaceID)
        return self.gtm_service.accounts().containers().workspaces().variables().create(parent=workspaceID,body=body).execute()
    
    def createTrigger(self, accountID, containerID, workspaceID, body):
        """This method implements a Trigger in GTM Platform

        Args:
            accountID (string): ID that identifies the client account in GTM.
            containerID (string): ID that identifies a specific container.
            workspaceID (string): Workspace ID.
            body (Trigger Dictionary): A dictionary that contains the set-up information about the trigger.

        Returns:
            Tag: The trigger element that was created.
        """
        workspaceID = 'accounts/%s/containers/%s/workspaces/%s'%(accountID, containerID, workspaceID)
        return self.gtm_service.accounts().containers().workspaces().triggers().create(parent=workspaceID,body=body).execute()
    
    def createTag(self, accountID, containerID, workspaceID, body):
        """This method implements a Tag in GTM Platform

        Args:
            accountID (string): ID that identifies the client account in GTM.
            containerID (string): ID that identifies a specific container.
            workspaceID (string): Workspace ID.
            body (Tag Dictionary): A dictionary that contains the set-up information about the tag. 

        Returns:
            Tag: The tag element that was created.
        """
        workspaceID = 'accounts/%s/containers/%s/workspaces/%s'%(accountID, containerID, workspaceID)
        return self.gtm_service.accounts().containers().workspaces().tags().create(parent=workspaceID,body=body).execute()
    
    def createTemple(self):
        pass
    
    def createFolder(self, parent, name=None, notes=None):
        """This method creates a GTM Folder.

        Args:
            parent (string): GTM Workspace's API relative path. Example: accounts/{account_id}/containers/{container_id}/workspaces/{workspace_id}
            name (string): Folder display name.
            notes (string, optional): User notes on how to apply this folder in the container.
            
            Returns:
            Folder: If successful, this method returns a Folders resource in the response body.
        """
        if name == None: name = namingTools.createFileName('GroupM', 'Strategy')
        body = {'name': name}
        if notes != None: body.update({'notes': notes})
        return self.gtm_service.accounts().containers().workspaces().folders().create(parent=parent, body=body).execute()
        
    def updateFolder(self, path, name=None, notes=None):
        """This methods update the name a specific folder. If the name don't 

        Args:
            path (string): GTM Folder's API relative path. Example: accounts/{account_id}/containers/{container_id}/workspaces/{workspace_id}/folders/{folder_id}
            name (string, optional): Folder display name. Defaults to None.
            notes (string, optional): User notes on how to apply this folder in the container.
            
            Returns:
            Folder: If successful, this method returns a Folders resource in the response body.
        """
        if name == None: name = namingTools.createFileName('GroupM', 'Strategy')
        body = {'name': name}
        if notes != None: body.update({'notes': notes})
        return self.gtm_service.accounts().containers().workspaces().folders().update(path=path, body=body)
    
    def existAccount(self, name):
        for account in self.accountList:
            if account['name'] == name:
                return True
        else:
            return False
    
    def existElement(self, parent, name, element='Tag'):
        if element == 'Tag':
            pass
        elif element == 'Trigger':
            pass
        elif element == 'Variable':
            pass
        elif element == 'Template':
            pass
        elif element == 'Folder':
            print('Entramos a existElement')
            folders =  self.getAllFolders(parent)
            print(folders)
            for folder in folders:
                if name in folder['name']:
                    return True, folder
            else:
                return False, {}
    
if __name__ == '__main__':
    gtm = GTM()