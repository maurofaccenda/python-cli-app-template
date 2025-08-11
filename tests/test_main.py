"""Tests for the main CLI module."""

from unittest.mock import Mock, patch, MagicMock
import click
import pytest

from cli_app.main import (
    main, configure, status, fetch, create, update, delete, health,
    validate_url, validate_json_data
)
from cli_app.config import Config


class TestParameterValidation:
    """Test cases for parameter validation functions."""
    
    def test_validate_url_valid_http(self):
        """Test URL validation with valid HTTP URL."""
        ctx = Mock()
        param = Mock()
        result = validate_url(ctx, param, "http://example.com")
        assert result == "http://example.com"
    
    def test_validate_url_valid_https(self):
        """Test URL validation with valid HTTPS URL."""
        ctx = Mock()
        param = Mock()
        result = validate_url(ctx, param, "https://api.example.com")
        assert result == "https://api.example.com"
    
    def test_validate_url_invalid(self):
        """Test URL validation with invalid URL."""
        ctx = Mock()
        param = Mock()
        with pytest.raises(click.BadParameter, match="URL must start with http:// or https://"):
            validate_url(ctx, param, "ftp://example.com")
    
    def test_validate_url_none(self):
        """Test URL validation with None value."""
        ctx = Mock()
        param = Mock()
        result = validate_url(ctx, param, None)
        assert result is None
    
    def test_validate_json_data_valid(self):
        """Test JSON data validation with valid JSON."""
        ctx = Mock()
        param = Mock()
        result = validate_json_data(ctx, param, '{"name": "test"}')
        assert result == '{"name": "test"}'
    
    def test_validate_json_data_invalid(self):
        """Test JSON data validation with invalid JSON."""
        ctx = Mock()
        param = Mock()
        with pytest.raises(click.BadParameter, match="Data must be valid JSON"):
            validate_json_data(ctx, param, '{"name": "test"')
    
    def test_validate_json_data_none(self):
        """Test JSON data validation with None value."""
        ctx = Mock()
        param = Mock()
        result = validate_json_data(ctx, param, None)
        assert result is None


class TestMainCLI:
    """Test cases for the main CLI commands."""
    
    def test_main_command_group(self):
        """Test that main creates a click command group."""
        assert isinstance(main, click.Group)
        assert main.name == "main"
    
    def test_main_help_text(self):
        """Test main command help text."""
        assert "Python CLI Application Template" in main.help
    
    def test_main_version_option(self):
        """Test that main has a version option."""
        # Check if version option exists in the command
        version_option = None
        for param in main.params:
            if hasattr(param, 'name') and param.name == 'version':
                version_option = param
                break
        
        assert version_option is not None
    
    def test_main_context_setup(self, mock_click_context):
        """Test main command context setup."""
        ctx = mock_click_context
        ctx.ensure_object = Mock()
        ctx.invoked_subcommand = "status"  # Simulate subcommand
        
        # Mock the config loading
        with patch('cli_app.main.Config') as mock_config_class:
            mock_config = Mock()
            mock_config_class.return_value = mock_config
            
            main.callback(ctx, None, False, None, None, 30, False)
            
            ctx.ensure_object.assert_called_once()
            assert ctx.obj["verbose"] is False
    
    def test_main_with_config_file(self, mock_click_context, sample_config_file):
        """Test main command with config file."""
        ctx = mock_click_context
        ctx.ensure_object = Mock()
        ctx.invoked_subcommand = "status"
        
        with patch('cli_app.main.Config') as mock_config_class:
            mock_config = Mock()
            mock_config_class.from_file.return_value = mock_config
            
            main.callback(ctx, sample_config_file, False, None, None, 30, False)
            
            mock_config_class.from_file.assert_called_once_with(sample_config_file)
    
    def test_main_with_command_line_overrides(self, mock_click_context):
        """Test main command with command line parameter overrides."""
        ctx = mock_click_context
        ctx.ensure_object = Mock()
        ctx.invoked_subcommand = "status"
        
        with patch('cli_app.main.Config') as mock_config_class:
            mock_config = Mock()
            mock_config_class.return_value = mock_config
            
            main.callback(ctx, None, True, "https://new.example.com", "new-token", 60, True)
            
            # Verify overrides were applied
            mock_config.api_endpoint = "https://new.example.com"
            mock_config.api_token = "new-token"
            mock_config.timeout = 60
            mock_config.verify_ssl = False
    
    def test_main_no_subcommand_shows_status(self, mock_click_context):
        """Test main command shows status when no subcommand given."""
        ctx = mock_click_context
        ctx.ensure_object = Mock()
        ctx.invoked_subcommand = None
        
        with patch('cli_app.main.Config') as mock_config_class:
            mock_config = Mock()
            mock_config_class.return_value = mock_config
            
            with patch('cli_app.main.status') as mock_status:
                main.callback(ctx, None, False, None, None, 30, False)
                
                mock_status.callback.assert_called_once_with(ctx)
    
    def test_main_config_error_handling(self, mock_click_context):
        """Test main command error handling for config loading."""
        ctx = mock_click_context
        ctx.ensure_object = Mock()
        ctx.exit = Mock()
        ctx.invoked_subcommand = "status"
        
        with patch('cli_app.main.Config') as mock_config_class:
            mock_config_class.side_effect = Exception("Config error")
            
            with patch('cli_app.main.console') as mock_console:
                main.callback(ctx, None, False, None, None, 30, False)
                
                mock_console.print.assert_called_once()
                assert "Error loading configuration" in mock_console.print.call_args[0][0]
                ctx.exit.assert_called_once_with(1)


