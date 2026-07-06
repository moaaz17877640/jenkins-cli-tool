import os
import json
import requests
from urllib.parse import urljoin
from dotenv import load_dotenv
# INFO: loading environment variables from .env file
load_dotenv()

CONFIG_FILE = os.path.expanduser("~/.jenkins_cli_config.json")

class JenkinsClient:
    def __init__(self):
        self.session = requests.Session()
        self.url = None
        self.load_config()
    #INFO : load vars from env file or from the config file
    def load_config(self):
        # Try environment variables first
        self.url = os.environ.get("JENKINS_URL")
        username = os.environ.get("JENKINS_USER")
        token = os.environ.get("JENKINS_TOKEN")
        
        if self.url and username and token:
            self.session.auth = (username, token)
            return

        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    self.url = config.get("url")
                    username = config.get("username")
                    token = config.get("token")
                    if username and token:
                        self.session.auth = (username, token)
            except Exception as e:
                print(f"Error loading config: {e}")
    #INFO : statful login so we dont have to login every time , it saves the credentials to ~/.jenkins_cli_config.json
    def save_config(self, url, username, token):
        self.url = url.rstrip('/')
        self.session.auth = (username, token)
        
        # Test connection
        try:
            self._get_json("api/json")
        except Exception as e:
            print(f"Failed to authenticate with Jenkins: {e}")
            return False

        config = {
            "url": self.url,
            "username": username,
            "token": token
        }
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f)
        print("Successfully authenticated and saved session.")
        return True
    # INFO: _get_api_url method is used to get the API URL for a specific path
    def _get_api_url(self, path):
        if not path:
            return "api/json"
        
        parts = path.strip('/').split('/')
        jenkins_path = "/job/".join(parts)
        return f"job/{jenkins_path}/api/json"
    # INFO: _get_json method is used to get JSON data from a specific Jenkins endpoint
    def _get_json(self, endpoint):
        if not self.url:
            raise ValueError("Jenkins URL not configured. Please run 'login' first.")
            
        url = urljoin(self.url + "/", endpoint)
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()
    
    # INFO: _post method is used to post data to a specific Jenkins endpoint
    def _post(self, endpoint, data=None):
        if not self.url:
            raise ValueError("Jenkins URL not configured. Please run 'login' first.")
            
        # INFO: Get crumb if CSRF is enabled
        crumb_url = urljoin(self.url + "/", "crumbIssuer/api/json")
        try:
            crumb_resp = self.session.get(crumb_url)
            if crumb_resp.status_code == 200:
                crumb_data = crumb_resp.json()
                self.session.headers.update({crumb_data['crumbRequestField']: crumb_data['crumb']})
        except Exception:
            pass # CSRF might be disabled or not accessible

        url = urljoin(self.url + "/", endpoint)
        response = self.session.post(url, data=data)
        response.raise_for_status()
        return response
    # INFO: list_jobs method is used to list jobs in a specific folder
    def list_jobs(self, path=""):
        try:
            endpoint = self._get_api_url(path)
            data = self._get_json(endpoint)
                
            jobs = data.get('jobs', [])
            if not jobs:
                print("No jobs found.")
            for job in jobs:
                print(f"- {job['name']} (Color: {job.get('color', 'Folder')})")
        except Exception as e:
            print(f"Error listing jobs: {e}")
    # INFO: get_status method is used to get the status of a specific Jenkins job
    def get_status(self, path):
        try:
            endpoint = self._get_api_url(path)
            data = self._get_json(endpoint)
            
            print(f"Job: {data.get('fullDisplayName', path)}")
            print(f"Buildable: {data.get('buildable', 'N/A')}")
            
            last_build = data.get('lastBuild')
            if last_build:
                # Fetch last build details
                build_endpoint = endpoint.replace("api/json", f"{last_build['number']}/api/json")
                build_data = self._get_json(build_endpoint)
                print(f"Last Build: #{build_data['number']} - {build_data.get('result', 'RUNNING')}")
                print(f"URL: {build_data['url']}")
            else:
                print("No builds found.")
        except Exception as e:
            print(f"Error getting status: {e}")
    
    # INFO: trigger_build method is used to trigger a Jenkins job
    def trigger_build(self, path, params=None):
        try:
            parts = path.strip('/').split('/')
            jenkins_path = "/job/".join(parts)
            
            if params:
                endpoint = f"job/{jenkins_path}/buildWithParameters"
                self._post(endpoint, data=params)
                print(f"Triggered parameterized build for '{path}' with params: {params}")
            else:
                endpoint = f"job/{jenkins_path}/build"
                self._post(endpoint)
                print(f"Triggered build for '{path}'")
        except Exception as e:
            print(f"Error triggering build: {e}")
