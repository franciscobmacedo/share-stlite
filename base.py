import json
import streamlit as st
from urllib.parse import urlparse
from pyodide.http import open_url
from streamlit_javascript import st_javascript
import pandas as pd


BASE_URL = "https://franciscobmacedo.github.io/share-stlite/"
SAVED_APPS_KEY = "saved_apps4"

def get_from_local_storage(k):
    v = st_javascript(
        f"JSON.parse(localStorage.getItem('{k}'));"
    )
    return v or {}


def set_to_local_storage(k, v):
    jdata = json.dumps(v)
    st_javascript(
        f"localStorage.setItem('{k}', JSON.stringify({jdata}));"
    )

saved_apps = get_from_local_storage(SAVED_APPS_KEY)



st.header('Open a previously used stlite app')
for app in saved_apps.values():
    path_segments = urlparse(app['search_url']).path.split("/")
    st.markdown(f"""
        - `{app['entrypoint_filename']}` from `{app['search_url']}`
        [launch app]({app['url']}) ↗️
        """,
        unsafe_allow_html=True
    )

st.header('Search for your stlite apps')

st.write(
    """
- paste the url to a github folder that contains your files ( for example `https://github.com/example-user/example-repo/tree/main/app_dir`). 
- It can include both `python` and `requirements.txt` files.
- You can also paste an url that points to just the app's python file (for example `https://github.com/example-user/example-repo/tree/main/app_dir/app_file.py`).
"""
)



class Page:
    def __init__(self) -> None:
        self.search_url = None
        self.files = {}
        self.other_files = []
        
        self.requirements_file = None
        self.include_requirements = True
        self.entrypoint_filename = None

        self.app_url = None
        saved_apps = {}
    
    def build(self):
        self.search_url = st.text_input("github url:", placeholder='https://github.com/example-user/example-repo/tree/main/app_dir')
        if self.search_url:
            self.get_files()
            if self.files:
                self.build_form()
            else:
                st.warning('It is not possible to detect any python files!', icon="⚠️")

    def get_files(self):
        path_segments = urlparse(self.search_url).path.split("/")
        user = path_segments[1]
        repo = path_segments[2]
        directory_path_segments = path_segments[5:]
        inner_directory_path = "/".join(directory_path_segments)

        api_url = f"https://api.github.com/repos/{user}/{repo}/contents/{inner_directory_path}"
        data = open_url(api_url)
        content = json.loads(data.read())

        files = {}
        requirements_file = None
        if isinstance(content, dict):
            if content.get('type', None) == "file" and content.get('name', None).endswith(".py"):
                files[content['name']] = content
            else:
                return
        else:
            for item in content:
                if item.get('type', None) == "file" and item.get('name', "").endswith(".py"):
                    files[item['name']] = item
                if item['type'] == "file" and item['name'] == "requirements.txt":
                    requirements_file = item

        self.files = files
        self.requirements_file = requirements_file

    @property
    def entrypoint_file(self):
        if self.entrypoint_filename and self.files:
            return self.files[self.entrypoint_filename]
        return None



    def build_form(self):
       
        st.header("1 - Entrypoint")

        self.entrypoint_filename = st.radio(
            "Choose your app's entrypoint file 👇",
            options=self.files,
        )
        
        st.markdown('#')
        st.header("2 - Requirements")
        if self.requirements_file:
            st.write('We found a "requirements.txt" in your directory. Do you want to include it?')
            self.include_requirements = st.checkbox('include "requirements.txt"', value=self.requirements_file is not None)
        else:
            st.warning('It is not possible to detect a "requirements.txt" file. If this is not expected, ensure your url points to a directory and not a file.', icon="⚠️")

        if len(self.files) > 1:
            other_filenames = [f for f in self.files if f != entrypoint_filename]
            st.header("3 - Other files")
            st.write('We found other files in this directory. Which ones should we include?')
            selected_other_filenames = st.multiselect(
                'select files you want to include',
                other_filenames,
                other_filenames)
            self.other_files = [self.files[f] for f in selected_other_filenames]
        st.markdown('#')

        self.build_app_url()
        self.save_app()
        
        st.markdown(f"[launch app]({self.app_url}) ↗️", unsafe_allow_html=True)

    def build_app_url(self):
        url = f'?url={self.entrypoint_file["download_url"]}'
        
        if self.other_files:
            files_urls = [f["download_url"] for f in self.other_files]
            url = f"{url}&url={'&url='.join(files_urls)}"


        if self.include_requirements and self.requirements_file:
            data = open_url(self.requirements_file['download_url'])
            requirements = [str(r).strip() for r in data.read().split()]
            url = f"{url}&req={'&req='.join(requirements)}"

        self.app_url = f"{BASE_URL}{url}"

    def save_app(self):
        if self.app_url:
            saved_apps[self.search_url] = {'url': self.app_url,
                                        'search_url': self.search_url,
                                        'entrypoint_filename':  self.entrypoint_filename,
                                    }
        set_to_local_storage(SAVED_APPS_KEY, saved_apps)
    



Page().build()