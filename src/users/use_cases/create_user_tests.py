import json
import uuid
from collections.abc import Generator
from unittest.mock import ANY

import pytest
from clickhouse_connect.driver import Client
from django.conf import settings

from event_log.tasks import send_events_to_clickhouse
from users.use_cases import CreateUser, CreateUserRequest, UserCreated

pytestmark = [pytest.mark.django_db]


@pytest.fixture()
def f_use_case() -> CreateUser:
    return CreateUser()


@pytest.fixture(autouse=True)
def f_clean_up_event_log(f_ch_client: Client) -> Generator:
    f_ch_client.query(f'TRUNCATE TABLE {settings.CLICKHOUSE_EVENT_LOG_TABLE_NAME}')
    yield


def test_user_created(f_use_case: CreateUser) -> None:
    request = CreateUserRequest(
        email='test@email.com', first_name='Test', last_name='Testovich',
    )

    response = f_use_case.execute(request)

    assert response.result.email == 'test@email.com'
    assert response.error == ''


def test_emails_are_unique(f_use_case: CreateUser) -> None:
    request = CreateUserRequest(
        email='test@email.com', first_name='Test', last_name='Testovich',
    )

    f_use_case.execute(request)
    response = f_use_case.execute(request)

    assert response.result is None
    assert response.error == 'User with this email already exists'


def test_event_log_entry_published(
    f_use_case: CreateUser,
    f_ch_client: Client,
) -> None:
    email = f'test_{uuid.uuid4()}@email.com'
    request = CreateUserRequest(
        email=email, first_name='Test', last_name='Testovich',
    )
    
    # Выполняем use-case, который добавляет событие в outbox
    f_use_case.execute(request)
    
    # Принудительно вызываем Celery-задачу для переноса событий в ClickHouse
    send_events_to_clickhouse()
    
    # Проверяем, что запись появилась в ClickHouse
    log = f_ch_client.query("""
            SELECT event_type, environment, event_context
            FROM default.event_log
            WHERE event_type = 'user_created'
        """)
    
    expected = [
        (
            'user_created',
            'Local',  # Из settings.ENVIRONMENT
            json.dumps({"email": email, "first_name": "Test", "last_name": "Testovich"}, sort_keys=True),
        ),
    ]
    
    print("log.result_rows:", log.result_rows)
    print("expected:", expected)
    
    assert log.result_rows == expected
