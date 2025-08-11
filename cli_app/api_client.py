"""Generic API client for making HTTP requests."""

import json
import logging
from typing import Any, Dict, Optional, Union
from urllib.parse import urljoin

import requests
from pydantic import BaseModel, HttpUrl

logger = logging.getLogger(__name__)


class APIError(Exception):
    """Custom exception for API-related errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response: Optional[requests.Response] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class APIClient(BaseModel):
    """Generic API client for making HTTP requests.
    
    This class provides a foundation for interacting with REST APIs.
    It handles authentication, common HTTP methods, and error handling.
    """
    
    base_url: HttpUrl
    token: str
    timeout: int = 30
    verify_ssl: bool = True
    session: Optional[requests.Session] = None
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, base_url: str, token: str, **kwargs):
        super().__init__(base_url=base_url, token=token, **kwargs)
        self._setup_session()
    
    def _setup_session(self) -> None:
        """Set up the requests session with default headers and authentication."""
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "User-Agent": "Python-CLI-App/0.1.0",
        })
        self.session.verify = self.verify_ssl
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> requests.Response:
        """Make an HTTP request to the API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint: API endpoint path
            data: Request body data
            params: Query parameters
            headers: Additional headers
            **kwargs: Additional arguments to pass to requests
            
        Returns:
            requests.Response: The HTTP response
            
        Raises:
            APIError: If the request fails or returns an error status
        """
        url = urljoin(str(self.base_url), endpoint)
        
        # Merge headers
        request_headers = self.session.headers.copy()
        if headers:
            request_headers.update(headers)
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                headers=request_headers,
                timeout=self.timeout,
                **kwargs
            )
            
            # Log request details
            logger.debug(f"{method} {url} - Status: {response.status_code}")
            
            # Handle error responses
            if not response.ok:
                error_msg = f"API request failed: {response.status_code} {response.reason}"
                try:
                    error_data = response.json()
                    if "message" in error_data:
                        error_msg = error_data["message"]
                    elif "error" in error_data:
                        error_msg = error_data["error"]
                except (ValueError, KeyError):
                    pass
                
                raise APIError(error_msg, response.status_code, response)
            
            return response
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise APIError(f"Request failed: {e}")
    
    def get_resource(self, resource: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get a resource from the API.
        
        Args:
            resource: Resource identifier or path
            params: Query parameters
            
        Returns:
            Dict containing the resource data
        """
        response = self._make_request("GET", resource, params=params)
        return response.json()
    
    def create_resource(self, resource: str, data: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Create a new resource via the API.
        
        Args:
            resource: Resource path
            data: Resource data (can be string or dict)
            
        Returns:
            Dict containing the created resource data
        """
        # Convert string data to dict if needed
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                raise APIError("Invalid JSON data provided")
        
        response = self._make_request("POST", resource, data=data)
        return response.json()
    
    def update_resource(self, resource: str, data: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Update an existing resource via the API.
        
        Args:
            resource: Resource identifier or path
            data: Updated resource data
            
        Returns:
            Dict containing the updated resource data
        """
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                raise APIError("Invalid JSON data provided")
        
        response = self._make_request("PUT", resource, data=data)
        return response.json()
    
    def delete_resource(self, resource: str) -> bool:
        """Delete a resource via the API.
        
        Args:
            resource: Resource identifier or path
            
        Returns:
            True if deletion was successful
        """
        response = self._make_request("DELETE", resource)
        return response.status_code in [200, 204]
    
    def list_resources(self, resource: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """List resources from the API.
        
        Args:
            resource: Resource path (usually plural, e.g., 'users', 'posts')
            params: Query parameters for filtering/pagination
            
        Returns:
            Dict containing the list of resources
        """
        response = self._make_request("GET", resource, params=params)
        return response.json()
    
    def health_check(self) -> bool:
        """Check if the API is healthy/accessible.
        
        Returns:
            True if the API is accessible
        """
        try:
            response = self._make_request("GET", "health", timeout=10)
            return response.status_code == 200
        except APIError:
            return False
    
    def close(self) -> None:
        """Close the session and clean up resources."""
        if self.session:
            self.session.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close() 