class TestConfigureCommand:
    """Test cases for the configure command."""
    
    def test_configure_command_success(self, tmp_path):
        """Test successful configuration."""
        with patch('cli_app.main.Config') as mock_config_class:
            mock_config = Mock()
            mock_config_class.return_value = mock_config
            
            with patch('cli_app.main.console') as mock_console:
                configure.callback(None, "https://api.example.com", "test-token", 45, True, "DEBUG")
                
                mock_config.api_endpoint = "https://api.example.com"
                mock_config.api_token = "test-token"
                mock_config.timeout = 45
                mock_config.verify_ssl = False
                mock_config.log_level = "DEBUG"
                mock_config.save.assert_called_once()
                mock_console.print.assert_called_once_with("[green]Configuration saved successfully![/green]")
    
    def test_configure_command_with_verbose(self, tmp_path):
        """Test configure command with verbose output."""
        with patch('cli_app.main.Config') as mock_config_class:
            mock_config = Mock()
            mock_config_class.return_value = mock_config
            
            ctx = Mock()
            ctx.obj = {"verbose": True}
            
            with patch('cli_app.main.console') as mock_console:
                configure.callback(ctx, "https://api.example.com", "test-token", 30, False, "INFO")
                
                # Should show verbose output
                assert mock_console.print.call_count > 1
    
    def test_configure_command_error_handling(self):
        """Test configure command error handling."""
        with patch('cli_app.main.Config') as mock_config_class:
            mock_config = Mock()
            mock_config.save.side_effect = Exception("Save error")
            mock_config_class.return_value = mock_config
            
            with patch('cli_app.main.console') as mock_console:
                ctx = Mock()
                ctx.exit = Mock()
                
                configure.callback(ctx, "https://api.example.com", "test-token", 30, False, "INFO")
                
                mock_console.print.assert_called_once()
                assert "Error saving configuration" in mock_console.print.call_args[0][0]
                ctx.exit.assert_called_once_with(1)


class TestStatusCommand:
    """Test cases for the status command."""
    
    def test_status_command_display(self, mock_click_context):
        """Test status command displays configuration."""
        ctx = mock_click_context
        
        with patch('cli_app.main.console') as mock_console:
            status.callback(ctx)
            
            mock_console.print.assert_called()
            # Should create a table
            assert any("Application Status" in str(call) for call in mock_console.print.call_args_list)
    
    def test_status_command_not_configured(self):
        """Test status command when not configured."""
        ctx = Mock()
        ctx.obj = {
            "verbose": False,
            "config": Config()  # Empty config
        }
        
        with patch('cli_app.main.console') as mock_console:
            status.callback(ctx)
            
            mock_console.print.assert_called()
            # Should show warning
            assert any("⚠️" in str(call) for call in mock_console.print.call_args_list)


