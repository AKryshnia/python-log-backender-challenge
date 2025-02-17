import clickhouse_connect
import pytest
from clickhouse_connect.driver import Client
from django.conf import settings


@pytest.fixture(scope='module')
def f_ch_client() -> Client:
    client = clickhouse_connect.get_client(
        host=settings.CLICKHOUSE_HOST,
        port=settings.CLICKHOUSE_PORT,
        username=settings.CLICKHOUSE_USER,  # должно быть ASCII
        password=settings.CLICKHOUSE_PASSWORD,
        database=settings.CLICKHOUSE_SCHEMA,
    )
    yield client
    client.close()
