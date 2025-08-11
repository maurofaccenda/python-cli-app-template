"""Main CLI application entry point."""

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from cli_app.config import Config
from cli_app.api_client import APIClient

console = Console()


def validate_url(ctx, param, value):
    """Validate URL parameter."""
    if value and not value.startswith(('http://', 'https://')):
        raise click.BadParameter('URL must start with http:// or https://')
    return value


def validate_json_data(ctx, param, value):
    """Validate JSON data parameter."""
    if value:
        try:
            import json
            json.loads(value)
        except json.JSONDecodeError:
            raise click.BadParameter('Data must be valid JSON')
    return value


@click.group(invoke_without_command=True)
@click.version_option(version="0.1.0", prog_name="cli-app")
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, dir_okay=False, path_type=str),
    envvar="CLI_APP_CONFIG",
    help="Path to configuration file",
    show_envvar=True,
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    default=False,
    envvar="CLI_APP_VERBOSE",
    help="Enable verbose output",
    show_envvar=True,
)
@click.option(
    "--endpoint",
    "-e",
    type=str,
    envvar="CLI_APP_API_ENDPOINT",
    help="API endpoint URL",
    callback=validate_url,
    show_envvar=True,
)
@click.option(
    "--token",
    "-t",
    type=str,
    envvar="CLI_APP_API_TOKEN",
    help="API authentication token",
    show_envvar=True,
)
@click.option(
    "--timeout",
    type=int,
    default=30,
    envvar="CLI_APP_TIMEOUT",
    help="Request timeout in seconds",
    show_envvar=True,
)
@click.option(
    "--no-verify-ssl",
    is_flag=True,
    default=False,
    envvar="CLI_APP_NO_VERIFY_SSL",
    help="Disable SSL verification",
    show_envvar=True,
)
@click.pass_context
def main(
    ctx: click.Context,
    config: str,
    verbose: bool,
    endpoint: str,
    token: str,
    timeout: int,
    no_verify_ssl: bool,
) -> None:
    """Python CLI Application Template.
    
    A professional CLI application template with best practices.
    
    Examples:
        cli-app --help                    # Show this help message
        cli-app status                    # Show application status
        cli-app configure -e URL -t TOKEN # Configure API credentials
        cli-app fetch -r users/1          # Fetch a resource
        cli-app create -r users -d '{"name":"John"}' # Create resource
    """
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    
    # Load configuration
    try:
        if config:
            ctx.obj["config"] = Config.from_file(config)
        else:
            ctx.obj["config"] = Config()
            
        # Override config with command line options
        if endpoint:
            ctx.obj["config"].api_endpoint = endpoint
        if token:
            ctx.obj["config"].api_token = token
        if timeout != 30:
            ctx.obj["config"].timeout = timeout
        if no_verify_ssl:
            ctx.obj["config"].verify_ssl = False
            
    except Exception as e:
        console.print(f"[red]Error loading configuration: {e}[/red]")
        ctx.exit(1)
    
    # If no subcommand is given, show status
    if ctx.invoked_subcommand is None:
        status.callback(ctx)


@main.command()
@click.option(
    "--endpoint",
    "-e",
    type=str,
    required=True,
    help="API endpoint URL",
    callback=validate_url,
)
@click.option(
    "--token",
    "-t",
    type=str,
    required=True,
    help="API authentication token",
    hide_input=True,
    confirmation_prompt=True,
)
@click.option(
    "--timeout",
    type=int,
    default=30,
    help="Request timeout in seconds",
)
@click.option(
    "--no-verify-ssl",
    is_flag=True,
    default=False,
    help="Disable SSL verification",
)
@click.option(
    "--log-level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]),
    default="INFO",
    help="Logging level",
)
@click.pass_context
def configure(
    ctx: click.Context,
    endpoint: str,
    token: str,
    timeout: int,
    no_verify_ssl: bool,
    log_level: str,
) -> None:
    """Configure the application with API credentials.
    
    This command will save the configuration to the default location.
    You can also set these values via environment variables.
    """
    try:
        config = Config()
        config.api_endpoint = endpoint
        config.api_token = token
        config.timeout = timeout
        config.verify_ssl = not no_verify_ssl
        config.log_level = log_level
        
        config.save()
        
        console.print("[green]Configuration saved successfully![/green]")
        
        if ctx.obj.get("verbose"):
            console.print(f"  Endpoint: {endpoint}")
            console.print(f"  Token: {'*' * 8}")
            console.print(f"  Timeout: {timeout}s")
            console.print(f"  SSL Verify: {not no_verify_ssl}")
            console.print(f"  Log Level: {log_level}")
            
    except Exception as e:
        console.print(f"[red]Error saving configuration: {e}[/red]")
        ctx.exit(1)