class TestFetchCommand:
    """Test cases for the fetch command."""
    
    def test_fetch_command_success(self, mock_click_context):
        """Test successful fetch command."""
        ctx = mock_click_context
        
        with patch('cli_app.main.APIClient') as mock_client_class:
            mock_client = Mock()
            mock_client.get_resource.return_value = {"id": 1, "name": "test"}
            mock_client_class.return_value = mock_client
            
            with patch('cli_app.main.console') as mock_console:
                fetch.callback(ctx, "users/1", None, None, "json")
                
                mock_client.get_resource.assert_called_once_with("users/1", None)
                mock_console.print.assert_called()
                assert "Successfully fetched users/1" in mock_console.print.call_args_list[0][0][0]
    
    def test_fetch_command_with_params(self, mock_click_context):
        """Test fetch command with query parameters."""
        ctx = mock_click_context
        
        with patch('cli_app.main.APIClient') as mock_client_class:
            mock_client = Mock()
            mock_client.get_resource.return_value = {"id": 1, "name": "test"}
            mock_client_class.return_value = mock_client
            
            with patch('cli_app.main.console') as mock_console:
                fetch.callback(ctx, "users", '{"page": 1}', None, "json")
                
                mock_client.get_resource.assert_called_once_with("users", {"page": 1})
    
    def test_fetch_command_with_output_file(self, mock_click_context, tmp_path):
        """Test fetch command with output file."""
        ctx = mock_click_context
        output_file = tmp_path / "output.json"
        
        with patch('cli_app.main.APIClient') as mock_client_class:
            mock_client = Mock()
            mock_client.get_resource.return_value = {"id": 1, "name": "test"}
            mock_client_class.return_value = mock_client
            
            with patch('cli_app.main.console') as mock_console:
                fetch.callback(ctx, "users/1", None, str(output_file), "json")
                
                assert output_file.exists()
                mock_console.print.assert_called()
                assert "Output saved to" in mock_console.print.call_args_list[-1][0][0]
    
    def test_fetch_command_table_format(self, mock_click_context):
        """Test fetch command with table format."""
        ctx = mock_click_context
        
        with patch('cli_app.main.APIClient') as mock_client_class:
            mock_client = Mock()
            mock_client.get_resource.return_value = [
                {"id": 1, "name": "John"},
                {"id": 2, "name": "Jane"}
            ]
            mock_client_class.return_value = mock_client
            
            with patch('cli_app.main.console') as mock_console:
                fetch.callback(ctx, "users", None, None, "table")
                
                # Should create a table
                mock_console.print.assert_called()
    
    def test_fetch_command_not_configured(self):
        """Test fetch command when not configured."""
        ctx = Mock()
        ctx.obj = {
            "config": Config()  # Empty config
        }
        ctx.exit = Mock()
        
        with patch('cli_app.main.console') as mock_console:
            fetch.callback(ctx, "users/1", None, None, "json")
            
            mock_console.print.assert_called_once()
            assert "API not configured" in mock_console.print.call_args[0][0]
            ctx.exit.assert_called_once_with(1)
    
    def test_fetch_command_api_error(self, mock_click_context):
        """Test fetch command with API error."""
        ctx = mock_click_context
        ctx.exit = Mock()
        
        with patch('cli_app.main.APIClient') as mock_client_class:
            mock_client = Mock()
            mock_client.get_resource.side_effect = Exception("API error")
            mock_client_class.return_value = mock_client
            
            with patch('cli_app.main.console') as mock_console:
                fetch.callback(ctx, "users/1", None, None, "json")
                
                mock_console.print.assert_called_once()
                assert "Error fetching data" in mock_console.print.call_args[0][0]
                ctx.exit.assert_called_once_with(1)


