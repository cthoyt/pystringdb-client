"""
Python library for interacting with STRINGdb of protein-protein interaction networks.

@jonathanronen 9/2015
"""

import logging
import requests
import pandas as pd
import xml.etree.cElementTree as et
from StringIO import StringIO

logger = logging.getLogger(__name__)

STRINGDB_ADDRESSES = [
    ("string-db.org",   "Main entry point of STRING"),
    ("string.embl.de",  "Alternative entry point of STRING"),
    ("stitch.embl.de",  "The sister database of STRING"),
]

STRINGDB_FORMATS = {
    'json',
    'tsv',
    'tsv-no-header',
    'psi-mi',
    'psi-mi-tab',
    'image',
}

PSIMITAB_COLUMNS = [
    'Unique identifier for interactor A',
    'Unique identifier for interactor B',
    'Alternative identifier for interactor A',
    'Alternative identifier for interactor B',
    'Aliases for A',
    'Aliases for B',
    'Interaction detection methods',
    'First author surname(s)',
    'Identifier of the publication',
    'NCBI Taxonomy identifier for interactor A',
    'NCBI Taxonomy identifier for interactor B',
    'Interaction types',
    'Source databases',
    'Interaction identifier(s)',
    'Confidence score',
]

STRINGDB_REQUEST_TEMPLATE = "{http}://{address}/api/{format}/{request}"

def do_request(request, req_format, params, https=False, database='string-db.org'):
    """
    Send actual HTTP request to API.
    """
    url = STRINGDB_REQUEST_TEMPLATE.format(
        http='https' if https else 'http',
        address=database,
        format=req_format,
        request=request)
    resp = requests.get(url, params=params)
    logger.debug('Requested {}'.format(resp.url))

    if resp.status_code == 200:
        return resp
    else:
        raise Exception(resp)

def get_interactions(identifiers, q_format='psi-mi', https=False, database='string-db.org'):
    """
    Query DB for interaction network in PSI-MI 2.5 format or PSI-MI-TAB format (similar to tsv).
    `identifiers` must be a list
    `format` may be 'psi-mi' or 'psi-mi-tab'
    If 'psi-mi', the response is returned in PSI-MI 2.5 XML format. This method will return
    an xml ElementTree object

    Example:
    ########
    results = stringdb.get_interaftions(['ALK'], format='psi-mi')

    If `format='psi-mi-tab'` results are returned in Tab-delimited form of PSI-MI
    (similar to tsv, modeled after the IntAct specification,
        Contains less info than XML response.)
    This method will return a pandas.DataFrame object.

    Example:
    ########
    results = stringdb.get_interaftions(['ALK'], format='psi-mi-tab')
    results.to_csv('outfile.tsv', delimiter='\t', index=False)
    """
    if q_format not in {'psi-mi', 'psi-mi-tab'}:
        raise Exception("format has to be one of ('psi-mi', 'psi-mi-tab'). {} is invalid.".format(q_format))
    resp = do_request('interactionsList', q_format, 
        {'identifiers': identifiers}, https=https, database=database)
    if q_format == 'psi-mi':
        return et.fromstring(resp.text)
    elif q_format == 'psi-mi-tab':
        sio = StringIO(resp.text)
        return pd.read_csv(sio, delimiter='\t', header=None, names=PSIMITAB_COLUMNS)

def get_interactions_image(identifier, flavor, filename, required_score=950,
    limit=50, https=False, database='string-db.org'):
    """
    Save network image of interactions to file.
    `identifiers` is the protein name
    `flavor` is one of:
        'evidence' for colored multilines
        'confidence' for singled lines where hue correspond to confidence score
        'actions' for stitch only.
    `filename` is the file to save the png to.

    """

    r = do_request('network', 'image',
        {'identifier': identifier, 'required_score': required_score, 'limit': limit},
        https=https, database=database)
    with open(filename, 'wb') as outfile:
        for chunk in r:
            outfile.write(chunk)


