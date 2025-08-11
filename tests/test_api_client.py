"""Tests for the API client module."""

import json
from unittest.mock import Mock, patch, MagicMock

import pytest
import requests

from cli_app.api_client import APIClient, APIError


class TestAPIClient:
    """Test cases for the APIClient class."""
    
    def test_init(self):
        """Test APIClient initialization."""
        client = APIClient("https://api.example.com", "test-token")
        
        assert str(client.base_url) == "https://api.example.com"
        assert client.token == "test-token"
        assert client.timeout == 30
        assert client.verify_ssl is True
        assert client.session is not None
    
    def test_init_with_kwargs(self):
        """Test APIClient initialization with additional parameters."""
        client = APIClient(
            "https://api.example.com",
            "test-token",
            timeout=60,
            verify_ssl=False
        )
        
        assert client.timeout == 60
        assert client.verify_ssl is False
    
    def test_setup_session(self):
        """Test session setup with correct headers."""
        client = APIClient("https://api.example.com", "test-token")
        
        assert client.session.headers["Authorization"] == "Bearer test-token"
        assert client.session.headers["Content-Type"] == "application/json"
        assert client.session.headers["User-Agent"] == "Python-CLI-App/0.1.0"
        assert client.session.verify is True
    
    def test_setup_session_no_ssl_verify(self):
        """Test session setup without SSL verification."""
        client = APIClient("https://api.example.com", "test-token", verify_ssl=False)
        assert client.session.verify is False
    
    @patch('cli_app.api_client.requests.Session')
    def test_make_request_success(self, mock_session_class, mock_api_response):
        """Test successful request."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        mock_session.headers = {}
        
        client = APIClient("https://api.example.com", "test-token")
        client.session = mock_session
        
        mock_session.request.return_value = mock_api_response
        
        response = client._make_request("GET", "test-endpoint")
        
        assert response == mock_api_response
        mock_session.request.assert_called_once()
        
        # Verify request parameters
        call_args = mock_session.request.call_args
        assert call_args[1]["method"] == "GET"
        assert call_args[1]["url"] == "https://api.example.com/test-endpoint"
        assert call_args[1]["timeout"] == 30
    
    @patch('cli_app.api_client.requests.Session')
    def test_make_request_with_data_and_params(self, mock_session_class, mock_api_response):
        """Test request with data and parameters."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        mock_session.headers = {}
        
        client = APIClient("https://api.example.com", "test-token")
        client.session = mock_session
        
        mock_session.request.return_value = mock_api_response
        
        data = {"key": "value"}
        params = {"page": 1}
        headers = {"Custom-Header": "custom-value"}
        
        response = client._make_request(
            "POST",
            "test-endpoint",
            data=data,
            params=params,
            headers=headers
        )
        
        assert response == mock_api_response
        
        # Verify request parameters
        call_args = mock_session.request.call_args
        assert call_args[1]["json"] == data
        assert call_args[1]["params"] == params
        assert call_args[1]["headers"]["Custom-Header"] == "custom-value"
    
    @patch('cli_app.api_client.requests.Session')
    def test_make_request_error_response(self, mock_session_class, mock_api_error_response):
        """Test request with error response."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        mock_session.headers = {}
        
        client = APIClient("https://api.example.com", "test-token")
        client.session = mock_session
        
        mock_session.request.return_value = mock_api_error_response
        
        with pytest.raises(APIError, match="Bad Request"):
            client._make_request("GET", "test-endpoint")
    
    @patch('cli_app.api_client.requests.Session')
    def test_make_request_network_error(self, mock_session_class):
        """Test request with network error."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        mock_session.headers = {}
        
        client = APIClient("https://api.example.com", "test-token")
        client.session = mock_session
        
        mock_session.request.side_effect = requests.exceptions.ConnectionError("Connection failed")
        
        with pytest.raises(APIError, match="Request failed: Connection failed"):
            client._make_request("GET", "test-endpoint")
    
    def test_get_resource(self, api_client, mock_api_response):
        """Test getting a resource."""
        with patch.object(api_client, '_make_request', return_value=mock_api_response):
            result = api_client.get_resource("users/1")
            
            assert result == {"id": 1, "name": "test", "status": "active"}
            api_client._make_request.assert_called_once_with("GET", "users/1", params=None)
    
    def test_get_resource_with_params(self, api_client, mock_api_response):
        """Test getting a resource with parameters."""
        with patch.object(api_client, '_make_request', return_value=mock_api_response):
            params = {"include": "profile", "fields": "id,name"}
            result = api_client.get_resource("users", params=params)
            
            assert result == {"id": 1, "name": "test", "status": "active"}
            api_client._make_request.assert_called_once_with("GET", "users", params=params)
    
    def test_create_resource_dict(self, api_client, mock_api_response):
        """Test creating a resource with dictionary data."""
        with patch.object(api_client, '_make_request', return_value=mock_api_response):
            data = {"name": "John Doe", "email": "john@example.com"}
            result = api_client.create_resource("users", data)
            
            assert result == {"id": 1, "name": "test", "status": "active"}
            api_client._make_request.assert_called_once_with("POST", "users", data=data)
    
    def test_create_resource_json_string(self, api_client, mock_api_response):
        """Test creating a resource with JSON string data."""
        with patch.object(api_client, '_make_request', return_value=mock_api_response):
            data = '{"name": "John Doe", "email": "john@example.com"}'
            result = api_client.create_resource("users", data)
            
            assert result == {"id": 1, "name": "test", "status": "active"}
            api_client._make_request.assert_called_once_with(
                "POST", "users", 
                data={"name": "John Doe", "email": "john@example.com"}
            )
    
    def test_create_resource_invalid_json(self, api_client):
        """Test creating a resource with invalid JSON string."""
        with pytest.raises(APIError, match="Invalid JSON data provided"):
            api_client.create_resource("users", "invalid json {")
    
    def test_update_resource(self, api_client, mock_api_response):
        """Test updating a resource."""
        with patch.object(api_client, '_make_request', return_value=mock_api_response):
            data = {"name": "Jane Doe"}
            result = api_client.update_resource("users/1", data)
            
            assert result == {"id": 1, "name": "test", "status": "active"}
            api_client._make_request.assert_called_once_with("PUT", "users/1", data=data)
    
    def test_delete_resource_success(self, api_client):
        """Test successful resource deletion."""
        mock_response = Mock()
        mock_response.status_code = 204
        
        with patch.object(api_client, '_make_request', return_value=mock_response):
            result = api_client.delete_resource("users/1")
            assert result is True
    
    def test_delete_resource_success_200(self, api_client):
        """Test successful resource deletion with 200 status."""
        mock_response = Mock()
        mock_response.status_code = 200
        
        with patch.object(api_client, '_make_request', return_value=mock_response):
            result = api_client.delete_resource("users/1")
            assert result is True
    
    def test_delete_resource_failure(self, api_client):
        """Test failed resource deletion."""
        mock_response = Mock()
        mock_response.status_code = 404
        
        with patch.object(api_client, '_make_request', return_value=mock_response):
            result = api_client.delete_resource("users/999")
            assert result is False
    
    def test_list_resources(self, api_client, mock_api_response):
        """Test listing resources."""
        with patch.object(api_client, '_make_request', return_value=mock_api_response):
            result = api_client.list_resources("users")
            
            assert result == {"id": 1, "name": "test", "status": "active"}
            api_client._make_request.assert_called_once_with("GET", "users", params=None)
    
    def test_list_resources_with_params(self, api_client, mock_api_response):
        """Test listing resources with parameters."""
        with patch.object(api_client, '_make_request', return_value=mock_api_response):
            params = {"page": 2, "limit": 20}
            result = api_client.list_resources("users", params=params)
            
            assert result == {"id": 1, "name": "test", "status": "active"}
            api_client._make_request.assert_called_once_with("GET", "users", params=params)
    
    def test_health_check_success(self, api_client):
        """Test successful health check."""
        mock_response = Mock()
        mock_response.status_code = 200
        
        with patch.object(api_client, '_make_request', return_value=mock_response):
            result = api_client.health_check()
            assert result is True
    
    def test_health_check_failure(self, api_client):
        """Test failed health check."""
        with patch.object(api_client, '_make_request', side_effect=APIError("Health check failed")):
            result = api_client.health_check()
            assert result is False
    
    def test_health_check_timeout(self, api_client):
        """Test health check with custom timeout."""
        mock_response = Mock()
        mock_response.status_code = 200
        
        with patch.object(api_client, '_make_request', return_value=mock_api_response) as mock_request:
            result = api_client.health_check()
            
            # Verify timeout was passed
            call_args = mock_request.call_args
            assert call_args[1]["timeout"] == 10
    
    def test_close(self, api_client):
        """Test closing the client session."""
        mock_session = Mock()
        api_client.session = mock_session
        
        api_client.close()
        mock_session.close.assert_called_once()
    
    def test_context_manager(self):
        """Test APIClient as context manager."""
        with APIClient("https://api.example.com", "test-token") as client:
            assert client.session is not None
        
        # Session should be closed after context exit
        assert client.session.closed


class TestAPIError:
    """Test cases for the APIError exception."""
    
    def test_api_error_basic(self):
        """Test basic APIError creation."""
        error = APIError("Test error message")
        assert str(error) == "Test error message"
        assert error.status_code is None
        assert error.response is None
    
    def test_api_error_with_status_code(self):
        """Test APIError with status code."""
        error = APIError("Test error message", status_code=404)
        assert error.status_code == 404
    
    def test_api_error_with_response(self):
        """Test APIError with response object."""
        mock_response = Mock()
        error = APIError("Test error message", response=mock_response)
        assert error.response == mock_response
    
    def test_api_error_with_all_parameters(self):
        """Test APIError with all parameters."""
        mock_response = Mock()
        error = APIError("Test error message", status_code=500, response=mock_response)
        assert str(error) == "Test error message"
        assert error.status_code == 500
        assert error.response == mock_response 