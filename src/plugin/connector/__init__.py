import logging
import requests

from spaceone.core.connector import BaseConnector

__all__ = ["RequestConnector"]

_LOGGER = logging.getLogger(__name__)


class RequestConnector(BaseConnector):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def send_request(
        self, url, headers, body=dict, method="GET", page=None, per_page=30
    ):
        try:
            if page:
                for response in self._pagination(url, headers, body, per_page, page):
                    yield response
            else:
                response = requests.get(url, headers=headers).json()
                yield response
        except Exception as e:
            _LOGGER.error(f"Request Error: {e}")
            raise e

    @staticmethod
    def _pagination(url, headers, body, per_page, page):
        responses = []
        while True:
            if url in "&":
                url = f"{url}&per_page={per_page}&page={page}"
            else:
                url = f"{url}?per_page={per_page}&page={page}"
            response = requests.get(url, headers=headers)
            response_json = response.json()
            if not response_json:
                break
            page += 1
            responses.extend(response_json)
        return responses

    @staticmethod
    def make_header(secret_data):
        github_token = secret_data.get("github_token")
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {github_token}",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        return headers
