
from google.cloud import secretmanager
import json
import requests
from google.cloud import bigquery

client = bigquery.Client()

class Comparison_bigquery:
    def __init__(self,project_name:str,destination_table:str,table_name:str,source_name:str,start_date:str,end_date:str):
        self.project_name = project_name
        self.destination_table = destination_table
        self.table_name = table_name
        self.start_date = start_date
        self.end_date = end_date


    def execute_command(self):
        client = bigquery.Client(project=self.project_name)
        
            
        query = f"""
            SELECT SUM(media_cost) as media_cost, SUM(impressions) as impressions, SUM(clicks) as clicks
            FROM `{self.project_name}.{self.destination_table}.{self.table_name}`
            WHERE date BETWEEN '{self.start_date}' AND '{self.end_date}'
        """
        result = client.query(query).result()
        rows = list(result)
        print(f"row is {rows}")
        row = rows[0]
        media_cost = row[0] if row[0] is not None else 0
        impressions = row[1] if row[1] is not None else 0
        clicks = row[2] if row[2] is not None else 0
        return media_cost, impressions, clicks


