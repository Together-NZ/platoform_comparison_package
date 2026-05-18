from .comparison_bigquery import Comparison_bigquery
from .comparison_source import Comparison_source
from .utils.safe_divide import safe_divide
class ComparisonTrigger:
    def __init__(self,project_name:str,destination_table:str,table_name:str,source_name:str,start_date:str,end_date:str,
                 secret_name:str,project_id:str):
        self.project_name = project_name
        self.destination_table = destination_table
        self.table_name = table_name
        self.source_name = source_name
        self.start_date = start_date
        self.end_date = end_date
        self.secret_name = secret_name
        self.project_id = project_id
        self.dimension_filter = ""
    def compare_data_return(self):
        comparison_bigquery = Comparison_bigquery(project_name=self.project_name,destination_table=self.destination_table,table_name=self.table_name,source_name=self.source_name,start_date=self.start_date,end_date=self.end_date)
        comparison_source = Comparison_source(comparison_name=self.source_name,dimension_filter=self.dimension_filter,comparison_start_date=self.start_date,comparison_end_date=self.end_date,secret_name=self.secret_name,project_id=self.project_id)
        bq_data=comparison_bigquery.execute_command()
        source_data=comparison_source.get_comparison_data()

        return bq_data, source_data
    
    def compare_data(self):
        data = self.compare_data_return()
        bq_data = data[0]
        source_data = data[1]
        print(bq_data, source_data)
        media_cost_difference = safe_divide(bq_data[0] - float(source_data[0]),float(source_data[0]))
        impression_difference = safe_divide(bq_data[1] - float(source_data[1]),float(source_data[1]))
        click_difference = safe_divide(bq_data[2] - float(source_data[2]),float(source_data[2]))
        print(media_cost_difference, impression_difference, click_difference)
        if self.source_name == "meta":
            if abs(media_cost_difference) > 0.005 or abs(impression_difference) > 0.01:
                return False
            return True
        else:
            if abs(media_cost_difference) > 0.05 or abs(impression_difference) > 0.01 or abs(click_difference) > 0.01:
                return False
            return True
        
if __name__ == "__main__":
    comparison_trigger = ComparisonTrigger(project_name="uowaikato-main",destination_table="snapchat_transformed",table_name="snapchat",source_name="snapchat",start_date="2026-05-03",end_date="2026-05-11",secret_name="airflow-variables-meltano_uowaikato_main",project_id="739679429225")
    print(comparison_trigger.compare_data())
    
