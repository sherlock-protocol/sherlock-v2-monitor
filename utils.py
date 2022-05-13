import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry


def requests_retry_session(
    retries=5,
    backoff_factor=1,
    status_forcelist=tuple(x for x in requests.status_codes._codes if x / 100 != 2 and x / 100 != 1),
    session=None,
):
    """Create a `requests` session that retries on certain error codes.

    Args:
        retries (int, optional): Number of attempted retries after the initial request. Defaults to 5.
        backoff_factor (int, optional): Exponential backoff factor. Defaults to 1.
        status_forcelist (List[int], optional): List of HTTP status codes that should trigger a retry.
                                                Defaults to all except 1XX and 2XX.
        session (Session, optional): `requests` session to setup retries for.
                                     If not specified, a new `requests` session will be created.

    Returns:
        Session: `requests` session
    """
    # Generate new session or use the provided one
    session = session or requests.Session()

    # Setup retry adapter
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)

    # Apply retry adapter to HTTP and HTTP requests
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    return session
