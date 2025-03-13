import pandas as pd
from models import DependencyModel
def to_markdown(dep :DependencyModel):
    cols= ','.join(dep.data_columns)
    markdown_df=pd.DataFrame(dep.pandas_dataframe).head(5).to_markdown()
    
    return f"COLUMNS :{cols}\n SAMPLE_DATA:\n {markdown_df}"