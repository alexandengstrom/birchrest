import sys
import os
import argparse
from typing import Any
import shutil
from colorama import Fore, Style, init
import subprocess
import platform

from .app import BirchRest

init(autoreset=True)

def init_project(args: Any) -> None:
    """
    Initializes a new project. If a directory name is provided, it creates that directory
    and moves into it. Otherwise, it initializes the project in the current directory.
    """
    cur_dir = os.getcwd()
    init_dir = cur_dir

    # Prompt user for directory name
    print(f"{Fore.GREEN}{Style.BRIGHT}BirchRest Project Initialization{Style.RESET_ALL}")
    dir_name = input(f"{Fore.YELLOW}Choose a name for the directory (leave blank to init in current directory):{Style.RESET_ALL}\n")

    if len(dir_name) > 0:
        init_dir = os.path.join(cur_dir, dir_name)
        if not os.path.exists(init_dir):
            os.mkdir(init_dir)
            print(f"{Fore.GREEN}Directory '{dir_name}' created.")
        else:
            print(f"{Fore.YELLOW}Directory '{dir_name}' already exists.")
    else:
        print(f"{Fore.GREEN}Initializing project in the current directory.")
    
    os.chdir(init_dir)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    boilerplate_dir = os.path.join(script_dir, '__boilerplate__')

    if not os.path.exists(boilerplate_dir):
        print(f"{Fore.RED}Boilerplate directory '__boilerplate__' not found in {script_dir}.")
        return

    try:
        for item in os.listdir(boilerplate_dir):
            src_path = os.path.join(boilerplate_dir, item)
            dest_path = os.path.join(init_dir, item)
            if os.path.isdir(src_path):
                shutil.copytree(src_path, dest_path, dirs_exist_ok=True)
            else:
                shutil.copy2(src_path, dest_path)
    except Exception as e:
        print(f"{Fore.RED}Error copying boilerplate contents: {e}")
        return

    create_venv = input(f"{Fore.YELLOW}Would you like to create a virtual environment? (y/n): {Style.RESET_ALL}").strip().lower()

    if create_venv == 'y':
        python_exec = 'python3' if platform.system() != 'Windows' else 'python'
        venv_path = os.path.join(init_dir, 'venv')

        print(f"{Fore.YELLOW}Creating virtual environment...{Style.RESET_ALL}")
        subprocess.run([python_exec, '-m', 'venv', 'venv'], shell=True, check=True)

        activate_script = ''
        if platform.system() == 'Windows':
            activate_script = os.path.join(venv_path, 'Scripts', 'activate.bat')
        else:
            activate_script = os.path.join(venv_path, 'bin', 'activate')

        print(f"{Fore.CYAN}Activating virtual environment and installing pylint and mypy...{Style.RESET_ALL}")
        
        try:
            if platform.system() == 'Windows':
                subprocess.run([activate_script, '&&', 'pip', 'install', 'pylint', 'mypy'], shell=True, check=True)
            else:
                subprocess.run(f'source {activate_script} && pip install pylint mypy', executable='/bin/bash', shell=True, check=True)
            print(f"{Fore.GREEN}pylint and mypy installed successfully inside the virtual environment.")
        except subprocess.CalledProcessError as e:
            print(f"{Fore.RED}Error occurred during installation: {e}")
            return
    else:
        print(f"{Fore.YELLOW}Virtual environment creation skipped.{Style.RESET_ALL}")

    enable_mypy = input(f"{Fore.YELLOW}Would you like to enable type checking with mypy? (y/n): {Style.RESET_ALL}").strip().lower()
    if enable_mypy == 'y':
        print(f"{Fore.GREEN}Type checking with mypy will be enabled.")
    else:
        print(f"{Fore.YELLOW}Type checking with mypy skipped.{Style.RESET_ALL}")

    enable_pylint = input(f"{Fore.YELLOW}Would you like to enable linting with pylint? (y/n): {Style.RESET_ALL}").strip().lower()
    if enable_pylint == 'y':
        print(f"{Fore.GREEN}Linting with pylint will be enabled.")
    else:
        print(f"{Fore.YELLOW}Linting with pylint skipped.{Style.RESET_ALL}")

    print(f"{Fore.GREEN}{Style.BRIGHT}Project initialization complete!{Style.RESET_ALL}")


def serve_project(port: int, host: str, log_level: str) -> None:
    """
    CLI version of starting the server
    """
    sys.path.insert(0, os.getcwd())
    app = BirchRest(log_level=log_level)
    app.serve(host=host, port=port)
    
def run_tests(args: Any) -> None:
    """ Runs the unit tests using Python's unittest framework. """
    print("Running unit tests...")
    try:
        subprocess.run(
            ["python", "-m", "unittest", "discover"],
            check=True,
            stdout=sys.stdout,
            stderr=sys.stderr,
            shell=True,
        )
    except subprocess.CalledProcessError as e:
        print("Typecheck failed!")


def run_typecheck(args: Any) -> None:
    """ Runs type checking with mypy. """
    print("Running type checks with mypy...")
    try:
        subprocess.run(
            ["mypy", "."],
            check=True,
            stdout=sys.stdout,
            stderr=sys.stderr,
            shell=True,
        )
    except subprocess.CalledProcessError as e:
        print("Typecheck failed!")


def run_lint(args: Any) -> None:
    """ Runs linting with pylint, excluding specified directories. """
    print("Running lint checks with pylint...")

    # Add directories to ignore such as venv, __pycache__, etc.
    exclude_dirs = ["venv", "__pycache__", ".venv", "node_modules"]

    # Create the ignore argument for pylint
    ignore_argument = ",".join(exclude_dirs)

    try:
        subprocess.run(
            ["pylint", ".", f"--ignore={ignore_argument}"],
            check=True,
            stdout=sys.stdout,
            stderr=sys.stderr,
            shell=True,
        )
    except subprocess.CalledProcessError as e:
        print("Typecheck failed!")

def main() -> None:
    """
    Entry point for the CLI.
    """
    parser = argparse.ArgumentParser(prog="birch", description="BirchRest CLI")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    init_parser = subparsers.add_parser("init", help="Initialize a new BirchREST project")
    init_parser.set_defaults(func=init_project)

    serve_parser = subparsers.add_parser("serve", help="Serve the BirchREST project")

    serve_parser.add_argument(
        "--port",
        type=int,
        default=13337,
        help="Port to start the server on (default: 13337)"
    )
    serve_parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host to bind the server to (default: 127.0.0.1)"
    )
    serve_parser.add_argument(
        "--log-level",
        type=str,
        default="info",
        choices=["debug", "info", "warning", "error", "critical"],
        help="Log level for the server (default: info)"
    )
    
    serve_parser.set_defaults(func=lambda args: serve_project(args.port, args.host, args.log_level))

    test_parser = subparsers.add_parser("test", help="Run unit tests")
    test_parser.set_defaults(func=run_tests)

    typecheck_parser = subparsers.add_parser("typecheck", help="Run mypy for type checking")
    typecheck_parser.set_defaults(func=run_typecheck)

    lint_parser = subparsers.add_parser("lint", help="Run pylint for lint checking")
    lint_parser.set_defaults(func=run_lint)
    args = parser.parse_args()

    if args.command:
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
