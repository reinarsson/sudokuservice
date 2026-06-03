from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import Dash, Input, Output, State, callback, dcc, html, no_update

from web.layouts.auth import login_layout, register_layout
from web.layouts.sudoku import sudoku_layout

dash_app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
)

dash_app.layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        dcc.Store(id="auth-store", storage_type="session"),
        html.Div(id="page-content"),
    ]
)


@callback(
    [Output("page-content", "children"), Output("url", "pathname")],
    Input("url", "pathname"),
    State("auth-store", "data"),
)
def display_page(pathname: str | None, auth_data: dict[str, str] | None) -> tuple[object, object]:
    """Route to the correct page layout, redirecting unauthenticated users."""
    if pathname == "/register":
        return register_layout(), no_update
    if pathname == "/sudoku":
        if not auth_data or "access_token" not in auth_data:
            return login_layout(), "/login"
        return sudoku_layout(), no_update
    return login_layout(), no_update


# Import callbacks so they are registered with Dash
import web.callbacks.auth as _auth_callbacks  # noqa: E402, F401
import web.callbacks.sudoku as _sudoku_callbacks  # noqa: E402, F401

if __name__ == "__main__":
    from core.config import Settings
    settings = Settings()
    dash_app.run(host=settings.api_host, port=settings.dash_port, debug=True)
