#%%
import json
import logging
import os
import pathlib
import sqlite3

from dotenv import load_dotenv
from pyzotero import zotero

#%% Logging config
logging.basicConfig(level=logging.INFO)

#%% Zotero library configuration
load_dotenv()
LIBRARY_ID = os.getenv('ZOTERO_LIBRARY_ID')
LIBRARY_TYPE = os.getenv('ZOTERO_LIBRARY_TYPE')
API_KEY = os.getenv('ZOTERO_API_KEY')

#%% Zotero instance
z = zotero.Zotero(LIBRARY_ID, LIBRARY_TYPE, API_KEY, preserve_json_order=True)

#%% SQLite database configuration
PROJROOT = pathlib.Path(__file__).parents[0].resolve()
DBNAME = os.environ['DBNAME']
DBPATH = os.path.join(PROJROOT, DBNAME)
conn = sqlite3.connect(DBPATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

def prepare_db():
    cur.execute(
    '''CREATE TABLE IF NOT EXISTS publications (
        key TEXT PRIMARY KEY
        , content JSON
        );
    ''')
    cur.execute(
    '''CREATE TABLE IF NOT EXISTS annotations (
        key TEXT PRIMARY KEY
        , content JSON
        );
    ''')
    cur.execute(
    '''CREATE TABLE IF NOT EXISTS sync (
        library TEXT PRIMARY KEY
        , library_version INTEGER
        );
    ''')
    conn.commit()

prepare_db()

#%%
def sync_publications(since):
    """ Fetches publications which have been updated since the given library version.
    Saves the publications to database.
    Returns 1 if successful, 0 otherwise.
    """
    # All publications should be placed top-level (not in collections)
    # Non-publication items might exist as well but can be ignored.
    # (There's no way to filter on bibliographic items in general directly?)
    items = z.everything(z.top(since=since))
    if items:
        for i, item in enumerate(items):
            key = item['key']
            obj = item
            cur.execute("""
                INSERT INTO publications (key, content)
                VALUES (:key, :content)
                ON CONFLICT (key) DO UPDATE SET content = :content
                ;""", {'key': key, 'content': json.dumps(obj)}
                )
            conn.commit()
        logging.info(f"Updated {i} publications")
        return 1
    else:
        logging.info(f"No new publications found")
        return 0


def sync_annotations(since):
    """ Fetches items of type 'annotation' which have been updated since the given library version.
    Saves the annotations to database.
    Returns 1 if successful, 0 otherwise.
    """
    # TODO: use Zotero.follow() or iterfollow() methods
    # https://pyzotero.readthedocs.io/en/latest/#the-follow-and-everything-methods
    items = z.everything(z.items(itemType='annotation', since=since))
    if items:
        for i, item in enumerate(items):
            key = item['key']
            obj = item
            cur.execute("""
                INSERT INTO annotations (key, content)
                VALUES (:key, :content)
                ON CONFLICT (key) DO UPDATE SET content = :content
                ;""", {'key': key, 'content': json.dumps(obj)}
                )
            conn.commit()
        logging.info(f"Updated {i + 1} annotations")
        return 1
    else:
        logging.info(f"No new annotations found")
        return 0


def get_local_library_version():
    """ Returns the last synced library version from the local database
    """
    cur.execute("""
        SELECT library_version
        FROM sync
        WHERE library=:library_id
        ;""", {'library_id': z.library_id}
    )
    row = cur.fetchone()
    local_library_version = row[0] if row else -1
    logging.info(f"local_library_version: {local_library_version}")
    return local_library_version if local_library_version else 0


def sync():
    zotero_library_version = z.last_modified_version()
    local_library_version = get_local_library_version()
    if zotero_library_version > local_library_version:
        p = sync_publications(since=local_library_version)
        a = sync_annotations(since=local_library_version)
        if p and a:
            cur.execute('''
            INSERT INTO sync (library, library_version)
            VALUES (:library_id, :library_version)
            ON CONFLICT (library) DO UPDATE SET library_version = :library_version
            ;''', {
                    'library_version': zotero_library_version,
                    'library_id': z.library_id
                }
            )
            conn.commit()
            logging.info("Sync successful")
        else:
            logging.warning("Sync incomplete")
    else:
        logging.info("Local library up to date")

#%%
sync()

#%%
logging.info(
    f"Local library version: {get_local_library_version()}, Remote library version: {z.last_modified_version()}",
)
