### Inkscape Helper

These are helper functions for some Inkscape plugins.

This code uses `unittest` and `mock` which can either be installed using `pip` or just by installing the packages.

# Running tests

Run all tests like so:
`python -m unittest discover`

Test individual modules like so:
`python -m unittest -v tests.test_<name>`

# Deploying

Run `./deploy.sh` (currently only on Linux). This copies the `inkscape_helper` folder to the Inkscape extensions folder so that it is accessible as an extension from within Inkscape.
