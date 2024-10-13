# type: ignore

import unittest
from unittest.mock import patch, MagicMock
import sys
from birchrest.cli import main, serve_project, init_project
import argparse

class TestBirchRestCLI(unittest.TestCase):

    @patch('birchrest.cli.BirchRest')
    def test_serve_project(self, mock_birchrest):
        """Test that the serve_project function starts the BirchRest server with the correct parameters."""
        mock_app_instance = MagicMock()
        mock_birchrest.return_value = mock_app_instance

        serve_project(port=5000, host="0.0.0.0", log_level="debug")

        mock_birchrest.assert_called_once_with(log_level="debug")
        mock_app_instance.serve.assert_called_once_with(host="0.0.0.0", port=5000)

    @patch('argparse.ArgumentParser.parse_args')
    @patch('birchrest.cli.serve_project')
    def test_main_with_serve(self, mock_serve_project, mock_parse_args):
        """Test the main function when the serve command is invoked."""
        mock_parse_args.return_value = argparse.Namespace(
            command="serve", port=13337, host="127.0.0.1", log_level="info", func=mock_serve_project
        )

        main()

        mock_serve_project.assert_called_once_with(mock_parse_args.return_value)

    @patch('argparse.ArgumentParser.parse_args')
    def test_main_with_no_command(self, mock_parse_args):
        """Test the main function when no command is provided (prints help)."""
        mock_parse_args.return_value = argparse.Namespace(command=None)

        with patch('argparse.ArgumentParser.print_help') as mock_print_help:
            main()
            mock_print_help.assert_called_once()

    @patch('birchrest.cli.init_project')
    @patch('argparse.ArgumentParser.parse_args')
    def test_main_with_init(self, mock_parse_args, mock_init_project):
        """Test the main function when the init command is invoked."""
        mock_parse_args.return_value = argparse.Namespace(command="init", func=mock_init_project)

        main()

        mock_init_project.assert_called_once()

if __name__ == "__main__":
    unittest.main()
