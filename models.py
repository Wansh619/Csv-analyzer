from pydantic import BaseModel, ValidationError,Field
from typing import Optional, Literal, Union
import pandas as pd
from typing import Any

# --------------------------
# Response Models
# --------------------------

class DependencyModel(BaseModel):
    data_columns: list[str]
    pandas_dataframe: dict[str,Any]



class TextResponse(BaseModel):
    type: Literal['text']
    title: str
    content:str

class QueryResponse(BaseModel):
    type: Literal['query']
    title: Optional[str]=None
    content: Optional[str] =None
    pandas_query: str
    columns: Optional[list[str]] = None
    head:Optional[int]=None
    sorted_columns_ascending:Optional[list[tuple[str,Literal[True,False]]]]=None
    

class PlotResponse(BaseModel):
    type: Literal['plot']
    title: Optional[str]=None
    content: Optional[str] =None
    plot_type: Literal['hist', 'scatter', 'line', 'bar', 'box']
    x_column: Optional[str]=None
    y_columns: list[str]



class ModelResponse(BaseModel):
    texts:list[TextResponse]
    queries: list[QueryResponse]
    plots: list[PlotResponse]






