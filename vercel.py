import hashlib
import os
from typing import Any, Optional

import requests


class Endpoint:
    def __init__(self, path: str, method: str):
        self.path = path
        self.method = method

    def __str__(self):
        return self.path

    def __add__(self, other: Any):
        return str(self) + other

    def __radd__(self, other: Any):
        return other + str(self)


class Endpoints:
    base = "https://api.vercel.com"

    upload_file_endpoint = Endpoint("/v2/now/files", "POST")


class Vercel:
    def __init__(
        self,
        api_key: Optional[str] = None,
        team_id: Optional[str] = None,
    ):
        self.api_key = api_key
        self.team_id = team_id

        self.load_config_from_env()

    def load_config_from_env(self):
        if self.api_key is None:
            self.api_key = os.getenv("VERCEL_API_KEY")

        if self.team_id is None:
            self.team_id = os.getenv("VERCEL_TEAM_ID")

    def get_auth_headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.api_key}"}

    def make_request(
        self,
        endpoint: str,
        method: str,
        headers: dict[str, str],
        body: bytes,
    ) -> requests.Response:
        """
        Makes a request to the Vercel API with the given API endpoint, headers and body
        """
        url = Endpoints.base + endpoint
        response = requests.request(
            method,
            url,
            headers=headers,
            data=body,
        )

        return response

    def upload_file(self, content: bytes) -> str:
        """
        Uploads a deployment file. Returns the sha256 digest

        Reference: https://vercel.com/docs/rest-api#endpoints/deployments/upload-deployment-files
        """
        digest = get_sha256_digest(content)

        headers = self.get_auth_headers()
        headers.update({"x-vercel-digest": digest})

        endpoint = Endpoints.upload_file_endpoint

        response = self.make_request(
            endpoint.path,
            endpoint.method,
            headers=headers,
            body=content,
        )

        response.raise_for_status()

        return digest

    def upload_directory(self, directory: str, recursive: Optional[bool] = True) -> str:
        """
        Uploads all files from a directory
        """


def get_sha256_digest(content: bytes) -> str:
    m = hashlib.sha256()
    m.update(content)
    return m.hexdigest()
