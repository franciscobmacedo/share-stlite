import json
import streamlit as st
from urllib.parse import urlparse
from pyodide.http import open_url


st.header('Search for your stlite apps')

st.write(
    """
 paste the url for the folder containing your files (python files and/or
        requirements.txt) or just an app python file.
"""
)

BASE_URL = "https://franciscobmacedo.github.io/share-stlite/"


def main():
    url = st.text_input("github url:")
    if url:
        files, requirements_file = get_files(url)
        build_form(files, requirements_file)

def get_files(url: str):
    path_segments = urlparse(url).path.split("/")
    user = path_segments[1];
    repo = path_segments[2];
    directory_path_segments = path_segments[5:];
    inner_directory_path = "/".join(directory_path_segments)

    api_url = f"https://api.github.com/repos/{user}/{repo}/contents/{inner_directory_path}"
    data = open_url(api_url)
    content = json.loads(data.read())

    files = {}
    requirements_file = None

    if isinstance(content, dict) and content['type'] == "file" and content['name'].endswith(".py"):
        files[content['name']] = content
    else:
        for item in content:
            if item['type'] == "file" and item['name'].endswith(".py"):
                files[item['name']] = item
            if item['type'] == "file" and item['name'] == "requirements.txt":
                requirements_file = item

    return files, requirements_file


def build_form(files, requirements_file):
    include_requirements = requirements_file is not None
    other_files = []

    st.header("1 - Entrypoint")
    entrypoint_filename = st.radio(
        "Choose your app's entrypoint file 👇",
        options=files,
    )
    
    st.markdown('#')
    st.header("2 - Requirements")
    if requirements_file:
        st.write('We found a "requirements.txt" in your directory. Do you want to include it?')
        include_requirements = st.checkbox('include "requirements.txt"', value=include_requirements)
    else:
        st.warning('It is not possible to detect a "requirements.txt" file. If this is not expected, ensure your url points to a directory and not a file.', icon="⚠️")

    if len(files) > 1:
        other_filenames = [f for f in files if f != entrypoint_filename]
        st.header("3 - Other files")
        st.write('We found other files in this directory. Which ones should we include?')
        selected_other_filename = st.multiselect(
            'select files you want to include',
            other_filenames,
            other_filenames)
        other_files = [files[f] for f in selected_other_filename]
    st.markdown('#')

    app_url = build_app_url(files[entrypoint_filename], other_files, include_requirements, requirements_file)

    st.markdown(f"[launch app]({app_url}) ↗️", unsafe_allow_html=True)



def build_app_url(entrypoint_file, other_files, include_requirements, requirements_file):
    url = f'?url={entrypoint_file["download_url"]}'
    
    if other_files:
        files_urls = [f["download_url"] for f in other_files]
        url = f"{url}&url={'&url='.join(files_urls)}"


    if include_requirements and requirements_file:
        data = open_url(requirements_file['download_url'])
        requirements = [str(r).strip() for r in data.read().split()]
        url = f"{url}&req={'&req='.join(requirements)}"

    return f"{BASE_URL}{url}"



main()