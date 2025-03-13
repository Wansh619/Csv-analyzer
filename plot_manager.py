import matplotlib.pyplot as plt
from models import PlotResponse
import numpy as np
class PlotManager:
    def __init__(self,df, plots_list=['scatter','line','bar','hist'],figure_size=(8,6)):
        self.dataframe=df
        self.plots_list=plots_list
        self.figure_size=figure_size

    def get_cols(self):
        return self.dataframe.columns.tolist()
    
    def plot_graph(self,plot_response:list[PlotResponse] )->plt.Figure:
        try:
            
            num_plots = len(plot_response)  
            rows = int(np.ceil(num_plots ** 0.5))  
            cols = int(np.ceil(num_plots / rows)) 

            fig, axes = plt.subplots(rows, cols, figsize=(cols * 4, rows * 3))  
            if num_plots==1:
                axes = np.array([axes])  
            else:
                axes = axes.flatten()
            for id ,plot in enumerate(plot_response):
                print(f'PLOTTING plot { id} :: {plot}')
                x_axis=plot.x_column
                y_axis=plot.y_columns
                for y in y_axis:
                    if plot.plot_type == "line":
                        axes[id].plot(self.dataframe[x_axis], self.dataframe[y], linestyle="-", label=f"{x_axis},{y}(line)")
                    elif plot.plot_type == "scatter":
                        axes[id].scatter(self.dataframe[x_axis], self.dataframe[y], label=f"{x_axis},{y} (scatter)")
                    elif plot.plot_type == "hist":
                        axes[id].hist(self.dataframe[y], label=f"{y} (hist)")
                    elif plot.plot_type == "bar":
                        axes[id].bar(self.dataframe[x_axis], self.dataframe[y], width=0.7, alpha=0.7, label=f"{x_axis},{y} (bar)")
                axes[id].set_xlabel(x_axis)  # Set X-axis label
                axes[id].set_ylabel(', '.join(y_axis)) 
                axes[id].legend()

                axes[id].set_title(f"{plot.title if plot.title else str('')} ")
            plt.tight_layout()
            return fig
        except Exception as e:
            print(f'[ERROR GENRATION PLOT]: {e}')
            return None






    

        