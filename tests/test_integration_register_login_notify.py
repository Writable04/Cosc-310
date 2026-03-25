import json
import uuid
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from app.main import app
from app.routers.dependencies import accounts_storage

# Mock SMTP so no real email is sent
smtp_mock = patch("smtplib.SMTP", MagicMock())
smtp_mock.start()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture(autouse=True)
def clean_accounts_storage_after_tests():
    existing_accounts = {}
    path = accounts_storage.path
    if path.exists():
        existing_accounts = json.loads(path.read_text())

    yield
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(existing_accounts, indent=2))


def test_register_login_send_authenticated_notification(client: TestClient) -> None:
    random_id = uuid.uuid4()
    username = f"test{random_id}"
    password = "Password123"
    email = f"test{random_id}@example.com"
    role = "admin"

    register_response = client.post(
        f"/authentication/register/{username}",
        params={
            "password": password,
            "validatated_password": password,
            "role": role,
            "email": email,
        },
    )

    assert register_response.status_code == 200

    login_response = client.post(
        f"/authentication/login/{username}",
        params={"password": password},
    )
    login_data = login_response.json()
    assert login_response.status_code == 200

    login_token = login_data["token"]

    notify_response = client.post(
        f"/notification/send/{username}/{login_token}",
        params={
            "customer_username": username,
            "subject": "Hello",
            "msg": "World",
        },
    )
    assert notify_response.status_code == 200


def test_send_notification_invalid_token(client: TestClient) -> None:
    random_id = uuid.uuid4()
    username = f"test{random_id}"
    password = "Password123"    
    email = f"test{random_id}@example.com"
    register_response = client.post(
        f"/authentication/register/{username}",
        params={
            "password": password,
            "validatated_password": password,
            "role": "admin",
            "email": email,
        },
    )
    assert register_response.status_code == 200

    notify_response  = client.post(
        f"/notification/send/{username}/invalid-token",
        params={
            "customer_username": username,
            "subject": "Hello",
            "msg": "Hell",
        },
    )
    assert notify_response.status_code == 401
