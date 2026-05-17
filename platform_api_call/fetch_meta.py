import requests
import json

def get_meta_comparison_data(source):
        secrets = source.read_secrets()
        meta_access_token = secrets["TAP_FACEBOOK_AIRBYTE_CONFIG_ACCESS_TOKEN"]
        api= source.get_comparison_api()
        compare_params = {
            "meta":{
                "fields":"spend,impressions,clicks",
                "time_range":json.dumps({"since":source.comparison_start_date,"until":source.comparison_end_date}),
                "access_token":f"{meta_access_token}"
            }
        }
        response = requests.get(api, params=compare_params["meta"], timeout=120)
        body = response.json()
        if body.get("error"):
            err = body["error"]
            raise RuntimeError(
                f"Meta Graph API error: {err.get('message', err)} (type={err.get('type')} code={err.get('code')})"
            )
        rows = body.get("data") or []
        if not rows:
            # No rows in range (no delivery / no permission scope) — same as LinkedIn empty elements.
            return 0.0, 0.0, 0.0
        total_spend = total_imp = total_clk = 0.0
        for row in rows:
            total_spend += float(row.get("spend") or 0)
            total_imp += float(row.get("impressions") or 0)
            total_clk += float(row.get("clicks") or 0)
        return total_spend, total_imp, total_clk