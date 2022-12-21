# Django - Success Center

## Description
Recording and management of students that use the STEP program. </br>
Management of STEP Employees and STEP Centers.

## Installation
1. git submodule update --init --recursive
2. Run the script located in ./scripts/general/installers/run.sh
3. Follow the instructions prompted on the screen.
4. If all tests pass, the program will be installed.

## Test
# Pytest Testing
This is the current way to run unit test, to run tests pytest -n auto

# Legacy Testing
Run tests with python manage.py test.
To skip Selenium (browser page tests, which can run slow/take a while), use the command
python manage.py test --exclude-tag=functional.
Note: To run in parallel (multi-threading): python manage.py test --parallel
