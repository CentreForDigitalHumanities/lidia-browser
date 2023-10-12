#%%
import json
import logging
import os
import pathlib
import sqlite3

from dotenv import load_dotenv
import yaml
from pyzotero import zotero

logging.basicConfig(level=logging.INFO)


def load_configuration():
    load_dotenv()
    config = {
        'projroot': pathlib.Path(__file__).parents[0].resolve(),
        'dbname': os.getenv('DBNAME', '<not set>'),
        'library_id': os.getenv('ZOTERO_LIBRARY_ID', '<not set>'),
        'library_type': os.getenv('ZOTERO_LIBRARY_TYPE', '<not set>'),
        'api_key': os.getenv('ZOTERO_API_KEY', '<not set>'),
    }

    # Skip projroot: "argument of type 'PosixPath' is not iterable"
    if any('<not set>' in value for key, value in config.items() if key != 'projroot'):
        raise Exception("Provide all required configuration in your .env file.")

    return config


def create_tables(conn, cur):
    try:
        cur.execute(
        '''CREATE TABLE IF NOT EXISTS publications (
            id TEXT PRIMARY KEY
            , content JSON
            , attachment_id TEXT
            );
        ''')
        cur.execute(
        '''CREATE TABLE IF NOT EXISTS annotations (
            id TEXT PRIMARY KEY
            , content JSON
            , annotation JSON
            );
        ''')
        cur.execute(
        '''CREATE TABLE IF NOT EXISTS sync (
            library_id TEXT PRIMARY KEY
            , library_version INTEGER
            );
        ''')
        conn.commit()
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
    except Exception as e:
        logging.error(f"Exception: {e}")


def setup_database(dbpath):
    conn = sqlite3.connect(dbpath)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    create_tables(conn, cur)

    return conn, cur


def get_zotero_instance(config):
    return zotero.Zotero(
        config['library_id'],
        config['library_type'],
        config['api_key'],
        preserve_json_order=True
    )


def sync_publications(conn, cur, zot, since):
    """ Fetches publications which have been updated since the given library version.
    Saves the publications to database.
    """
    # All publications should be placed top-level (not in collections)
    # Non-publication items might exist as well but can be ignored.
    # (There's no way to filter on bibliographic items in general directly?)
    items = zot.everything(zot.top(since=since))
    if items:
        for item in items:
            key = item['key']
            obj = item
            # Annotations are linked to their parent PDF, not the bibliographic item
            # Assuming only one attachment per publication
            url = obj.get("links", {}).get("attachment", {}).get("href")
            attachment_id = url.rstrip('/').split('/')[-1] if url else ''
            try:
                cur.execute("""
                    INSERT INTO publications (id, content, attachment_id)
                    VALUES (:id, :content, :attachment_id)
                    ON CONFLICT (id) DO UPDATE SET
                            content = :content,
                            attachment_id = :attachment_id
                    ;""", {'id': key, 'content': json.dumps(obj), 'attachment_id': attachment_id}
                    )
                conn.commit()
            except sqlite3.Error as e:
                logging.error(f"Database error: {e}")
        logging.info(f"Updated {len(items)} publications")
    else:
        logging.info(f"No new publications found")


def sync_annotations(conn, cur, zot, since):
    """ Fetches items of type 'annotation' which have been updated since the given library version.
    Saves the annotations to database.
    """
    # TODO: use Zotero.follow() or iterfollow() methods
    # https://pyzotero.readthedocs.io/en/latest/#the-follow-and-everything-methods
    items = zot.everything(zot.items(itemType='annotation', since=since))
    if items:
        for item in items:
            key = item['key']
            annotation = item['data']['annotationComment']
            annotation = annotation.removeprefix('~~~~LIDIA~~~~')
            try:
                annotation = json.dumps(yaml.safe_load(annotation))
            except yaml.YAMLError as e:
                logging.error(f"YAMLError: {e}")
            try:
                cur.execute("""
                    INSERT INTO annotations (id, content, annotation)
                    VALUES (:id, :content, :annotation)
                    ON CONFLICT (id) DO UPDATE SET
                            content = :content,
                            annotation = :annotation
                    ;""", {
                            'id': key,
                            'content': json.dumps(item),
                            'annotation': annotation,
                        }
                    )
                conn.commit()
            except sqlite3.Error as e:
                logging.error(f"Database error: {e}")
        logging.info(f"Updated {len(items)} annotations")
    else:
        logging.info(f"No new annotations found")


def get_local_library_version(cur, zot):
    """ Returns the last synced library version from the local database.
    """
    try:
        cur.execute("""
            SELECT library_version
            FROM sync
            WHERE library_id = :library_id
            ;""", {'library_id': zot.library_id}
        )
        row = cur.fetchone()
        local_library_version = row[0] if row else -1
        logging.info(f"local_library_version: {local_library_version}")
        return local_library_version if local_library_version else 0
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")


def sync(conn, cur, zot):
    zotero_library_version = zot.last_modified_version()
    local_library_version = get_local_library_version(cur, zot)
    if zotero_library_version > local_library_version:
        sync_publications(conn, cur, zot, since=local_library_version)
        sync_annotations(conn, cur, zot, since=local_library_version)
        try:
            cur.execute('''
            INSERT INTO sync (library_id, library_version)
            VALUES (:library_id, :library_version)
            ON CONFLICT (library_id) DO UPDATE SET library_version = :library_version
            ;''', {
                    'library_version': zotero_library_version,
                    'library_id': zot.library_id
                }
            )
            conn.commit()
            logging.info("Sync successful")
        except sqlite3.Error as e:
            logging.error(f"Database error: {e}")
    else:
        logging.info("Local library up to date")


def main():
    config = load_configuration()
    dbpath = os.path.join(config['projroot'], config['dbname'])
    conn, cur = setup_database(dbpath)
    zot = get_zotero_instance(config)
    sync(conn, cur, zot)


if __name__ == "__main__":
    main()
