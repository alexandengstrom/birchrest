# type: ignore

import unittest
from unittest.mock import patch, MagicMock, mock_open
import sys
from birchrest.cli import main, serve_project, init_project, generate_openapi, run_lint, run_tests, run_typecheck
import argparse
import subprocess
import json
class TestBirchRestCLI(unittest.TestCase):

    @patch('birchrest.cli.BirchRest')
    def test_serve_project(self, mock_birchrest):
        """Test that the serve_project function starts the BirchRest server with the correct parameters."""
        mock_app_instance = MagicMock()
        mock_birchrest.return_value = mock_app_instance

        serve_project(port=5000, host="0.0.0.0", log_level="debug")

        mock_birchrest.assert_called_once_with(log_level="debug", base_path="")
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
        
    @patch('builtins.input', side_effect=['', 'n', 'n', 'n'])
    @patch('os.mkdir')
    @patch('shutil.copytree')
    @patch('shutil.copy2')
    def test_init_project_no_directory(self, mock_copy2, mock_copytree, mock_mkdir, mock_input):
        """Test project initialization in the current directory."""
        with patch('os.path.exists', return_value=True):
            init_project(None)
            mock_mkdir.assert_not_called()
            mock_copy2.assert_called()
            mock_copytree.assert_called()

    @patch('subprocess.run')
    def test_run_tests(self, mock_subprocess_run):
        """Test running unit tests."""
        run_tests(None)
        mock_subprocess_run.assert_called_once_with(
            ["python", "-m", "unittest", "discover", "-s", "tests"],
            check=True,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )

    @patch('subprocess.run')
    def test_run_typecheck(self, mock_subprocess_run):
        """Test running mypy for type checking."""
        run_typecheck(None)
        mock_subprocess_run.assert_called_once_with(
            ["mypy", "."], check=True, stdout=sys.stdout, stderr=sys.stderr
        )

    @patch('subprocess.run')
    def test_run_lint(self, mock_subprocess_run):
        """Test running pylint for linting."""
        run_lint(None)
        mock_subprocess_run.assert_called_once_with(
            ["pylint", ".", "--ignore=venv,__pycache__,.venv,node_modules"],
            check=True,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )

    @patch('birchrest.cli.BirchRest')
    @patch('builtins.open', new_callable=mock_open)
    def test_generate_openapi(self, mock_open_file, mock_birchrest):
        """Test OpenAPI documentation generation."""
        mock_app_instance = MagicMock()
        mock_birchrest.return_value = mock_app_instance
        mock_app_instance._generate_open_api.return_value = {"openapi": "3.0.0"}

        args = argparse.Namespace(filename="openapi_test.json")
        generate_openapi(args)

        mock_birchrest.assert_called_once()
        mock_app_instance._generate_open_api.assert_called_once()

        expected_output = json.dumps({"openapi": "3.0.0"}, indent=4)
        written_content = ''.join(call.args[0] for call in mock_open_file().write.mock_calls)

        self.assertEqual(written_content, expected_output)



if __name__ == "__main__":
    unittest.main()
