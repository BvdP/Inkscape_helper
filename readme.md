### Inkscape Helper

These are helper functions for some Inkscape plugins.

# Running tests

Run all tests like so:
`python -m unittest discover tests`

Test individual modules like so:
`python -m unittest -v tests.test_<name>

# Deploying

Run `./deploy.sh` (currently only on Linux). This copies the `inkscape_helper` folder to the Inkscape extensions folder so that it is accessible from inkscape extensions.
