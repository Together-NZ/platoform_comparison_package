import requests
import json
from pathlib import Path
import google
from google.auth.transport.requests import Request
from google.auth import impersonated_credentials
import csv
import time
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
    
def get_dv360_standard_comparison_data(source,client_info):
    return _get_dv360_comparison_data(source, "dv360_standard",client_info)

def get_dv360_youtube_comparison_data(source,client_info):
    return _get_dv360_comparison_data(source, "dv360_youtube",client_info)

def _get_dv360_comparison_data(source,type,client):
        start_date = source.comparison_start_date
        end_date = source.comparison_end_date
        start_year, start_month,start_day = map(int,start_date.split('-'))
        end_year, end_month,end_day = map(int,end_date.split('-'))
        
        secrets = source.read_secrets()
        api= source.get_comparison_api()

        dv360_advertiser_id = secrets["TAP_DV360_ADVERTISER_ID"]
        if "kiwibank" in client.lower():
            dv360_service_account = secrets["TAP_DV360_KIWIBANK_SERVICE_ACCOUNT"]
        else:
            dv360_service_account = secrets["TAP_DV360_SERVICE_ACCOUNT"]
        authenticator = GoogleADCAuthenticator(dv360_service_account)
        headers = {"Authorization": f"Bearer {authenticator.credentials.token}"}
        
        template_path = Path(__file__).with_name(f"{type}.json")
        with open(template_path, "r") as f:
            payload = json.load(f)
            payload["params"]["filters"] = [{"type":"FILTER_ADVERTISER","value":dv360_advertiser_id}]
            payload["metadata"]["dataRange"]["customStartDate"]["year"] = start_year
            payload["metadata"]["dataRange"]["customStartDate"]["month"] = start_month
            payload["metadata"]["dataRange"]["customStartDate"]["day"] = start_day
            payload["metadata"]["dataRange"]["customEndDate"]["year"] = end_year
            payload["metadata"]["dataRange"]["customEndDate"]["month"] = end_month
            payload["metadata"]["dataRange"]["customEndDate"]["day"] = end_day
            
        response = requests.post(api,json=payload,headers=headers)
        print(response.json())
        query_id = response.json()["queryId"]
        run_api= f"{api}/{query_id}:run"
        print(run_api)
        response = requests.post(run_api,headers=headers)
        print(response.json())
        report_id = response.json()["key"]["reportId"]
        report_api = f"{api}/{query_id}/reports/{report_id}"
        print(report_api)
        response = requests.get(report_api,headers=headers)
        while True:
            if response.json()["metadata"]["status"]["state"] == "DONE":
                break
            else:
                time.sleep(10)
                response = requests.get(report_api, headers=headers)
                print("Waiting for report to be ready...")
                
        csv_url = response.json()["metadata"]["googleCloudStoragePath"]
        response = requests.get(csv_url, timeout=120)
        if response.status_code != 200:
            raise RuntimeError(f"Failed to download CSV: {response.status_code} - {response.text}")
        csv_content=response.content.decode("utf-8")
        result=[]
        try:
            reader = csv.DictReader(csv_content.splitlines())

            for row in reader:
                for column_name,value in row.items():
                    result.append({"column_name":column_name,"value":value})
                break
                        
        except Exception as e:
            print(f"Error: {e}")  
            
        clicks = impressions = media_cost = 0
        print(result)
        for item in result:
            
            if item['column_name'] == 'Clicks' and item['value'] is not None:
                clicks = item['value']
            elif item['column_name'] == 'Impressions' and item['value'] is not None:
                impressions = item['value']
            elif item['column_name'] == 'Revenue (Adv Currency)' and item['value'] is not None:
                media_cost = item['value']
            elif item['column_name'] == 'Advertiser Currency' or item['column_name'] == 'Advertiser ID':
                continue
            else:
                raise ValueError(f"Invalid column name: {item['column_name']}")
            
        return media_cost,impressions,clicks