import requests
import json 

def get_linkedin_comparison_data(source):
        secrets = source.read_secrets()   
        api= source.get_comparison_api()
        linkedin_access_token = secrets["TAP_LINKEDIN_ADS_ACCESS_TOKEN"]
        linkedin_account_id = secrets["TAP_LINKEDIN_ADS_ACCOUNT_ID"]
        headers = {
            "Authorization": f"Bearer {linkedin_access_token}",
            "LinkedIn-Version": "202511",
            "X-Restli-Protocol-Version": "2.0.0",
        }
        url = (
            f"{api}"
            "?q=analytics"
            f"&dateRange=(start:(year:{source.comparison_start_date.split('-')[0]},month:{source.comparison_start_date.split('-')[1]},day:{source.comparison_start_date.split('-')[2]}),end:(year:{source.comparison_end_date.split('-')[0]},month:{source.comparison_end_date.split('-')[1]},day:{source.comparison_end_date.split('-')[2]}))"
            "&timeGranularity=ALL"
            f"&accounts=List(urn%3Ali%3AsponsoredAccount%3A{linkedin_account_id})"
            "&pivot=ACCOUNT"
            "&fields=impressions,clicks,costInLocalCurrency"
        )
        response = requests.get(url, headers=headers)
        data = response.json()
        if data['elements']:
            clicks=data['elements'][0]['clicks']
            impressions=data['elements'][0]['impressions']
            media_cost=data['elements'][0]['costInLocalCurrency']
            return media_cost,impressions,clicks
        else:
            return 0,0,0