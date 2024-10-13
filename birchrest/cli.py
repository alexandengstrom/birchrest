import sys
import os
import argparse

from .app import BirchRest

def init_project() -> None:
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
