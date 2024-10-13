import sys
import os
import argparse
from typing import Any

from .app import BirchRest

def init_project(args: Any) -> None:
    """
    Initializes a new project. If a directory name is provided, it creates that directory
    and moves into it. Otherwise, it initializes the project in the current directory.
    """
    cur_dir = os.getcwd()
    init_dir = cur_dir

    dir_name = input("Choose a name for the directory (leave blank to init in current directory):\n")

    if len(dir_name) > 0:
        init_dir = os.path.join(cur_dir, dir_name)
        if not os.path.exists(init_dir):
            os.mkdir(init_dir)
            print(f"Directory '{dir_name}' created.")
        else:
            print(f"Directory '{dir_name}' already exists.")
    else:
        print("Initializing project in the current directory.")
    
    os.chdir(init_dir)
    print(f"Moved into directory: {os.getcwd()}")
    
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
