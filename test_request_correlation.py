"""Exercise the production correlation installer without loading ML models."""

import asyncio
from uuid import UUID

import httpx
import pytest
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.testclient import TestClient

from request_correlation import RequestCorrelationMiddleware, install_request_correlation


def make_app(correlated: bool = True) -> FastAPI:
    app = FastAPI()
    if correlated:
        install_request_correlation(app)

    @app.get("/state")
    async def state(request: Request):
        await asyncio.sleep(0)
        return {"request_id": request.state.request_id}

    @app.get("/required")
    async def required(value: int):
        return {"value": value}

    @app.get("/handled")
    async def handled():
        raise HTTPException(415, "Please upload a JPEG or PNG image.")

    @app.get("/boom")
    async def boom():
        raise RuntimeError("test failure")

    @app.get("/existing-header")
    async def existing_header():
        return JSONResponse({"ok": True}, headers={"X-Request-ID": "route-value"})

    @app.get("/stream")
    async def stream():
        async def chunks():
            yield b"first"
            yield b"second"

        return StreamingResponse(chunks(), media_type="text/plain")

    return app


@pytest.fixture
def app() -> FastAPI:
    return make_app()


@pytest.mark.parametrize("header_name", ["X-Request-ID", "x-request-id", "X-REQUEST-ID"])
@pytest.mark.parametrize("request_id", ["client-trace-123", "", "  client trace  "])
def test_supplied_id_preserved_in_state_and_header(app, header_name, request_id):
    with TestClient(app) as client:
        response = client.get("/state", headers={header_name: request_id})
    assert response.status_code == 200
    assert response.json() == {"request_id": request_id}
    assert response.headers["X-Request-ID"] == request_id


def test_generated_ids_are_valid_unique_and_match_state(app):
    with TestClient(app) as client:
        responses = [client.get("/state") for _ in range(2)]
    ids = []
    for response in responses:
        assert response.status_code == 200
        request_id = response.headers["X-Request-ID"]
        assert str(UUID(request_id)) == request_id
        assert UUID(request_id).version == 4
        assert response.json() == {"request_id": request_id}
        ids.append(request_id)
    assert ids[0] != ids[1]


@pytest.mark.parametrize("request_id", [None, "error-trace"])
@pytest.mark.parametrize(
    "path,status", [("/missing", 404), ("/required", 422), ("/handled", 415), ("/boom", 500)]
)
def test_errors_keep_existing_status_body_and_content_type(app, path, status, request_id):
    headers = {} if request_id is None else {"X-Request-ID": request_id}
    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get(path, headers=headers)
    with TestClient(make_app(False), raise_server_exceptions=False) as client:
        baseline = client.get(path)
    assert response.status_code == baseline.status_code == status
    assert response.content == baseline.content
    assert response.headers["content-type"] == baseline.headers["content-type"]
    if request_id is None:
        assert UUID(response.headers["X-Request-ID"]).version == 4
    else:
        assert response.headers["X-Request-ID"] == request_id


def test_unhandled_exception_still_propagates_for_server_logging(app):
    with TestClient(app) as client:
        with pytest.raises(RuntimeError, match="test failure"):
            client.get("/boom")


def test_response_has_one_authoritative_id(app):
    with TestClient(app) as client:
        response = client.get("/existing-header", headers={"X-Request-ID": "client-value"})
    assert response.json() == {"ok": True}
    assert response.headers.get_list("X-Request-ID") == ["client-value"]


@pytest.mark.parametrize("path", ["/docs", "/redoc", "/openapi.json", "/stream"])
def test_documentation_and_streaming_responses(app, path):
    with TestClient(app) as client:
        response = client.get(path, headers={"X-Request-ID": "resource-trace"})
    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "resource-trace"
    if path == "/stream":
        assert response.content == b"firstsecond"


@pytest.mark.parametrize("request_id", [None, "static-trace"])
def test_static_responses(app, tmp_path, request_id):
    (tmp_path / "asset.txt").write_text("static asset", encoding="utf-8")
    app.mount("/static", StaticFiles(directory=tmp_path), name="static")
    headers = {} if request_id is None else {"X-Request-ID": request_id}
    with TestClient(app) as client:
        response = client.get("/static/asset.txt", headers=headers)
    assert response.status_code == 200
    assert response.text == "static asset"
    if request_id is None:
        assert UUID(response.headers["X-Request-ID"]).version == 4
    else:
        assert response.headers["X-Request-ID"] == request_id


def test_concurrent_requests_keep_independent_ids(app):
    async def run_requests():
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as client:
            supplied = [f"parallel-{i}" for i in range(10)]
            responses = await asyncio.gather(
                *(client.get("/state", headers={"X-Request-ID": value}) for value in supplied),
                *(client.get("/state") for _ in range(10)),
            )
        generated = []
        for i, response in enumerate(responses):
            assert response.status_code == 200
            value = response.headers["X-Request-ID"]
            assert response.json() == {"request_id": value}
            if i < len(supplied):
                assert value == supplied[i]
            else:
                assert UUID(value).version == 4
                generated.append(value)
        assert len(set(generated)) == len(generated)

    asyncio.run(run_requests())


@pytest.mark.parametrize("scope_type", ["lifespan", "websocket"])
def test_non_http_scopes_pass_through_unchanged(scope_type):
    scope = {"type": scope_type, "state": {"existing": "value"}}
    seen = []

    async def downstream(actual_scope, receive, send):
        seen.append(actual_scope)
        await send({"type": "test.message"})

    async def receive():
        return {"type": "test.receive"}

    async def send(message):
        seen.append(message)

    asyncio.run(RequestCorrelationMiddleware(downstream)(scope, receive, send))
    assert seen == [scope, {"type": "test.message"}]
    assert scope["state"] == {"existing": "value"}
