const BASE_APP_FILES = {"base.py": {url: "https://raw.githubusercontent.com/franciscobmacedo/share-stlite/main/base.py"}}
const loadAppFromUrl = () => {
  console.log("loading app from url");
  const queryString = window.location.search;
  const urlParams = new URLSearchParams(queryString);
  const files = urlParams.getAll("url").reduce(
    (a, url) => ({
      ...a,
      [new URL(url).pathname.split("/").pop()]: { url },
    }),
    {}
  );
  const requirements = urlParams.getAll("req");
  if (Object.keys(files).length === 0) {
    mountStlite(BASE_APP_FILES, []);
    return
  }
  mountStlite(files, requirements);
};

const mountStlite = (files, requirements) => {
  console.log(files)
  console.log(requirements)
  const entryPointName = Object.keys(files)[0];
  stlite.mount(
    {
      requirements: requirements, // Packages to install
      entrypoint: entryPointName, // The target file of the `streamlit run` command - use the first file present
      files: files,
    },
    document.getElementById("root")
  );
};

loadAppFromUrl();
