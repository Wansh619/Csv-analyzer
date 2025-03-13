#CONSISITS OF 2 CLASSES 

# ANALYSER
import pandas as pd
from models import QueryResponse

class Analyser:
    def __init__(self,df: pd.DataFrame =None):
        self.dataframe=df
        self.columns= df.columns
        self.num_rows,self.num_cols= df.shape[0], df.shape[1]
        print(f""" 
==================================================================
|                           ANALYSER                             |
|===============================|================================|
|                               |                                |
|           NUM ROWS            |          {self.num_rows}       |
|                               |                                |
|           NUM COLUMNS         |          {self.num_cols}       |
|                               |                                |
==================================================================
            """)
        self.dataframe.info()
        self.dataframe.describe()

    def process_query(self,query_response : QueryResponse=None)->str :
        try:
            print(self.dataframe.head(5))
            print(query_response)
            # query
            temp= self.dataframe.query(query_response.pandas_query)
            # sorting
            print(temp) 
            if query_response.sorted_columns_ascending:
                cols,asc=zip(*query_response.sorted_columns_ascending)
                temp=temp.sort_values(by=list(cols),ascending=list(asc))
            if query_response.head:
                temp= temp.head(query_response.head)
            temp=temp.loc[:,query_response.columns]
            print(temp.to_markdown())
            return temp.to_markdown()
            
        except Exception as e:
            print(e) 
            return ''



        