@main.command()
@click.pass_context
def status(ctx: click.Context) -> None:
    """Show application status and configuration."""
    config = ctx.obj["config"]
    
    # Create a rich table for better display
    table = Table(title="Application Status", show_header=True, header_style="bold magenta")
    table.add_column("Setting", style="cyan", no_wrap=True)
    table.add_column("Value", style="green")
    
    table.add_row("API Endpoint", config.api_endpoint or "Not configured")
    table.add_row("API Token", "Configured" if config.api_token else "Not configured")
    table.add_row("Timeout", f"{config.timeout}s")
    table.add_row("SSL Verification", "Enabled" if config.verify_ssl else "Disabled")
    table.add_row("Log Level", config.log_level)
    table.add_row("Verbose Mode", "Yes" if ctx.obj.get("verbose") else "No")
    
    console.print(table)
    
    if not config.is_configured():
        console.print("\n[yellow]⚠️  API not configured. Use 'configure' command first.[/yellow]")


@main.command()
@click.option(
    "--resource",
    "-r",
    type=str,
    required=True,
    help="Resource to fetch (e.g., users, users/1, posts)",
)
@click.option(
    "--params",
    "-p",
    type=str,
    help="Query parameters as JSON (e.g., '{\"page\": 1, \"limit\": 10}')",
    callback=validate_json_data,
)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=str),
    help="Output file path (default: stdout)",
)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["json", "table", "yaml"]),
    default="json",
    help="Output format",
)
@click.pass_context
def fetch(
    ctx: click.Context,
    resource: str,
    params: str,
    output: str,
    format: str,
) -> None:
    """Fetch data from the API.
    
    Examples:
        cli-app fetch -r users              # Fetch all users
        cli-app fetch -r users/1            # Fetch specific user
        cli-app fetch -r posts -p '{"page": 2}'  # Fetch with params
    """
    config = ctx.obj["config"]
    
    if not config.is_configured():
        console.print("[red]API not configured. Use 'configure' command first.[/red]")
        ctx.exit(1)
    
    try:
        # Parse parameters if provided
        import json
        query_params = json.loads(params) if params else None
        
        api_client = APIClient(config.api_endpoint, config.api_token)
        data = api_client.get_resource(resource, query_params)
        
        console.print(f"[green]Successfully fetched {resource}[/green]")
        
        # Format and display output
        if format == "json":
            if output:
                with open(output, 'w') as f:
                    json.dump(data, f, indent=2)
                console.print(f"[blue]Output saved to {output}[/blue]")
            else:
                console.print(json.dumps(data, indent=2))
        elif format == "table" and isinstance(data, list):
            # Create a table for list data
            if data and isinstance(data[0], dict):
                table = Table(title=f"Resource: {resource}")
                for key in data[0].keys():
                    table.add_column(key, style="cyan")
                
                for item in data:
                    table.add_row(*[str(v) for v in item.values()])
                console.print(table)
            else:
                console.print(data)
        else:
            console.print(data)
            
    except Exception as e:
        console.print(f"[red]Error fetching data: {e}[/red]")
        if ctx.obj.get("verbose"):
            console.print_exception()
        ctx.exit(1)


