from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import dcc, html


def login_layout() -> html.Div:
    """Return the login page layout."""
    return html.Div(
        [
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H3("Login", className="card-title text-center mb-4"),
                        dbc.Input(id="login-username", placeholder="Username", className="mb-3"),
                        dbc.Input(
                            id="login-password",
                            placeholder="Password",
                            type="password",
                            className="mb-3",
                        ),
                        dbc.Button("Login", id="login-button", color="primary", className="w-100 mb-3"),
                        html.Div(id="login-message"),
                        html.Hr(),
                        dcc.Link("Don't have an account? Register", href="/register"),
                    ]
                ),
                className="mx-auto mt-5",
                style={"maxWidth": "400px"},
            ),
        ]
    )


def register_layout() -> html.Div:
    """Return the registration page layout."""
    return html.Div(
        [
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H3("Register", className="card-title text-center mb-4"),
                        dbc.Input(id="register-username", placeholder="Username", className="mb-3"),
                        dbc.Input(id="register-email", placeholder="Email", type="email", className="mb-3"),
                        dbc.Input(
                            id="register-password",
                            placeholder="Password",
                            type="password",
                            className="mb-3",
                        ),
                        dbc.Button("Register", id="register-button", color="success", className="w-100 mb-3"),
                        html.Div(id="register-message"),
                        html.Hr(),
                        dcc.Link("Already have an account? Login", href="/login"),
                    ]
                ),
                className="mx-auto mt-5",
                style={"maxWidth": "400px"},
            ),
        ]
    )
