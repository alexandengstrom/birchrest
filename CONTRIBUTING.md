# Contributing to BirchRest
Thanks for taking an interest in contributing to BirchRest! Any help, whether it's fixing a bug, adding a feature, or reporting an issue, is greatly appreciated.
## How to Contribute
### Pull Requests
Pull requests are welcome! If you’ve made improvements or fixed something, here’s how to submit a pull request:

1. Fork the repository and create a new branch (```git checkout -b feature/your-feature```).
2. Commit your changes (```git commit -m 'Add a new feature'``` ).
3. Push your changes (```git push origin feature/your-feature```).
4. Open a pull request and describe what you’ve changed.

### Reporting Issues
If you find a problem that you can’t solve yourself or don’t have time to work on, feel free to open an issue. Please provide as much detail as you can, including steps to reproduce the issue and any logs or error messages. Suggestions and discussions on potential solutions are always welcome!

## What Happens When You Open a Pull Request
When you submit a pull request, some automated checks will run. These checks need to pass before the pull request can be merged:

1. **Unit Tests**: All unit tests will run on different Python versions (>=3.8) across various operating systems (Windows, macOS, and Linux). This ensures everything works as expected in different environments.
2. **Code Coverage**: The project requires at least 80% code coverage. If the tests don't cover enough of the code, the pull request will fail.
3. **Type Checking**: mypy will check the code for correct type annotations. The pull request must pass this check.
4. **Linting**: pylint will check the code style. If the code doesn’t meet the style requirements, the pull request will need to be updated.



