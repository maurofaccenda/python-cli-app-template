# Python CLI Application Template

A professional Python CLI application template with best practices, built using modern Python tooling and designed for extensibility.

## Features

- 🚀 **Modern Python CLI** - Built with Click and Rich for beautiful command-line interfaces
- 🔧 **Generic API Client** - Flexible HTTP client for REST API interactions
- ⚙️ **Configuration Management** - Pydantic-based config with environment variable support
- 🎯 **Enhanced Click Parameters** - Advanced parameter validation, types, and environment variable integration
- 🧪 **Comprehensive Testing** - Full test suite with pytest and mocking
- 📦 **UV Integration** - Fast dependency management with uv
- 🎨 **Code Quality** - Pre-configured with Ruff, mypy, and pre-commit hooks
- 📊 **Coverage Reports** - Built-in test coverage reporting

## Quick Start

### Prerequisites

- Python 3.13 or higher
- [uv](https://github.com/astral-sh/uv) package manager

### Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd python-cli-app-template
   ```

2. **Install dependencies:**
   ```bash
   uv sync
   ```

3. **Install the application in development mode:**
   ```bash
   uv pip install -e .
   ```

### Basic Usage

1. **Configure the application:**
   ```bash
   cli-app configure --endpoint https://api.example.com --token your-api-token
   ```

2. **Check status:**
   ```bash
   cli-app status
   ```

3. **Fetch data from API:**
   ```bash
   cli-app fetch --resource users/1
   cli-app fetch --resource users --params '{"page": 1, "limit": 10}' --format table
   ```

4. **Create a new resource:**
   ```bash
   cli-app create --resource users --data '{"name": "John Doe", "email": "john@example.com"}'
   cli-app create --resource posts --file post_data.json
   ```

5. **Update a resource:**
   ```bash
   cli-app update --resource users/1 --data '{"name": "Jane Doe"}'
   ```

6. **Delete a resource:**
   ```bash
   cli-app delete --resource users/1
   cli-app delete --resource users/1 --force
   ```

7. **Check API health:**
   ```bash
   cli-app health
   ```

## Project Structure

```
python-cli-app-template/
├── cli_app/                 # Main application package
│   ├── __init__.py         # Package initialization
│   ├── main.py             # CLI entry point and commands
│   ├── api_client.py       # Generic API client class
│   └── config.py           # Configuration management
├── tests/                   # Test suite
│   ├── __init__.py         # Test package initialization
│   ├── conftest.py         # Pytest configuration and fixtures
│   ├── test_config.py      # Configuration module tests
│   └── test_api_client.py  # API client tests
├── pyproject.toml          # Project configuration and dependencies
├── README.md               # This file
├── .gitignore             # Git ignore patterns
├── .pre-commit-config.yaml # Pre-commit hooks configuration
└── Makefile               # Development tasks
```

## Development

### Setting up the development environment

1. **Install development dependencies:**
   ```bash
   uv sync --group dev
   ```

2. **Install pre-commit hooks:**
   ```bash
   pre-commit install
   ```

### Running tests

```bash
# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=cli_app --cov-report=html

# Run specific test file
uv run pytest tests/test_config.py

# Run tests with verbose output
uv run pytest -v
```

### Code formatting and linting

```bash
# Format and lint code with Ruff
uv run ruff check cli_app/ tests/
uv run ruff format cli_app/ tests/

# Type checking with mypy
uv run mypy cli_app/
```

### Pre-commit hooks

The project includes pre-commit hooks that automatically run code quality checks:

- Ruff linting and formatting
- mypy type checking

These run automatically on every commit, ensuring code quality.

## Enhanced Click Parameters

The CLI application uses advanced Click parameter features for a professional user experience:

### **Parameter Types & Validation**
- **URL Validation** - Automatic validation of API endpoints
- **JSON Validation** - Built-in JSON data validation
- **File Paths** - Support for reading data from files
- **Choice Parameters** - Predefined options for format, log levels, etc.

### **Environment Variable Integration**
All parameters can be set via environment variables:
```bash
export CLI_APP_API_ENDPOINT="https://api.example.com"
export CLI_APP_API_TOKEN="your-token"
export CLI_APP_VERBOSE="true"
export CLI_APP_TIMEOUT="60"
export CLI_APP_NO_VERIFY_SSL="true"
```

### **Parameter Overrides**
Command line options override environment variables and configuration files:
```bash
cli-app --endpoint https://custom.api.com --timeout 120 --verbose
```

### **Interactive Features**
- **Confirmation Prompts** - Safe deletion with user confirmation
- **Hidden Input** - Secure token input with confirmation
- **Rich Output** - Beautiful tables and formatted display

## API Client Usage

The `APIClient` class provides a flexible foundation for interacting with REST APIs:

```python
from cli_app.api_client import APIClient

# Initialize client
client = APIClient("https://api.example.com", "your-token")

# Make requests
users = client.list_resources("users")
user = client.get_resource("users/1")
new_user = client.create_resource("users", {"name": "Jane Doe"})
updated_user = client.update_resource("users/1", {"name": "Jane Smith"})
success = client.delete_resource("users/1")

# Health check
is_healthy = client.health_check()

# Context manager usage
with APIClient("https://api.example.com", "your-token") as client:
    data = client.get_resource("health")
```

## Configuration

The application supports multiple configuration sources:

### Environment Variables

```bash
export CLI_APP_API_ENDPOINT="https://api.example.com"
export CLI_APP_API_TOKEN="your-token"
export CLI_APP_TIMEOUT="60"
export CLI_APP_LOG_LEVEL="DEBUG"
```

### Configuration File

Create a TOML configuration file:

```toml
# ~/.config/cli-app/config.toml
api_endpoint = "https://api.example.com"
api_token = "your-api-token"
timeout = 60
verify_ssl = true
log_level = "INFO"
```

### Command Line

```bash
cli-app --config /path/to/config.toml --verbose
```

## Adding New Commands

To add new CLI commands, extend the `main.py` file:

```python
@main.command()
@click.option("--name", required=True, help="Resource name")
@click.pass_context
def new_command(ctx: click.Context, name: str) -> None:
    """Description of your new command."""
    config = ctx.obj["config"]
    
    # Your command logic here
    console.print(f"Executing command with name: {name}")
```

## Testing

The project includes a comprehensive test suite:

- **Unit tests** for all modules
- **Mock fixtures** for external dependencies
- **Configuration testing** with temporary files
- **API client testing** with mocked HTTP responses

### Test Organization

- `tests/conftest.py` - Common fixtures and test configuration
- `tests/test_config.py` - Configuration management tests
- `tests/test_api_client.py` - API client functionality tests

### Running Specific Tests

```bash
# Run tests with specific markers
uv run pytest -m "unit"

# Run tests matching a pattern
uv run pytest -k "config"

# Run tests with specific output
uv run pytest --tb=short
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Run tests: `uv run pytest`
5. Format code: `uv run ruff format .`
6. Commit your changes: `git commit -m 'Add amazing feature'`
7. Push to the branch: `git push origin feature/amazing-feature`
8. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Click](https://click.palletsprojects.com/) - Python package for creating command line interfaces
- [Rich](https://rich.readthedocs.io/) - Rich text and beautiful formatting in the terminal
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Data validation using Python type annotations
- [pytest](https://docs.pytest.org/) - Testing framework
- [uv](https://github.com/astral-sh/uv) - Fast Python package installer and resolver 