from nicegui import ui, app, Client
from fastapi.responses import RedirectResponse
from frontend.pages.utils import validate_token
import os

def register_login_pages(msal_app, AUTH_FLOW_STATES, ENTRA_LOGOUT_ENDPOINT, SCOPE, REDIRECT_PATH):

    @ui.page("/login")
    def login():
        """
        Starts the authentication flow and redirects the user to log in on Microsoft's website.
        """
        auth_flow = msal_app.initiate_auth_code_flow(
            SCOPE,
            redirect_uri=f"{os.getenv('BASE_APPLICATION_URL')}{REDIRECT_PATH}",
        )
        AUTH_FLOW_STATES[auth_flow["state"]] = auth_flow
        return RedirectResponse(auth_flow["auth_uri"])

    @ui.page(REDIRECT_PATH)
    def authorized(client: Client):
        """
        Handles the redirect from Microsoft after login.
        """
        state = client.request.query_params.get("state")
        auth_flow = AUTH_FLOW_STATES.get(state, None)
        if auth_flow is None:
            return ui.navigate.to("/login")
        
        query_params = dict(client.request.query_params) # type: ignore[union-attr]
        result = msal_app.acquire_token_by_auth_code_flow(auth_flow, query_params)
        if "error" in result:
            ui.label(f"Error: {result['error']} - {result.get('error_description')}")
            return

        id_token = result.get("id_token")
        claims = validate_token(id_token, os.environ.get('TENANT_NAME'))
        if not claims:
            ui.label("Error: Invalid ID token.")
            return
        app.storage.user["claims"] = claims
        ui.navigate.to("/")

    @ui.page("/logout")
    def logout():
        """
        Logs out the user and redirects to Microsoft logout endpoint.
        """
        app.storage.user.pop("user", None)
        app.storage.user.pop("claims", None)
        return RedirectResponse(f"{ENTRA_LOGOUT_ENDPOINT}?post_logout_redirect_uri={os.environ.get('BASE_APPLICATION_URL')}")