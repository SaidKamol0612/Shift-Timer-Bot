import json
from pathlib import Path
from typing import Dict


class RequestUtils:
    _file_path = Path(__file__).parent / "requests.json"

    @classmethod
    def load_requests(cls) -> Dict[str, str]:
        """Load requests from file as {user_id: channel_id} dict."""
        if not cls._file_path.exists():
            return {}
        try:
            with cls._file_path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}

    @classmethod
    def save_requests(cls, requests: Dict[str, str]) -> None:
        """Save requests dict to file."""
        with cls._file_path.open("w", encoding="utf-8") as f:
            json.dump(requests, f, ensure_ascii=False, indent=4)

    @classmethod
    def has_request(cls, user_id: int, channel_id: str) -> bool:
        """Check if user_id already linked to channel_id."""
        requests = cls.load_requests()
        return requests.get(str(user_id)) == channel_id

    @classmethod
    def add_request(cls, user_id: int, channel_id: str) -> None:
        """Add or update request."""
        requests = cls.load_requests()
        requests[str(user_id)] = channel_id
        cls.save_requests(requests)

    @classmethod
    def remove_request(cls, user_id: int, channel_id: str) -> None:
        """Remove request if it matches channel_id."""
        requests = cls.load_requests()
        if requests.get(str(user_id)) == channel_id:
            del requests[str(user_id)]
            cls.save_requests(requests)
