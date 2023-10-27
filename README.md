# LIDIA Browser: Linguistic Diagnostics explorer

This project fetches bibliographic entries and annotations from the LinguisticDiagnostics Zotero group library, and allows to browse and search them.


## Installation

Install the dependencies:

    pip install -r requirements.txt

Create a file `lidiabrowser/lidiabrowser/.env` with your Zotero library and authentication details:

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
python manage.py runserver
```

