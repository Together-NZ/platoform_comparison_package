from asyncio.tasks import run_coroutine_threadsafe
import json
from google.cloud import secretmanager
from google.cloud import bigquery
import requests
import google
from pathlib import Path
from google.auth.transport.requests import Request
from google.auth import impersonated_credentials
from .platform_api_call.fetch_tiktok import get_tiktok_comparison_data
from .platform_api_call.fetch_linkedin import get_linkedin_comparison_data
from .platform_api_call.fetch_meta import get_meta_comparison_data
from .platform_api_call.fetch_dv360 import get_dv360_standard_comparison_data, get_dv360_youtube_comparison_data
from .platform_api_call.fetch_snapchat import get_snapchat_comparison_data
import csv
import time
MELTANO_MARKER = "meltano_"

class GoogleADCAuthenticator:
    """Custom authenticator using Google Application Default Credentials with impersonation."""

    def __init__(self, target_service_account):
        # Obtain default ADC credentials
        source_credentials, _ = google.auth.default()
        # Create impersonated credentials
        self.credentials = impersonated_credentials.Credentials(
            source_credentials=source_credentials,
            target_principal=target_service_account,
            target_scopes=["https://www.googleapis.com/auth/doubleclickbidmanager"],
        )
        if not self.credentials.valid:
            self.credentials.refresh(Request())

    def __call__(self, request):
        """Add Authorization header."""
        if not self.credentials.valid:
            self.credentials.refresh(Request())
        request.headers["Authorization"] = f"Bearer {self.credentials.token}"
        return request
    
class Comparison_source:
    def __init__(self,comparison_name:str,dimension_filter:str,comparison_start_date:str,comparison_end_date:str,
                 secret_name:str,project_id:str):
        self.comparison_name = comparison_name
        self.dimension_filter = dimension_filter
        self.comparison_start_date = comparison_start_date
        self.comparison_end_date = comparison_end_date
        self.secret_name = secret_name
        self.project_id = project_id
        
    def _read_common_secrets(self):
        client = secretmanager.SecretManagerServiceClient()
        secret_path="projects/739679429225/secrets/airflow-variables-meltano_common_secret/versions/latest"
        response = client.access_secret_version(name=secret_path)
        return json.loads(response.payload.data.decode("UTF-8"))
    
    def read_secrets(self):
        common_secrets = self._read_common_secrets()
        client_secrets = json.loads(
            secretmanager.SecretManagerServiceClient()
            .access_secret_version(name=f"projects/{self.project_id}/secrets/{self.secret_name}/versions/latest")
            .payload.data.decode("UTF-8")
        )
        return {**common_secrets, **client_secrets}
    
    def get_comparison_name(self):
        return self.comparison_name

    def get_dimension_filter(self):
        return self.dimension_filter

    def get_comparison_start_date(self):
        return self.comparison_start_date

    def get_comparison_end_date(self):
        return self.comparison_end_date
    
    def get_comparison_api(self):
        secrets = self.read_secrets()
        meta_account_id = secrets["TAP_FACEBOOK_AIRBYTE_CONFIG_ACCOUNT_ID"]
        snapchat_ad_account_id = secrets["TAP_SNAPCHAT_ADS_AD_ACCOUNT_IDS"]
        comparison_api = {
            "meta":f"https://graph.facebook.com/v25.0/act_{meta_account_id}/insights",
            "linkedin": "https://api.linkedin.com/rest/adAnalytics",
            "dv360_standard": "https://doubleclickbidmanager.googleapis.com/v2/queries",
            "dv360_youtube": "https://doubleclickbidmanager.googleapis.com/v2/queries",
            "tiktok": "https://business-api.tiktok.com/open_api/v1.3/report/integrated/get/",
            "ttd": "https://api.thetradedesk.com/v3/myreports/reportschedule",
            "snapchat": f"https://adsapi.snapchat.com/v1/adaccounts/{snapchat_ad_account_id}/stats?granularity=TOTAL"
        }
        return comparison_api[self.comparison_name]
    

    def get_tiktok_comparison_data(self):
        return get_tiktok_comparison_data(self)
    
    def get_snapchat_comparison_data(self):
        secrets = self.read_secrets()
        self.snapchat_client_id = secrets["TAP_SNAPCHAT_ADS_CLIENT_ID"]
        self.snapchat_client_secret = secrets["TAP_SNAPCHAT_ADS_CLIENT_SECRET"]
        self.snapchat_refresh_token = secrets["TAP_SNAPCHAT_ADS_REFRESH_TOKEN"]
        return get_snapchat_comparison_data(self)
    
    def get_meta_comparison_data(self):
        return get_meta_comparison_data(self)
    
    def get_dv360_standard_comparison_data(self,client_info):
        return get_dv360_standard_comparison_data(self,client_info)
    
    def get_dv360_youtube_comparison_data(self,client_info):
        return get_dv360_youtube_comparison_data(self,client_info)
    
    def get_linkedin_comparison_data(self):
        return get_linkedin_comparison_data(self)
    
    def _meltano_suffix_from_secret_name(self):
        if MELTANO_MARKER not in self.secret_name:
            return self.secret_name
        _, _, suffix = self.secret_name.partition(MELTANO_MARKER)
        return suffix if suffix else self.secret_name
    
    
    def get_comparison_data(self):
        advertiser_info = self._meltano_suffix_from_secret_name()
        if "dv360" in self.comparison_name.lower():
            
            media_costs,impressions,clicks = getattr(self, f"get_{self.comparison_name}_comparison_data")(advertiser_info)
        else:
            
            media_costs,impressions,clicks = getattr(self, f"get_{self.comparison_name}_comparison_data")()
        return media_costs,impressions,clicks
    


    
    
if __name__ == "__main__":
    print(Comparison_source(comparison_name="snapchat",dimension_filter="",comparison_start_date="2026-05-07",comparison_end_date="2026-05-12",secret_name="airflow-variables-meltano_uowaikato_main",project_id="739679429225").get_snapchat_comparison_data())