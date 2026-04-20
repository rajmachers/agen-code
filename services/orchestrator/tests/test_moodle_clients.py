import asyncio

from app.core import clients


def test_moodle_lookup_cohorts_blank_query_skips_ws_call(monkeypatch) -> None:
    async def fake_ws_call(*_args, **_kwargs):
        raise AssertionError("WS call should not happen for blank query")

    monkeypatch.setattr(clients, "_moodle_ws_call", fake_ws_call)

    result = asyncio.run(clients.moodle_lookup_cohorts(query="", limit=10))

    assert result == []