@main.command()
@click.option(
    "--resource",
    "-r",
    type=str,
    required=True,
    help="Resource path (e.g., users, posts)",
)
@click.option(
    "--data",
    "-d",
    type=str,
    required=True,
    help="Resource data as JSON (e.g., '{\"name\": \"John\", \"email\": \"john@example.com\"}')",
    callback=validate_json_data,
)
@click.option(
    "--file",
    "-f",
    type=click.Path(exists=True, dir_okay=False, path_type=str),
    help="Read data from file instead of --data option",
)
@click.pass_context
def create(
    ctx: click.Context,
    resource: str,
    data: str,
    file: str,
) -> None:
    """Create a new resource via the API.
    
    Examples:
        cli-app create -r users -d '{"name":"John","email":"john@example.com"}'
        cli-app create -r posts -f post_data.json
    """
    config = ctx.obj["config"]
    
    if not config.is_configured():
        console.print("[red]API not configured. Use 'configure' command first.[/red]")
        ctx.exit(1)
    
    try:
        # Use file data if provided, otherwise use --data
        if file:
            with open(file, 'r') as f:
                data = f.read()
        
        api_client = APIClient(config.api_endpoint, config.api_token)
        result = api_client.create_resource(resource, data)
        
        console.print(f"[green]Successfully created {resource}[/green]")
        console.print(result)
        
    except Exception as e:
        console.print(f"[red]Error creating resource: {e}[/red]")
        if ctx.obj.get("verbose"):
            console.print_exception()
        ctx.exit(1)


@main.command()
@click.option(
    "--resource",
    "-r",
    type=str,
    required=True,
    help="Resource to update (e.g., users/1)",
)
@click.option(
    "--data",
    "-d",
    type=str,
    required=True,
    help="Update data as JSON",
    callback=validate_json_data,
)
@click.pass_context
def update(ctx: click.Context, resource: str, data: str) -> None:
    """Update an existing resource via the API."""
    config = ctx.obj["config"]
    
    if not config.is_configured():
        console.print("[red]API not configured. Use 'configure' command first.[/red]")
        ctx.exit(1)
    
    try:
        api_client = APIClient(config.api_endpoint, config.api_token)
        result = api_client.update_resource(resource, data)
        
        console.print(f"[green]Successfully updated {resource}[/green]")
        console.print(result)
        
    except Exception as e:
        console.print(f"[red]Error updating resource: {e}[/red]")
        if ctx.obj.get("verbose"):
            console.print_exception()
        ctx.exit(1)


@main.command()
@click.option(
    "--resource",
    "-r",
    type=str,
    required=True,
    help="Resource to delete (e.g., users/1)",
)
@click.option(
    "--force",
    "-f",
    is_flag=True,
    help="Force deletion without confirmation",
)
@click.pass_context
def delete(ctx: click.Context, resource: str, force: bool) -> None:
    """Delete a resource via the API."""
    config = ctx.obj["config"]
    
    if not config.is_configured():
        console.print("[red]API not configured. Use 'configure' command first.[/red]")
        ctx.exit(1)
    
    if not force:
        if not click.confirm(f"Are you sure you want to delete {resource}?"):
            console.print("[yellow]Deletion cancelled[/yellow]")
            return
    
    try:
        api_client = APIClient(config.api_endpoint, config.api_token)
        success = api_client.delete_resource(resource)
        
        if success:
            console.print(f"[green]Successfully deleted {resource}[/green]")
        else:
            console.print(f"[yellow]Resource {resource} was not found or could not be deleted[/yellow]")
        
    except Exception as e:
        console.print(f"[red]Error deleting resource: {e}[/red]")
        if ctx.obj.get("verbose"):
            console.print_exception()
        ctx.exit(1)


@main.command()
@click.pass_context
def health(ctx: click.Context) -> None:
    """Check API health status."""
    config = ctx.obj["config"]
    
    if not config.is_configured():
        console.print("[red]API not configured. Use 'configure' command first.[/red]")
        ctx.exit(1)
    
    try:
        api_client = APIClient(config.api_endpoint, config.api_token)
        is_healthy = api_client.health_check()
        
        if is_healthy:
            console.print("[green]✅ API is healthy[/green]")
        else:
            console.print("[red]❌ API is unhealthy[/red]")
            
    except Exception as e:
        console.print(f"[red]Error checking API health: {e}[/red]")
        if ctx.obj.get("verbose"):
            console.print_exception()
        ctx.exit(1)


if __name__ == "__main__":
    main() 