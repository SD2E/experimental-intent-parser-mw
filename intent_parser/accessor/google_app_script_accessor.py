from googleapiclient.discovery import build
import intent_parser.utils.intent_parser_utils as intent_parser_utils
import intent_parser.utils.script_addon_utils as script_addon_utils
import datetime

class GoogleAppScriptAccessor:
    """ 
    A list of APIs to access a Google Add-on Script Project.
    Refer to https://developers.google.com/apps-script/api/reference/rest to get information on how this class is set up.
    """
 
    def __init__(self, creds):
        self._service = build('script', 'v1', credentials=creds)
    
    def get_project_metadata(self, script_id, version_number=None):
        """
        Get metadata of a script project. 
        This metadata will include the appscript Code and manifest file.
        
        Args:
            script_id: id of the script project
            version_number: An integer value to get the script project base off of a version number. Default to None if no version is provided.
        
        Return:
            A Content object representing the metadata in the json format.
        """
        if version_number is None:
            return self._service.projects().getContent(
                scriptId=script_id).execute()
                
        return self._service.projects().getContent(
            scriptId=script_id,
            versionNumber=version_number).execute() 
    
    def get_project_versions(self, script_id):
        """
        Get a list of versions generated for the project
        
        Returns:
            A list of integers. An empty list is returned if no version exist on the project
        """
        response = self._service.projects().versions().list(
            scriptId=script_id).execute()
        if not response:
            return []
        list_of_versions = self._get_versions(script_id, response, [])
        return list_of_versions
    
    def _get_versions(self, script_id, response, list_of_versions):
        if 'nextPageToken' not in response:
            list_of_versions.extend(self._get_version_number(response['versions']))
            return list_of_versions
        
        next_page_token = response['nextPageToken']
        response = self._service.projects().versions().list(
            scriptId=script_id,
            pageToken=next_page_token).execute()
        list_of_versions.extend(self._get_version_number(response['versions']))
        self._get_versions(response, list_of_versions)
        
    def _get_version_number(self, version_list):
        version_numbers = []
        for index in range(len(version_list)):
            version_dict = version_list[index]
            version_numbers.append(version_dict['versionNumber'])
        return version_numbers
    
    def get_head_version(self, script_id):
        """
        Get the latest project version.
        Args:
            script_id: id of the app script.
            
        Returns:
            An integer value for representing the latest version for the app script.
        """
        list_of_versions = self.get_project_versions(script_id)
        if not list_of_versions:
            return 0
        
        return max(list_of_versions)
    
    def _get_manifest_file_index(self, file_list):
        for index in range(len(file_list)):
            file = file_list[index]
            file_type = file['type']
            file_name = file['name']
            
            if file_type == 'JSON' and file_name == 'appsscript':
                return index
        
        return None
    
    def _get_code_file_index(self, file_list):
        for index in range(len(file_list)):
            file = file_list[index]
            file_type = file['type']
            file_name = file['name']
            
            if file_type == 'SERVER_JS' and file_name == 'Code':
                return index
        
        return None
    
    def update_project_metadata(self, script_id, remote_content, local_code_path, local_manifest_path):
        """
        Update a script project's remote metadata with local metadata. 
        
        Args:
            script_id: id associated to a script project.
            remote_content: A Content object
            
        Returns:
            If request is successful, a Content object is returned in the form of json
        """
        file_list = remote_content['files']
      
        code_index = self._get_code_file_index(file_list)
        
        file_list[code_index]['source'] = str(intent_parser_utils.load_file(local_code_path)).strip()
        
        manifest_index = self._get_manifest_file_index(file_list)
        file_list[manifest_index] = intent_parser_utils.load_json_file(local_manifest_path)
        request = {'files' : file_list}
        
        content_obj = self._service.projects().updateContent(
            body=request,
            scriptId=script_id).execute()
        return content_obj
   
    def set_project_metadata(self, script_id, project_metadata, user_obj, local_code_path, local_manifest_path, code_file_name):
        """
        Set project's remote metadata with local metadata. 
        This includes updating manifest file and adding to project metadata a SERVER_JS file for the server code.
         
        Args:
            script_id: id associated to a script project.
         
        Returns:
            If request is successful, a Content object representing the metadata is returned in the json format.
        """
        
        file_list = project_metadata['files']
        manifest_index = self._get_manifest_file_index(file_list)
        file_list[manifest_index] = intent_parser_utils.load_json_file(local_manifest_path)
        
        source = str(intent_parser_utils.load_file(local_code_path)).strip()
        code_functions = script_addon_utils.get_function_names_from_js_file(local_code_path) 
        
        d = datetime.datetime.utcnow()
        created_time = d.isoformat("T") + "Z"
        
        code_file = {
            "name": code_file_name,
            "type": 'SERVER_JS',
            "source": source,
            "lastModifyUser": user_obj,
            "createTime": created_time,
            "updateTime": created_time,
            "functionSet": code_functions
        }
        
        file_list.append(code_file)
        request = {'files' : file_list}
        
        content_obj = self._service.projects().updateContent(
            body=request,
            scriptId=script_id).execute()
        return content_obj
            
    def create_project(self, project_title, doc_id):
        """
        Create a new Add-on script project bounded to a document.
        
        Args: 
            doc_id: id of Google Doc the script project will create from
            project_title: name of the script project
        
        Return:
            If request is successful, a project object is returned in a json format. 
        """
        request = {
            'title': project_title,
            'parentId': doc_id
        }
        project_obj = self._service.projects().create(
            body=request).execute()
        return project_obj
            
        
    def create_version(self, script_id, number, description):
        """
        Create a new version assigned to the script project. 
        
        Args:
            script_id: the script id of the project
            number: the version number
            description: A description for created version. 
        
        Returns:
            If request is successful, a version object is returned in the json format
        """
        d = datetime.datetime.utcnow()
        created_time = d.isoformat("T") + "Z"
        
        request = {
            'versionNumber': number,
            'description': description,
            'createTime': created_time
            }
        version_obj = self._service.projects().versions().create(
            scriptId=script_id,
            body=request).execute()
        
        return version_obj
    
    def get_deployment(self, script_id, deployment_id):
        """
        Get deployment from a script project.
        Args:
            script_id: id assigned to the script
            deployment_id: id assigned to the deployment
        Returns:
            If request is successful, a deployment object is returned in json format
        """
        deployment_obj = self._service.projects().deployments().get(
            scriptId=script_id,
            deploymentId=deployment_id).execute()
            
        return deployment_obj
    
    def create_deployment(self, script_id, deploy_version, description):
        request = {
            'versionNumber': deploy_version,
            'manifestFileName': 'appsscript',
            'description': description
        }
        return self._service.projects().deployments().create(
            scriptId=script_id,
            body=request).execute()
        
    def update_deployment(self, script_id, deploy_id, version_number, description):
        """
        Updates an existing deployment from an app script project. 
        Args:
            script_id: The script id that the project updates from.
            deploy_id: The deploy id assigned to the deployment object.
            version_number: The version of the deployment
            description: A description for updating the deployment. 
        
        Returns:
            If request is successful, a Deployment object is returned in the form json.
        """
        request = {
            'deploymentConfig': {
                'scriptId': script_id, 
                'versionNumber': version_number,
                'manifestFileName': 'appsscript',
                'description': description
            }
        }
        return self._service.projects().deployments().update(
            scriptId=script_id,
            deploymentId=deploy_id,
            body=request).execute()
        