class TestCreateCommand:
    """Test cases for the create command."""
    
    def test_create_command_success(self, mock_click_context):
        """Test successful create command."""
        ctx = mock_click_context
        
        with patch('cli_app.main.APIClient') as mock_client_class:
            mock_client = Mock()
            mock_client.create_resource.return_value = {"id": 2, "name": "new user"}
            mock_client_class.return_value = mock_client
            
            with patch('cli_app.main.console') as mock_console:
                create.callback(ctx, "users", '{"name": "new user"}', None)
                
                mock_client.create_resource.assert_called_once_with("users", {"name": "new user"})
                mock_console.print.assert_called()
                assert "Successfully created users" in mock_console.print.call_args_list[0][0][0]
    
    def test_create_command_with_file(self, mock_click_context, tmp_path):
        """Test create command with file input."""
        ctx = mock_click_context
        data_file = tmp_path / "user_data.json"
        data_file.write_text('{"name": "John", "email": "john@example.com"}')
        
        with patch('cli_app.main.APIClient') as mock_client_class:
            mock_client = Mock()
            mock_client.create_resource.return_value = {"id": 1, "name": "John"}
            mock_client_class.return_value = mock_client
            
            with patch('cli_app.main.console') as mock_console:
                create.callback(ctx, "users", None, str(data_file))
                
                mock_client.create_resource.assert_called_once_with("users", {"name": "John", "email": "john@example.com"})
    
    def test_create_command_not_configured(self):
        """Test create command when not configured."""
        ctx = Mock()
        ctx.obj = {
            "config": Config()  # Empty config
        }
        ctx.exit = Mock()
        
        with patch('cli_app.main.console') as mock_console:
            create.callback(ctx, "users", '{"name": "test"}', None)
            
            mock_console.print.assert_called_once()
            assert "API not configured" in mock_console.print.call_args[0][0]
            ctx.exit.assert_called_once_with(1)
    
    def test_create_command_api_error(self, mock_click_context):
        """Test create command with API error."""
        ctx = mock_click_context
        ctx.exit = Mock()
        
        with patch('cli_app.main.APIClient') as mock_client_class:
            mock_client = Mock()
            mock_client.create_resource.side_effect = Exception("API error")
            mock_client_class.return_value = mock_client
            
            with patch('cli_app.main.console') as mock_console:
                create.callback(ctx, "users", '{"name": "test"}', None)
                
                mock_console.print.assert_called_once()
                assert "Error creating resource" in mock_console.print.call_args[0][0]
                ctx.exit.assert_called_once_with(1)


class TestUpdateCommand:
    """Test cases for the update command."""
    
    def test_update_command_success(self, mock_click_context):
        """Test successful update command."""
        ctx = mock_click_context
        
        with patch('cli_app.main.APIClient') as mock_client_class:
            mock_client = Mock()
            mock_client.update_resource.return_value = {"id": 1, "name": "updated"}
            mock_client_class.return_value = mock_client
            
            with patch('cli_app.main.console') as mock_console:
                update.callback(ctx, "users/1", '{"name": "updated"}')
                
                mock_client.update_resource.assert_called_once_with("users/1", {"name": "updated"})
                mock_console.print.assert_called()
                assert "Successfully updated users/1" in mock_console.print.call_args_list[0][0][0]


class TestDeleteCommand:
    """Test cases for the delete command."""
    
    def test_delete_command_success(self, mock_click_context):
        """Test successful delete command."""
        ctx = mock_click_context
        
        with patch('cli_app.main.APIClient') as mock_client_class:
            mock_client = Mock()
            mock_client.delete_resource.return_value = True
            mock_client_class.return_value = mock_client
            
            with patch('cli_app.main.console') as mock_console:
                with patch('click.confirm', return_value=True):
                    delete.callback(ctx, "users/1", False)
                    
                    mock_client.delete_resource.assert_called_once_with("users/1")
                    mock_console.print.assert_called()
                    assert "Successfully deleted users/1" in mock_console.print.call_args_list[0][0][0]
    
    def test_delete_command_force(self, mock_click_context):
        """Test delete command with force flag."""
        ctx = mock_click_context
        
        with patch('cli_app.main.APIClient') as mock_client_class:
            mock_client = Mock()
            mock_client.delete_resource.return_value = True
            mock_client_class.return_value = mock_client
            
            with patch('cli_app.main.console') as mock_console:
                delete.callback(ctx, "users/1", True)
                
                # Should not ask for confirmation
                mock_client.delete_resource.assert_called_once_with("users/1")


class TestHealthCommand:
    """Test cases for the health command."""
    
    def test_health_command_success(self, mock_click_context):
        """Test successful health check."""
        ctx = mock_click_context
        
        with patch('cli_app.main.APIClient') as mock_client_class:
            mock_client = Mock()
            mock_client.health_check.return_value = True
            mock_client_class.return_value = mock_client
            
            with patch('cli_app.main.console') as mock_console:
                health.callback(ctx)
                
                mock_console.print.assert_called_once()
                assert "✅ API is healthy" in mock_console.print.call_args[0][0]
    
    def test_health_command_unhealthy(self, mock_click_context):
        """Test health check when API is unhealthy."""
        ctx = mock_click_context
        
        with patch('cli_app.main.APIClient') as mock_client_class:
            mock_client = Mock()
            mock_client.health_check.return_value = False
            mock_client_class.return_value = mock_client
            
            with patch('cli_app.main.console') as mock_console:
                health.callback(ctx)
                
                mock_console.print.assert_called_once()
                assert "❌ API is unhealthy" in mock_console.print.call_args[0][0] 