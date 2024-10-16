import sys
import os
import argparse
import shutil
import subprocess
import platform
import json

from colorama import Fore, Style, init
from typing import Any

from .app import BirchRest

init(autoreset=True)


def should_print() -> bool:
    return os.getenv("birchrest_log_level") != "test"


def init_project(_args: Any) -> None:
    """
    Initializes a new project. If a directory name is provided, it creates that directory
    and moves into it. Otherwise, it initializes the project in the current directory.
    """
    cur_dir = os.getcwd()
    init_dir = cur_dir
    if should_print():
        print(
            f"{Fore.GREEN}{Style.BRIGHT}BirchRest Project Initialization{Style.RESET_ALL}"
        )
    dir_name = input(
        f"{Fore.YELLOW}Choose a name for the directory (leave blank to init in current directory):{Style.RESET_ALL}\n"
    )

    if len(dir_name) > 0:
        init_dir = os.path.join(cur_dir, dir_name)
        if not os.path.exists(init_dir):
            os.mkdir(init_dir)
            if should_print():
                print(f"{Fore.GREEN}Directory '{dir_name}' created.")
        else:
            if should_print():
                print(f"{Fore.YELLOW}Directory '{dir_name}' already exists.")
    else:
        if should_print():
            print(f"{Fore.GREEN}Initializing project in the current directory.")

    os.chdir(init_dir)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    boilerplate_dir = os.path.join(script_dir, "__boilerplate__")

    if not os.path.exists(boilerplate_dir):
        if should_print():
            print(
                f"{Fore.RED}Boilerplate directory '__boilerplate__' not found in {script_dir}."
            )
        return

    try:
        for item in os.listdir(boilerplate_dir):
            src_path = os.path.join(boilerplate_dir, item)
            dest_path = os.path.join(init_dir, item)

            if os.path.isdir(src_path):
                shutil.copytree(src_path, dest_path, dirs_exist_ok=True)
            else:
                shutil.copy2(src_path, dest_path)

        if should_print():
            print(
                f"{Fore.GREEN}Boilerplate contents copied to {init_dir} successfully."
            )
    except Exception as e:
        if should_print():
            print(f"{Fore.RED}Error copying boilerplate contents: {e}")
        return

    create_venv = (
        input(
            f"{Fore.YELLOW}Would you like to create a virtual environment? (y/n): {Style.RESET_ALL}"
        )
        .strip()
        .lower()
    )

    if create_venv == "y":
        python_exec = "python3" if platform.system() != "Windows" else "python"
        venv_path = os.path.join(init_dir, "venv")

        if should_print():
            print(f"{Fore.YELLOW}Creating virtual environment...{Style.RESET_ALL}")
        subprocess.run([python_exec, "-m", "venv", "venv"], check=True)

        activate_script = ""
        if platform.system() == "Windows":
            activate_script = os.path.join(venv_path, "Scripts", "activate.bat")
        else:
            activate_script = os.path.join(venv_path, "bin", "activate")

        if should_print():
            print(
                f"{Fore.CYAN}Activating virtual environment and installing pylint and mypy...{Style.RESET_ALL}"
            )

        try:
            if platform.system() == "Windows":
                subprocess.run(
                    [activate_script, "&&", "pip", "install", "pylint", "mypy"],
                    shell=True,
                    check=True,
                )
            else:
                subprocess.run(
                    f"source {activate_script} && pip install pylint mypy",
                    shell=True,
                    executable="/bin/bash",
                    check=True,
                )
            if should_print():
                print(
                    f"{Fore.GREEN}pylint and mypy installed successfully inside the virtual environment."
                )
        except subprocess.CalledProcessError as e:
            if should_print():
                print(f"{Fore.RED}Error occurred during installation: {e}")
            return
    else:
        if should_print():
            print(
                f"{Fore.YELLOW}Virtual environment creation skipped.{Style.RESET_ALL}"
            )

    enable_mypy = (
        input(
            f"{Fore.YELLOW}Would you like to enable type checking with mypy? (y/n): {Style.RESET_ALL}"
        )
        .strip()
        .lower()
    )
    if enable_mypy == "y":
        if should_print():
            print(f"{Fore.GREEN}Type checking with mypy will be enabled.")
    else:
        if should_print():
            print(f"{Fore.YELLOW}Type checking with mypy skipped.{Style.RESET_ALL}")

    enable_pylint = (
        input(
            f"{Fore.YELLOW}Would you like to enable linting with pylint? (y/n): {Style.RESET_ALL}"
        )
        .strip()
        .lower()
    )
    if enable_pylint == "y":
        if should_print():
            print(f"{Fore.GREEN}Linting with pylint will be enabled.")
    else:
        if should_print():
            print(f"{Fore.YELLOW}Linting with pylint skipped.{Style.RESET_ALL}")

    if should_print():
        print(
            f"{Fore.GREEN}{Style.BRIGHT}Project initialization complete!{Style.RESET_ALL}"
        )


