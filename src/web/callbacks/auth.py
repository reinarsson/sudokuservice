from __future__ import annotations

import httpx
from dash import Input, Output, State, callback, html, no_update

from core.config import Settings

_settings = Settings()
_BASE_URL = f"http://{_settings.api_host}:{_settings.api_port}/api/v1/auth"


@callback(
    [
        Output("login-message", "children"),
        Output("auth-store", "data"),
        Output("url", "pathname", allow_duplicate=True),
    ],
    Input("login-button", "n_clicks"),
    [State("login-username", "value"), State("login-password", "value")],
    prevent_initial_call=True,
)
def handle_login(
    n_clicks: int | None,
    username: str | None,
    password: str | None,
) -> tuple[object, object, object]:
    """Send login request to the auth API and store tokens."""
    if not username or not password:
        error_msg = html.Span("Please fill in all fields.", style={"color": "red"})
        return error_msg, no_update, no_update

    with httpx.Client() as client:
        response = client.post(
            f"{_BASE_URL}/login",
            json={"username": username, "password": password},
        )

    if response.status_code == 200:
        data = response.json()
        return no_update, data, "/sudoku"

    detail = response.json().get("detail", "Login failed.")
    error_msg = html.Span(detail, style={"color": "red"})
    return error_msg, no_update, no_update


@callback(
    Output("register-message", "children"),
    Input("register-button", "n_clicks"),
    [
        State("register-username", "value"),
        State("register-email", "value"),
        State("register-password", "value"),
    ],
    prevent_initial_call=True,
)
def handle_register(
    n_clicks: int | None,
    username: str | None,
    email: str | None,
    password: str | None,
) -> object:
    """Send registration request to the auth API."""
    if not username or not email or not password:
        return html.Span("Please fill in all fields.", style={"color": "red"})

    with httpx.Client() as client:
        response = client.post(
            f"{_BASE_URL}/register",
            json={"username": username, "email": email, "password": password},
        )

    if response.status_code == 201:
        return html.Span(
            "Registration successful! You can now login.",
            style={"color": "green"},
        )
    detail = response.json().get("detail", "Registration failed.")
    return html.Span(detail, style={"color": "red"})
