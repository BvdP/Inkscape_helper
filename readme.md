### Inkscape Helper

These are helper functions for some Inkscape plugins.

This code uses `unittest` and `mock` which can either be installed using `pip` or just by installing the packages.

# Running tests

Run all tests like so:
`python -m unittest discover`

Test individual modules like so:
`python -m unittest -v tests.test_<name>`

## Test coverage
A test coverage package is available via Pip or as a debian package.
Pip calls it `coverage`, the Debian package is called `python2-coverage` (I use the latter).

You call it as `python2-coverage run -m unittest discover` or `python2-coverage rum -m unittest -v tests.test_<name>`. This produces the same output as running unittest but it stores results in `.coverage`.

To get a report use `python2-coverage report` or `python2-coverage html`.

# Deploying

Run `./deploy.sh` (currently only on Linux). This copies the `inkscape_helper` folder to the Inkscape extensions folder so that it is accessible as an extension from within Inkscape.