def serve_project(port: int, host: str, log_level: str, base_path: str = "") -> None:
    """
    CLI version of starting the server
    """
    sys.path.insert(0, os.getcwd())
    app = BirchRest(log_level=log_level, base_path=base_path)
    app.serve(host=host, port=port)


def run_tests(_args: Any) -> None:
    """Runs the unit tests using Python's unittest framework."""
    if should_print():
        print("Running unit tests...")
    try:
        subprocess.run(
            ["python", "-m", "unittest", "discover", "-s", "tests"],
            check=True,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )
    except:
        pass


def run_typecheck(_args: Any) -> None:
    """Runs type checking with mypy."""
    if should_print():
        print("Running type checks with mypy...")
    try:
        subprocess.run(["mypy", "."], check=True, stdout=sys.stdout, stderr=sys.stderr)
    except:
        pass


def run_lint(_args: Any) -> None:
    """Runs linting with pylint, excluding specified directories."""
    if should_print():
        print("Running lint checks with pylint...")

    exclude_dirs = ["venv", "__pycache__", ".venv", "node_modules"]

    ignore_argument = ",".join(exclude_dirs)

    try:
        subprocess.run(
            ["pylint", ".", f"--ignore={ignore_argument}"],
            check=True,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )
    except:
        pass


def generate_openapi(args: Any) -> None:
    """
    Generates the OpenAPI documentation for the BirchRest project and saves it to a file.

    Args:
        args: The command-line arguments, including the output filename.
    """
    sys.path.insert(0, os.getcwd())
    app = BirchRest()
    openapi_spec = app._generate_open_api()

    output_filename = args.filename or "openapi.json"

    try:
        with open(output_filename, "w") as f:
            json.dump(openapi_spec, f, indent=4)
        if should_print():
            print(
            f"{Fore.GREEN}OpenAPI documentation generated and saved to {output_filename}.{Style.RESET_ALL}"
        )
    except Exception as e:
        if should_print():
            print(f"{Fore.RED}Error writing OpenAPI documentation: {e}{Style.RESET_ALL}")


def main() -> None:
    """
    Entry point for the CLI.
    """
    parser = argparse.ArgumentParser(prog="birch", description="BirchRest CLI")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    init_parser = subparsers.add_parser(
        "init", help="Initialize a new BirchREST project"
    )
    init_parser.set_defaults(func=init_project)

    openapi_parser = subparsers.add_parser(
        "openapi", help="Generate OpenAPI documentation"
    )
    openapi_parser.add_argument(
        "--filename",
        type=str,
        default="openapi.json",
        help="Output filename for the OpenAPI JSON file (default: openapi.json)",
    )
    openapi_parser.set_defaults(func=generate_openapi)

    serve_parser = subparsers.add_parser("serve", help="Serve the BirchREST project")

    serve_parser.add_argument(
        "--port",
        type=int,
        default=13337,
        help="Port to start the server on (default: 13337)",
    )
    serve_parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host to bind the server to (default: 127.0.0.1)",
    )
    serve_parser.add_argument(
        "--log-level",
        type=str,
        default="info",
        choices=["debug", "info", "warning", "error", "critical"],
        help="Log level for the server (default: info)",
    )

    serve_parser.add_argument(
        "--base-bath",
        type=str,
        default="",
        help="Prefix the api with a global basepath (default: None)",
    )

    serve_parser.set_defaults(
        func=lambda args: serve_project(
            args.port, args.host, args.log_level, args.base_bath
        )
    )

    test_parser = subparsers.add_parser("test", help="Run unit tests")
    test_parser.set_defaults(func=run_tests)

    typecheck_parser = subparsers.add_parser(
        "typecheck", help="Run mypy for type checking"
    )
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
