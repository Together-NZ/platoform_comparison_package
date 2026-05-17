import requests
import json


def get_tiktok_comparison_data(source):
        secrets = source.read_secrets()
        tiktok_access_token = secrets["TAP_TIKTOK_ACCESS_TOKEN"]
        api= source.get_comparison_api()
        params: dict[str, str | int] = {
            "advertiser_id": secrets["TAP_TIKTOK_ADVERTISER_ID"],
            "service_type": "AUCTION",
            "report_type": "BASIC",
            "data_level": "AUCTION_ADVERTISER",
            "dimensions": json.dumps(["advertiser_id"]),
            "metrics": json.dumps(["spend", "impressions", "clicks"]),
            "start_date": source.comparison_start_date,
            "end_date": source.comparison_end_date,
            "page": 1,
            "page_size": 1000,
        }


        headers = {
            "Access-Token": tiktok_access_token,
        }
        response = requests.get(api, params=params, headers=headers)
        body = response.json()
        if "code" in body and body["code"] != 0:
            raise RuntimeError(
                f"TikTok API error: {body.get('message', body)} (code={body.get('code')})"
            )
        data = body.get("data")
        if data is None:
            return 0.0, 0.0, 0.0
        lst = data.get("list") or []
        if not lst:
            return 0.0, 0.0, 0.0
        metrics = (lst[0] or {}).get("metrics") or {}
        if metrics is None:
            return 0.0, 0.0, 0.0
        media_costs = float(metrics.get("spend") or 0)
        impressions = float(metrics.get("impressions") or 0)
        clicks = float(metrics.get("clicks") or 0)
        return media_costs, impressions, clicks