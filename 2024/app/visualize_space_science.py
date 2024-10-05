import streamlit as st
import requests
import json
import plotly.graph_objs as go
import os
from PIL import Image
from glob2 import glob
import datetime

st.set_page_config(
    layout="wide",
)


# Custom CSS to increase the font size of the entire app
custom_css = """
    <style>
        /* Increase font size for all text elements */
        html, body, [class*="css"]  {
            font-size: 24px; /* You can adjust this size to your liking */
        }
    </style>
    """

# Inject the custom CSS
st.markdown(custom_css, unsafe_allow_html=True)



# Sidebar
st.title('Visualizing Space Science')
st.sidebar.image("./images/image.jpeg", width=250)
st.sidebar.title('Space Apps 2024')
st.sidebar.markdown('**Hikari Nova**: Inspired by the explosive power of a nova, a stellar light, a tiny child.')
st.sidebar.markdown('## Members:')
st.sidebar.markdown('Sandra Puentes')
st.sidebar.markdown('Luis Carlos Manrique')


# Functions

# asking for user input
@st.cache_data()
def get_metadata(OSD_ID):
    endpoint = 'https://osdr.nasa.gov/osdr/data/osd/meta/' + str(OSD_ID)
    result = requests.get(endpoint).json()
    if result['hits'] > 0:
        st.write('Successfully got metadata')

        filename = './files/OSD_' + str(OSD_ID) + '.json'
        with open(filename, 'w') as f:
            json.dump(result, f)
        return(result)
    else:
        st.write(f"Failed to get metadata for experiment {OSD_ID}")
        return None


def loading_data(OSD_ID):
    # Checking if experiment data already exists
    filename = './files/OSD_' + str(OSD_ID) + '.json'

    if os.path.exists(filename):
        with open(filename, 'r') as f:
            response_meta = json.load(f)

        st.write('Successfully loaded data')
    else:
        response_meta = get_metadata(OSD_ID)

        if response_meta is not None:
            # write dictionary to a text file
            with open(filename, 'w') as f:
                json.dump(response_meta, f)
        else:
            return None

    return response_meta

def extract_title(response_meta):
    return(response_meta['study']['OSD-' + str(OSD_ID)]['studies'][0]['title'])

def extract_description(response_meta):
    return(response_meta['study']['OSD-' + str(OSD_ID)]['studies'][0]['description'])

def extract_submission_date(response_meta):
    date = response_meta['study']['OSD-' + str(OSD_ID)]['studies'][0]['submissionDate']
    date_obj = datetime.datetime.strptime(date, "%d-%b-%Y")
    result = date_obj.strftime("%y%m%d")
    return(date, result)

def get_files(OSD_ID):
    endpoint = 'https://osdr.nasa.gov/osdr/data/osd/files/' + str(OSD_ID)
    response_files = requests.get(endpoint).json()
    files_json = response_files['studies']['OSD-' + str(OSD_ID)]['study_files']
    list_files = [files_json[n]['remote_url'] for n in range(len(files_json))]
    return list_files

def create_url(chosen_file):
    return 'https://osdr.nasa.gov' + chosen_file

def load_protocols(response_meta):
    if response_meta:
        protocols = response_meta['study']['OSD-' + str(OSD_ID)]['studies'][0]['protocols']
        all_protocols = [protocols[n]['description'] for n in range(len(protocols))]
        return(all_protocols)
    else:
        return None



OSD_ID = st.text_input("Enter experiment ID (e.g. 665):")

#tab0, tab1, tab2, tab3, tab4, tab5 = st.tabs(["Introduction", "General information", "Files", "Protocols", "Parameters", "Materials"])
tab1, tab0, tab2, tab3 = st.tabs(["General information", "Introduction", "Files", "Protocols"])

with tab1:
    if OSD_ID:
        st.markdown(f"## Collecting information for experiment: {OSD_ID}")
        try:
            response_meta = loading_data(OSD_ID)
            #st.write(response_meta)

            if response_meta:
                #st.write(response_meta)

                st.markdown(f"## Title:")
                st.write(extract_title(response_meta))

                st.markdown(f"## Submission Date:")
                date, result = extract_submission_date(response_meta)
                st.write(date)

                url = 'https://apod.nasa.gov/apod/ap' + result + '.html'
                st.markdown("[Picture of the day](%s)" % url)


                st.markdown(f"## Description:")
                st.write(extract_description(response_meta))

        except:
            st.write(f"Failed to get metadata for experiment {OSD_ID}")



with tab0:
    st.markdown("# Summary")

    filename = './files/OSD_' + str(OSD_ID) + '.mp3'
    if os.path.isfile(filename):
        st.header("Podcast")
        st.audio(filename, format="audio/mpeg", loop=True)
    #else:
    #    st.write("Coming soon")
    
    st.markdown("This page was made with L :heart: ve and Generative AI. Original Source NASA")

    col1, col2 = st.columns([2, 1])

    with col1:
        #if OSD_ID:
        if os.path.isfile('./files/chatgpt_' + str(OSD_ID) + '.json'):
            st.header("General questions")
            with open('./files/chatgpt_' + str(OSD_ID) + '.json', 'r') as f:
                response_chatgpt = json.load(f)
            
            # Loop through the dictionary and display each key in bold
            for key, value in response_chatgpt.items():
                st.markdown(f"<span style='color: red;'>**{key}**</span>: {value}", unsafe_allow_html=True)
        # else:
        #    st.write(f"Coming soon")

    with col2:
        #if OSD_ID:
        if os.path.isfile('./files/chatgpt_' + str(OSD_ID) + '.json'):
            st.header("A glimpse into the research")
            image_files = glob('*/OSD_' + str(OSD_ID) + '_*.jpeg')

            # Loop through each image and display it in Streamlit
            for image_file in image_files:
                img = Image.open(image_file)
                st.image(img, caption=None, use_column_width=True)
        # else:
        #    st.write(f"Coming soon")


with tab2:
    st.markdown("# Related files")

    if OSD_ID:
        if response_meta:
            list_files = get_files(OSD_ID)
            st.write(f'Number of files: {len(list_files)}')

    if st.button("Show Information", key='bt_files'):
        for url in list_files:
            st.write(f"[{url}]({create_url(url)})")
            st.write("")  # add an empty line


with tab3:
    st.markdown("# Information about protocols")

    if OSD_ID:
        if response_meta:
            list_protocols = load_protocols(response_meta)
            st.write(f'Number of protocols: {len(list_protocols)}')

    if st.button("Show Information", key='bt_protocols'):
        for protocol in list_protocols:
            st.write(protocol)
            st.write("")  # add an empty line

# with tab4:
#     st.markdown(f"# This is tab 4")

# with tab5:
#     st.markdown(f"# This is tab 5")

css = '''
<style>
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
    font-size:1rem;
    }
</style>
'''

st.markdown(css, unsafe_allow_html=True)