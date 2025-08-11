#!/usr/bin/env python3
"""Development setup script for the Python CLI application."""

import os
import subprocess
import sys
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Command: {command}")
        print(f"   Error: {e.stderr}")
        return False


def check_uv_installed():
    """Check if uv is installed."""
    try:
        subprocess.run(["uv", "--version"], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def main():
    """Main setup function."""
    print("🚀 Python CLI Application - Development Setup")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 13):
        print(f"❌ Error: Python 3.13+ required, found {sys.version}")
        print("   Please upgrade to Python 3.13 or higher")
        sys.exit(1)
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} detected")
    
    # Check if we're in the right directory
    if not Path("pyproject.toml").exists():
        print("❌ Error: This script must be run from the project root directory")
        print("   (where pyproject.toml is located)")
        sys.exit(1)
    
    # Check if uv is installed
    if not check_uv_installed():
        print("❌ Error: uv is not installed")
        print("   Please install uv first:")
        print("   curl -LsSf https://astral.sh/uv/install.sh | sh")
        print("   or visit: https://github.com/astral-sh/uv")
        sys.exit(1)
    
    print("✅ uv is installed")
    print()
    
    # Install dependencies
    if not run_command("uv sync", "Installing dependencies"):
        sys.exit(1)
    
    # Install development dependencies
    if not run_command("uv sync --group dev", "Installing development dependencies"):
        sys.exit(1)
    
    # Install the application in development mode
    if not run_command("uv pip install -e .", "Installing CLI app in development mode"):
        sys.exit(1)
    
    # Install pre-commit hooks
    if not run_command("uv run pre-commit install", "Installing pre-commit hooks"):
        print("⚠️  Warning: Pre-commit hooks installation failed, but continuing...")
    
    # Run initial formatting
    print("🔄 Running initial code formatting...")
    if run_command("uv run ruff format .", "Formatting code with Ruff"):
        print("✅ Code formatting completed")
    
    # Run tests to verify setup
    print("🔄 Running tests to verify setup...")
    if run_command("uv run pytest --version", "Checking pytest installation"):
        if run_command("uv run pytest tests/ -v", "Running test suite"):
            print("✅ All tests passed!")
        else:
            print("⚠️  Warning: Some tests failed, but setup is complete")
    
    print()
    print("🎉 Development setup completed successfully!")
    print()
    print("📋 Next steps:")
    print("   1. Configure your API credentials:")
    print("      cli-app configure --endpoint <url> --token <token>")
    print()
    print("   2. Check the application status:")
    print("      cli-app status")
    print()
    print("   3. Try the example commands:")
    print("      cli-app --help")
    print("      cli-app fetch --resource users")
    print()
    print("   4. Run tests during development:")
    print("      uv run pytest")
    print()
    print("   5. Format code before committing:")
    print("      uv run ruff format .")
    print()
    print("💡 Useful commands:")
    print("   - make help          # Show available make targets")
    print("   - make test          # Run tests")
    print("   - make format        # Format code")
    print("   - make lint          # Run linting")
    print("   - make check-all     # Run all quality checks")


if __name__ == "__main__":
    main() 