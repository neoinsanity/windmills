#!/usr/bin/env bash
###########################################################
### Script to execute Windmill unit tests.
###########################################################
#
# This script is to be run from the project root directory with the command:
#   <project_root>$ .bin/run_test.sh
#
# The command will create an html coverage report in the directory
# <project_root>/COVERAGE_REPORT.
#

# Remove pyc files that may cause false results.
find . -type f -iname \*.pyc -delete

# Remove the current coverage collection file
rm -f .coverage
rm -rf COVERAGE_REPORT

# Ensure that a test output directory is created to
# make a common location for test cruft.
mkdir -p TEST_OUT

# Increase ulimit for file handles
ulimit -n 1024

# Execute the tests as per the given config.
nosetests -c bin/nose.cfg
