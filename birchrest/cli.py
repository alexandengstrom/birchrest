import sys
import os
import argparse
from typing import Any
import shutil

from .app import BirchRest



def init_project(args: Any) -> None:
    """
    Initializes a new project. If a directory name is provided, it creates that directory
    and moves into it. Otherwise, it initializes the project in the current directory.
    """
    # Get current directory and set default init directory
    cur_dir = os.getcwd()
    init_dir = cur_dir

    # Prompt user for directory name
    dir_name = input("Choose a name for the directory (leave blank to init in current directory):\n")

    # Set init_dir to new directory if user specifies a name
    if len(dir_name) > 0:
        init_dir = os.path.join(cur_dir, dir_name)
        if not os.path.exists(init_dir):
            os.mkdir(init_dir)
            print(f"Directory '{dir_name}' created.")
        else:
            print(f"Directory '{dir_name}' already exists.")
    else:
        print("Initializing project in the current directory.")
    
    # Change into the new directory
    os.chdir(init_dir)
    print(f"Moved into directory: {os.getcwd()}")

    # Path to the boilerplate directory (assumed to be in the same directory as this script)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    boilerplate_dir = os.path.join(script_dir, '__boilerplate__')

    if not os.path.exists(boilerplate_dir):
        print(f"Boilerplate directory '__boilerplate__' not found in {script_dir}.")
        return

    # Copy boilerplate contents to the chosen directory
    try:
        for item in os.listdir(boilerplate_dir):
            src_path = os.path.join(boilerplate_dir, item)
            dest_path = os.path.join(init_dir, item)
            if os.path.isdir(src_path):
                # Recursively copy directories
                shutil.copytree(src_path, dest_path, dirs_exist_ok=True)
            else:
                # Copy individual files
                shutil.copy2(src_path, dest_path)
        print(f"Boilerplate contents copied to {init_dir}.")
    except Exception as e:
        print(f"Error copying boilerplate contents: {e}")

    """Initialize a new BirchRest project."""
    raise NotImplementedError


def serve_project(port: int, host: str, log_level: str) -> None:
    """
    CLI version of starting the server
    """
    sys.path.insert(0, os.getcwd())
    app = BirchRest(log_level=log_level)
    app.serve(host=host, port=port)

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

    args = parser.parse_args()

    if args.command:
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
