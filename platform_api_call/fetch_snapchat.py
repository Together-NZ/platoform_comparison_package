import requests
import json

def get_access_token(source):
    url = "https://accounts.snapchat.com/login/oauth2/access_token"
    params = {
        "client_id": source.snapchat_client_id,
        "client_secret": source.snapchat_client_secret,
        "grant_type":"refresh_token",
        "refresh_token": source.snapchat_refresh_token
    }
    response = requests.post(url, params=params)
    data = response.json()
    if response.status_code != 200:
        raise ValueError(f"Failed to get access token: {data}")
    return data["access_token"]



def get_snapchat_comparison_data(source):
    snapchat_access_token = get_access_token(source)
    api= source.get_comparison_api()
    params = {
        "fields": "impressions,swipes,spend",
        "breakdown": "campaign",
        "start_time": f"{source.comparison_start_date}T00:00:00.000",
        "end_time": f"{source.comparison_end_date}T00:00:00.000",
    }
    headers = {
        "Authorization": f"Bearer {snapchat_access_token}",
    }
    swipes = media_cost = impressions = 0
    response = requests.get(api, params=params, headers=headers)
    data = response.json()
    result = data["total_stats"][0]["total_stat"]["breakdown_stats"]["campaign"]
    for entity in result:

        impressions_response = entity["stats"]["impressions"]
        swipes_response = entity["stats"]["swipes"]
        spend_response = entity["stats"]["spend"]
        media_cost_response = spend_response / 1000000
        
        impressions += impressions_response
        swipes += swipes_response
        media_cost += media_cost_response

    return media_cost, impressions, swipes
