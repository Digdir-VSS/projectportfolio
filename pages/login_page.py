from nicegui import ui, app, Client
from fastapi.responses import RedirectResponse
import os

def register_login_pages(msal_app, AUTH_FLOW_STATES, USER_DATA, ENTRA_LOGOUT_ENDPOINT, SCOPE, REDIRECT_PATH):

    @ui.page("/login")
    def login():
        """
        Starts the authentication flow and redirects the user to log in on Microsoft's website.
        """
        auth_flow = msal_app.initiate_auth_code_flow(
            SCOPE,
            redirect_uri=f"{os.getenv('BASE_APPLICATION_URL')}{REDIRECT_PATH}",
        )
        browser_id = app.storage.browser["id"]
        AUTH_FLOW_STATES[browser_id] = auth_flow
        return RedirectResponse(auth_flow["auth_uri"])

    @ui.page(REDIRECT_PATH)
    def authorized(client: Client):
        """
        Handles the redirect from Microsoft after login.
        """
        browser_id = app.storage.browser["id"]
        auth_flow = AUTH_FLOW_STATES.get(browser_id, None)
        if auth_flow is None:
            return ui.navigate.to("/login")
        params_auth_state = client.request.query_params["state"] # type: ignore[union-attr]
        if params_auth_state != auth_flow["state"]:
            ui.label(f"Invalid state parameter")
            return
        query_params = dict(client.request.query_params) # type: ignore[union-attr]
        result = msal_app.acquire_token_by_auth_code_flow(auth_flow, query_params)
        if "error" in result:
            ui.label(f"Error: {result['error']} - {result.get('error_description')}")
            return
        from pages.utils import validate_token
        id_token = result.get("id_token")
        claims = validate_token(id_token, os.environ.get('TENANT_NAME'))
        if not claims:
            ui.label("Error: Invalid ID token.")
            return
        USER_DATA[browser_id] = claims
        print(USER_DATA.get(browser_id)["preferred_username"])
        ui.navigate.to("/")

    @ui.page("/logout")
    def logout():
        """
        Logs out the user and redirects to Microsoft logout endpoint.
        """
        browser_id = app.storage.browser["id"]
        if browser_id in AUTH_FLOW_STATES:
            del AUTH_FLOW_STATES[browser_id]
        if browser_id in USER_DATA:
            del USER_DATA[browser_id]
        if "user" in app.storage.user:
            del app.storage.user["user"]
        return RedirectResponse(f"{ENTRA_LOGOUT_ENDPOINT}?post_logout_redirect_uri={os.environ.get('BASE_APPLICATION_URL')}")