from google.auth.transport.requests import Request
from google.auth import impersonated_credentials
import google



class GoogleADCAuthenticator:
    """Custom authenticator using Google Application Default Credentials with impersonation."""

    def __init__(self, target_service_account,scopes):
        # Obtain default ADC credentials
        source_credentials, _ = google.auth.default()
        # Create impersonated credentials
        self.credentials = impersonated_credentials.Credentials(
            source_credentials=source_credentials,
            target_principal=target_service_account,
            target_scopes=scopes,
        )
        if not self.credentials.valid:
            self.credentials.refresh(Request())

    def __call__(self, request):
        """Add Authorization header."""
        if not self.credentials.valid:
            self.credentials.refresh(Request())
        request.headers["Authorization"] = f"Bearer {self.credentials.token}"
        return request