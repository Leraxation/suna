import os
import httpx
from   agentpress.tool import Tool, ToolResult
from   utils.logger import logger

class NetlifyDeployTool(Tool ):
    def __init__(self):
        super().__init__()
        self.netlify_access_token = os.getenv("NETLIFY_ACCESS_TOKEN")
        if not self.netlify_access_token:
            # This will raise an error if the token is not found, which is good for debugging
            raise ValueError("NETLIFY_ACCESS_TOKEN environment variable not set or empty.")
        self.base_url = "https://api.netlify.com/api/v1"
        self.headers = {
            "Authorization": f"Bearer {self.netlify_access_token}",
            "Content-Type": "application/json"
        }

    # @tool
    def deploy_website(self, site_id: str, build_hook_url: str ) -> ToolResult:
        """
        Deploys a website to Netlify by triggering a build hook.
        This tool is used to initiate a new deployment for an existing Netlify site.
        You must provide the Netlify Site ID and the Build Hook URL for the site.

        Args:
            site_id (str): The unique ID of the Netlify site to deploy.
                           You can find this in your Netlify site settings under "Site information".
            build_hook_url (str): The URL of the build hook for the Netlify site.
                                  You can find this in your Netlify site settings under "Build & deploy" -> "Build hooks".
        Returns:
            ToolResult: A success message if the deployment is triggered, or an error message.
        """
        logger.info(f"Attempting to deploy Netlify site {site_id} using build hook.")
        try:
            # Use httpx.post to trigger the build hook
            response = httpx.post(build_hook_url, headers=self.headers )
            response.raise_for_status() # Raise an exception for 4xx or 5xx responses

            if response.status_code == 200 or response.status_code == 204:
                return self.success_response(f"Deployment triggered successfully for site ID: {site_id}.")
            else:
                # This part might be redundant due to raise_for_status, but good for explicit handling
                return self.error_response(f"Failed to trigger deployment for site ID: {site_id}. Status: {response.status_code}, Response: {response.text}")
        except httpx.RequestError as e:
            # Catches network errors (e.g., DNS resolution failed, connection refused )
            return self.error_response(f"Network error during Netlify deployment: {e}")
        except httpx.HTTPStatusError as e:
            # Catches HTTP errors (e.g., 401 Unauthorized, 404 Not Found, 500 Server Error )
            return self.error_response(f"HTTP error during Netlify deployment: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            # Catches any other unexpected errors
            return self.error_response(f"An unexpected error occurred during Netlify deployment: {e}")

