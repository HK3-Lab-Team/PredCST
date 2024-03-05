import subprocess
from typing import Optional, List
import os

def create_pyenv(package_name: str, version: Optional[str] = None) -> str:
    """
    Creates a new pyenv environment, installs a specified package (and optionally a version),
    and returns the directory path of the new environment.
    """
    env_name = f"{package_name}_version_{version}_env" if version else f"{package_name}_env"

    # Create a new Python environment
    subprocess.run(["pyenv", "virtualenv", "3.12.1", env_name], check=True)

    # Get the path to the environment
    env_path = subprocess.check_output(["pyenv", "prefix", env_name]).decode().strip()

    # Build the path to the pip executable within the new environment
    pip_path = f"{env_path}/bin/pip"

    # Install the package (and optionally, the version)
    package_to_install = f"{package_name}=={version}" if version else package_name
    subprocess.run([pip_path, "install", package_to_install], check=True)

    return env_path, env_name


def list_pip_versions(package_name: str) -> List[str]:
    """
    Lists all available pip versions for a given pip package.
    
    Args:
    package_name (str): The name of the pip package to list versions for.
    
    Returns:
    List[str]: A list of strings, each representing a version of the package.
    """
    # Use pip to list all available versions of the package
    result = subprocess.run(["pip", "index", "versions", package_name], capture_output=True, text=True)
    
    # Check if the command was successful
    if result.returncode != 0:
        raise Exception(f"Failed to list versions for package '{package_name}'. Error: {result.stderr}")
    
    # Process the output to extract version numbers
    versions = []
    for line in result.stdout.splitlines():
        if "Available versions:" in line:
            versions = line.split(":")[1].strip().split(", ")
            break
    
    return versions

def list_pyenv_environments():
    pyenv_versions_path = os.path.expanduser("~/.pyenv/versions")
    envs = []
    try:
        environments = os.listdir(pyenv_versions_path)
        for env in environments:
            if env not in [".DS_Store", "3.12.1"]:
                envs.append(env)
    except FileNotFoundError:
        print("Pyenv versions directory not found. Is pyenv installed?")
    return envs