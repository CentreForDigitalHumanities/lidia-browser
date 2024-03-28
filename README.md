# LIDIA Browser: Linguistic Diagnostics explorer

This is the source code for the [LIDIA Annotation Browser](https://lidia.hum.uu.nl/) website.
The annotation browser is a companion to the [LIDIA Zotero plugin](https://github.com/CentreForDigitalHumanities/lidia-zotero) for LIDIA, a pilot project for annotating linguistic diagnostics.

It is a Django project containing two apps:

- The `sync` app contains management commands and logic for fetching publication and annotation data from a Zotero library via the Zotero API using [pyzotero](https://github.com/urschrei/pyzotero).
- The `lidia` app contains functions for converting LIDIA YAML annotations to Django structures, and provides a browse/search interface using the Django Admin.


## Installation

Install the dependencies:

    pip install -r requirements.txt

Create a file `.env` in the repository root with your Zotero library and authentication details.
See the [pyzotero quickstart](https://github.com/urschrei/pyzotero#quickstart) for where to get a Zotero API key and find your library ID.

```sh
ZOTERO_LIBRARY_ID=12345
# Library type is 'user' or 'group'
ZOTERO_LIBRARY_TYPE=group
ZOTERO_API_KEY=a1b2c3d
```

By default, LIDIA Browser is set to use SQLite3, so no database setup is necessary.


## Usage

To run on a local machine, use:

```sh
cd lidiabrowser
python manage.py migrate
python manage.py sync
python manage.py populate
python manage.py runserver
```

You can remove raw sync data or converted sync data from the database using the `--refresh` option:

```sh
python manage.py sync --refresh
python manage.py populate --refresh
```
