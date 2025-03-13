import gradio as gr
import pandas as pd
import matplotlib.pyplot as plt
from analyser import Analyser
from plot_manager import PlotManager
from PIL import Image
from models import PlotResponse
from llm import CSVAnalysisModel

import io

# Global variable to store the uploaded DataFrame
df = None  





#PLOTTING SECTION OPERATIONS
def update_plotting_section(plot_manager):
    if plot_manager is None:
        return None,None,None
    return plot_manager.get_cols(),plot_manager.get_cols(),plot_manager.plots_list


def provide_graph(plot_manager:PlotManager=None,
                  checkboxes=None,
                  x_dropdown=None,
                  y_dropdown=None,
               
                  ):
    if not plot_manager:
        return None
    try:

        if checkboxes is None :
            raise ValueError("Please choose a Value for the plot type")

        plot_response=PlotResponse(type='plot',plot_type=checkboxes,x_column=x_dropdown,y_columns=y_dropdown)
        print(plot_response)
        figure=plot_manager.plot_graph([plot_response])
        buf = io.BytesIO()
        figure.savefig(buf, format="png")  # Save plot as a PNG in memory
        buf.seek(0)
        img = Image.open(buf) 
        return img
    except Exception as e:
        print(f"ERROR:{e}")
        return None
    




# Function to load CSV and extract column names
def load_csv(file_bytes):
    global df
    if not file_bytes:
        return ("Please upload a CSV file.",None,None ,None,None,None,None,None)# Read CSV from bytes
    df = pd.read_csv(io.BytesIO(file_bytes))
    analyser=Analyser(df=df)
    plot_manager= PlotManager(df=df)
    model=None
    model= CSVAnalysisModel()
    model.load_data(df)
    cols=df.columns.to_list()
    buffer = io.StringIO()
    df.info(buf=buffer)
    info_str = buffer.getvalue()
    buffer.close()
    

    buffer.close()
    return (  f"```\n{info_str}\n```",
             analyser,
             plot_manager,
             model,
             df,
             gr.Dropdown(choices=cols),
             gr.Dropdown(choices=cols),
             gr.Radio(choices= plot_manager.plots_list)
             )

def process_text(user_input:str=None,
                 model=None,
                 plot_manager:PlotManager=None,
                 analyser:Analyser=None):
    try:
        if any(v is None for v in (user_input,model, plot_manager, analyser)):
            return None ,None
        response= model.process_question(user_input)
        print("[GOT THE PROPER RESPONSE ]")
        output_text=[]
        try:
            for text in response.texts:
                header=f"### {text.title}"
                content=text.content
                output_text.append(header)
                output_text.append(content)
        except Exception as e:
            print(f'[ERROR]: in text -> {e}')



        try:
            for query in response.queries:
                header=f"### {query.title}"
                content=query.content
                output_text.append(header)
                output_text.append(content)
                output_text.append(analyser.process_query(query))
        except Exception as e:
                print(f'[ERROR]: in query -> {e}')
        try:
            for plot in response.plots:
                header=f"### {plot.title}"
                content=plot.content
                output_text.append(header)
                output_text.append(content)
        except Exception as e:
            print(f'[ERROR]: in plot -> {e}')

        print("GOING TO GENERATE FIGURES")
        figure=plot_manager.plot_graph(response.plots)
        print(f'[GOT THE FIGURE]: {figure}')
        if figure:
            buf = io.BytesIO()
            figure.savefig(buf, format="png")  # Save plot as a PNG in memory
            buf.seek(0)
            img = Image.open(buf) 
        else:
            img=None
        return '\n \n'.join(output_text),img
        
    except Exception as e:
        print(f"[ERROR]: {e}")
        return  None ,None
        



        

    

with gr.Blocks() as demo:
    with gr.Row():  
        with gr.Column(scale=1):
            gr.Markdown("# 📊 Data Columns")
            checkboxes = gr.Radio(choices=[], label="Select columns to plot", interactive=True)
            x_dropdown = gr.Dropdown([], label="Select X-Axis Column (for histogram choose column here)",scale=1,interactive=True)
            y_dropdown = gr.Dropdown([],multiselect=True, label="Select Y-Axis Column(s)",scale=1,interactive=True)
            plot_button = gr.Button("Plot")
            gr.Markdown("### Upload your CSV file:")
            file_input = gr.File(label="Upload CSV", type="binary",scale=0.5)
        with gr.Column(scale=2):
            gr.Markdown("### Plots:") 
            canvas_output = gr.Image(label="Matplotlib Plot",interactive=False)
            with gr.Column(scale=1):
                user_text = gr.Textbox(label="Enter text", placeholder="Type here...")
                submit_btn = gr.Button("Submit")
                status_output = gr.Markdown(label="Status")
        with gr.Column(scale=0.25):
                gr.Markdown("### WELCOME:") 
                text_output = gr.Markdown(label="Output")
                
                


#STATES
    analyser= gr.State(None)
    plot_manager= gr.State(None)
    dataframe= gr.State(None)
    model= gr.State(None)
#EVENT BINDINGS
    file_input.change(load_csv, inputs=file_input, outputs=[status_output, analyser,plot_manager,model,dataframe,x_dropdown,y_dropdown,checkboxes])
    plot_button.click(provide_graph,inputs=[plot_manager,checkboxes,x_dropdown,y_dropdown],outputs=[canvas_output])
    
    submit_btn.click(process_text, inputs=[user_text,model,plot_manager,analyser], outputs=[text_output,canvas_output])


demo.launch(debug=True)