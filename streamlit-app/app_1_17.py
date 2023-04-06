import numpy
import plotly.graph_objs as go
import streamlit as st
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import pandas as pd
from thirdai import bolt


model_path = "1bn_name_ctg_keywords_4gram.bolt"
data_path = "processed_recipes_3.csv"
# key Qeury string for model
QUERY = 'Name'
annotation = 'On'

@st.experimental_singleton
class Model:
    def __init__(self, model_path, data_path):
        self.model = bolt.UniversalDeepTransformer.load(model_path)
        self.data = pd.read_csv(data_path)

    def process_query(self, query):
        query = query.replace('\n', ' ').strip()
        query = ' '.join([query[i :i + 4] for i in range(len(query) - 3)])
        return query

food_udt = Model(model_path, data_path)
def get_embeddings_and_legend(user_input, topn):
    legend = []
    temp = []
    for k in range(len(user_input)) :
        query = user_input[k].lower()
        query = food_udt.process_query(query)
        cashew = food_udt.model.embedding_representation({QUERY : query})
        scores = food_udt.model.predict({QUERY : query.lower()})
        sorted_ids = scores.argsort()[-topn :][: :-1]
        temp.append(cashew)
        legend.append(user_input[k])
        for id in sorted_ids :
            temp.append(food_udt.model.get_entity_embedding(int(food_udt.model.class_name(id))))
            legend.append(food_udt.data.iloc[id][QUERY])
    temp = numpy.array(temp)
    return temp, legend
def display_scatterplot_3D(emb, user_input, legend, annotation='On', dim_red = 'PCA', perplexity = 0.0, learning_rate = 0, iteration = 0, topn=0):
    label = legend
    label_dict = dict([(y, x + 1) for x, y in enumerate(set(label))])
    if dim_red == 'PCA':
        three_dim = PCA(random_state=0).fit_transform(emb)[:,:3]
    else:
        three_dim = TSNE(n_components = 3, random_state=0, perplexity = min(perplexity, topn), learning_rate = learning_rate, n_iter = iteration).fit_transform(emb)[:,:3]

    color = 'blue'
    quiver = go.Cone(
        x = [0,0,0], 
        y = [0,0,0],
        z = [0,0,0],
        u = [1.5,0,0],
        v = [0,1.5,0],
        w = [0,0,1.5],
        anchor = "tail",
        colorscale = [[0, color] , [1, color]],
        showscale = False
        )
    data = [quiver]
    count = 0
    for i in range (len(user_input)):
                trace = go.Scatter3d(
                    x = three_dim[count:count+topn,0],
                    y = three_dim[count:count+topn,1],  
                    z = three_dim[count:count+topn,2],
                    text = legend[count:count+topn] if annotation == 'On' else '',
                    name = user_input[i],
                    textposition = "top center",
                    textfont_size = 30,
                    mode = 'markers+text',
                    marker = {
                        'size': 10,
                        'opacity': 0.8,
                        'color': 2
                    }
       
                )
                data.append(trace)
                count = count+topn
    layout = go.Layout(
        margin = {'l': 0, 'r': 0, 'b': 0, 't': 0},
        showlegend=True,
        legend=dict(
        x=1,
        y=0.5,
        font=dict(
            family="Courier New",
            size=25,
            color="black"
        )),
        font = dict(
            family = " Courier New ",
            size = 15),
        autosize = False,
        width = 1000,
        height = 1000
        )
    plot_figure = go.Figure(data = data, layout = layout)
    st.plotly_chart(plot_figure)


def display_scatterplot_2D(emb, user_input, legend, annotation='On', dim_red = 'PCA', perplexity = 0.0, learning_rate = 0, iteration = 0, topn=0):
    label = legend
    label_dict = dict([(y, x + 1) for x, y in enumerate(set(label))])
    color_map = [label_dict[x] for x in label]
    if dim_red == 'PCA':
        two_dim = PCA(random_state=0).fit_transform(emb)[:,:2]
    else:
        two_dim = TSNE(random_state=0, perplexity = min(perplexity, topn), learning_rate = learning_rate, n_iter = iteration).fit_transform(emb)[:,:2]
    data = []
    count = 0

    for i in range(len(user_input)) :
        trace = go.Scatter(
            x = two_dim[count:count+topn+1,0],
            y = two_dim[count:count+topn+1,1],
            text = legend[count:count+topn+1] if annotation == 'On' else '',
            name = user_input[i],
            textposition = "top center",
            textfont_size = 20,
            mode = 'markers+text',
            marker = {
                'size': 15,
                'opacity': 0.8,
                'color': 2
            }
        )
        data.append(trace)
        count = count+topn+1
    layout = go.Layout(
        margin = {'l': 0, 'r': 0, 'b': 0, 't': 0},
        showlegend=True,
        hoverlabel=dict(
            bgcolor="white", 
            font_size=20, 
            font_family="Courier New"),
        legend=dict(
        x=1,
        y=0.5,
        font=dict(
            family="Courier New",
            size=25,
            color="black"
        )),
        font = dict(
            family = " Courier New ",
            size = 15),
        autosize = False,
        width = 1000,
        height = 1000
        )
    plot_figure = go.Figure(data = data, layout = layout)
    st.plotly_chart(plot_figure)

dim_red = st.sidebar.selectbox(
 'Select method for visualization',
 ('PCA','TSNE'))
dimension = st.sidebar.radio(
     "Select the dimension of the visualization",
     ('2-D', '3-D'))
user_input = st.sidebar.text_input("Enter the query you wish to explore. If you have multiple queries, separate them using a comma (,)",'palak paneer, kofta, basil pasta')
top_n = st.sidebar.slider('Select the top K results associated with the input query you want to visualize ',
    5, 50, (5))

if dim_red == 'TSNE':
    learning_rate = st.sidebar.slider('Adjust the learning rate',
    10, 500, (10))

    iteration = st.sidebar.slider('Adjust the number of iteration',
    250, 1000, (350))

    perplexity = st.sidebar.slider(
        'Adjust the perplexity. perplexity is to choose number of neighours assosiation should be less than top K',
        5, 50, (top_n))
    
else:
    perplexity = 0
    learning_rate = 0
    iteration = 0    

if user_input != '':
    user_input = [x.strip() for x in user_input.split(',')]


st.title('ThirdAI Embedding Visualization')
if user_input != "":
    emb, legend = get_embeddings_and_legend(user_input, top_n)
    if dimension == '2-D':
        st.write('To access more information about each point on the visualization, hover over them or click the expand symbol in the top right corner to enlarge it.')
        display_scatterplot_2D(emb, user_input, legend, annotation, dim_red, perplexity, learning_rate, iteration, top_n)
    else:
        st.write('To access more information about each point on the visualization, hover over them or click the expand symbol in the top right corner to enlarge it.')
        display_scatterplot_3D(emb, user_input, legend, annotation, dim_red, perplexity, learning_rate, iteration, top_n)
