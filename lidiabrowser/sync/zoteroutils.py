"""Utilities related to the Zotero API"""


from typing import Optional


def get_attachment_url(publicationdata: dict) -> str:
    attachment_url = None
    try:
        attachment_url = publicationdata.get(
            'links', {}
        ).get(
            'attachment', {}
        ).get('href', None)
    except AttributeError:
        # dict is different than expected
        pass
    if attachment_url:
        return attachment_url
    else:
        raise ValueError("publicationdata argument contains incorrect data")


def get_attachment_id_from_url(url: str) -> str:
    return url.rstrip('/').split('/')[-1]
    
