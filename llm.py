import ollama
import json
from models import PlotResponse,ModelResponse,QueryResponse,TextResponse
from pydantic_ai import Agent,capture_run_messages,UnexpectedModelBehavior,RunContext
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.exceptions import UsageLimitExceeded
from pydantic_ai.usage import UsageLimits
from pydantic import  ValidationError
import pandas as pd
class CSVAnalysisModel:
    def __init__(self, model_name: str = "llama3.1"):
        self.df = None
        self.model_name = model_name
        self._current_context = None
        
    def load_data(self, dataframe: pd.DataFrame):
        """Ingest CSV data for analysis"""
        self.df = dataframe
        self._current_context = self._create_data_context()

    def _create_data_context(self) -> str:
        """Create structured data context for LLM prompts"""
        if self.df is None:
            return ""
            
        return (
            "[DATA DESCRIPTION]\n"
            f"Dataset Columns:\n{self.df.columns.tolist()}\n\n"
            f"Sample Data (first 3 rows):\n{self.df.head(3).to_string()}"
        )

    def _build_llm_prompt(self, question: str) -> str:
        """Construct structured prompt for LLM"""
        return f"""
        I want you to act as a CSV data analysis model whose purpose is to returing the response in the following way mentioned before.
        ## CONTEXT:
        {self._current_context}
        
        ## AVAILABLE RESPONSE TYPE:
        1. TextResponse - For explanations and summaries
        2. QueryResponse - To filter/query the dataset
        3. PlotInstruction - For data visualization
        
        ## USER QUESTION: 
        {question}

        ## INSTRUCTIONS:
        1. Create a list responses according to given instruction below be strict with the response structure.
        2. Give only the JSON Response in output nothing else
        3. Write the pandas query strictly according to the dataframe columns provided
        :

         
        ### TextResponse structure:
        ```        
        {{
            "type": "text",
            "title": "Title",  
            "content": "Your text here"
        }}
        ```
        
        ### QueryResponse structure:
        ```
        {{
            "type": "query",
            "title": " Title",
            "content": " Description",
            "pandas_query": "sales > 100 and region == 'West'",  // Valid df.query() string
            "columns": ["product", "sales"],
            "head": 5,      //cab be null
            "sorted_columns_ascending": [["sales", false]]                  
        }}
        ```
        ### PlotResponse structure:
       ``` 
        {{
            "type": "plot",
            "title": " Title",  
            "content": " Description",
            "plot_type": "hist | scatter | line | bar | box",
            "x_column": "column_name",  
            "y_columns": ["col1", "col2"]
        }}
        ```

    ## EXAMPLE OF RESPONSE:
    ```
        {{
        "data": [
                {{
                "type": "text",
                "content": "Analyzing sales data trends..."
                }},
                {{
                "type": "query",
                "title": "Title",
                "content": "Description",
                "pandas_query": "sales > 100 and region == 'West'",  
                "columns": ["product", "sales"],
                "head": 5,
                "count": 10,
                "sorted_columns_ascending": [["sales", false]] 
                }}
            ]
        }}
    ```
        """

    def parse_llm_response(self, raw_response: str) -> ModelResponse:
        """Parse and validate LLM response"""
        try:
            response_data = json.loads(raw_response)
            text_responses,query_responses,plot_responses=[],[],[]
            for response in response_data['data']:
                if response["type"] == "text":
                    text_response=TextResponse(**response)
                    text_responses.append(text_response)
                    print('text')
                elif response["type"] == "query":
                    query_response=QueryResponse(**response)
                    query_responses.append(query_response)
                    print('query')
                elif response["type"] == "plot":
                    plot_response=PlotResponse(**response)
                    plot_responses.append(plot_response)
                    print('plot')
                else:
                    raise ValidationError("Invalid response type")
            print('[DONE PARSING]')
            return ModelResponse(texts=text_responses,
                                 queries=query_responses,
                                 plots=plot_responses)
        except (KeyError, json.JSONDecodeError, ValidationError) as e:
            print(f"Failed to parse response: {str(e)}")
            return None


    def process_question(self, question: str) -> ModelResponse:
        """Main analysis pipeline"""
        if self.df is None:
            raise ValueError("No data loaded")

        prompt = self._build_llm_prompt(question)
        print(prompt)
        # Get LLM response
        response = ollama.generate(
            model=self.model_name,
            prompt=prompt,
            format='json',
            options={'temperature': 0.1}
        )
        print(f"""
=====================================
              {response['response']}
=====================================""")
        # Parse and return structured response
        return self.parse_llm_response(response['response'])
    
if __name__ == "__main__":
    # Initialize model
    model = CSVAnalysisModel()
    
    # Sample data
    df = pd.DataFrame({
        'age': [25, 30, 35, 40, 45],
        'salary': [50000, 60000, 75000, 90000, 110000]
    })
    model.load_data(df)

    # Process query
    question = "Provide me the age first 5 people with imcome >65000 sorted by salaries in ascending order and draw a garph of income vs age"
    response=model.process_question(question=question)
    print(response.model_dump())
