const isObjectEmpty = (objectName) => {
  return Object.keys(objectName).length === 0;
};

function convertRawToGitHubURL(rawURL) {
  const url = new URL(rawURL);
  const pathSegments = url.pathname.split("/");

  const user = pathSegments[1];
  const repo = pathSegments[2];
  const branch = pathSegments[3];
  const filePath = pathSegments.slice(4).join("/");
  const githubURL = `https://github.com/${user}/${repo}/blob/${branch}/${filePath}`;
  return githubURL;
}

const mountStlite = (files, requirements) => {
  appContainer = document.getElementById("app-container");
  defaultContainer = document.getElementById("default-container");
  sourceCodeButton = document.getElementById("source-code-button");
  if (isObjectEmpty(files)) {
    appContainer.style.display = "none";
    defaultContainer.style.display = "block";
    return;
  }
  defaultContainer.style.display = "none";
  appContainer.style.display = "block";

  const entryPointName = Object.keys(files)[0];
  const entryPointUrl = files[entryPointName]["url"];
  stlite.mount(
    {
      requirements: requirements, // Packages to install
      entrypoint: entryPointName, // The target file of the `streamlit run` command - use the first file present
      files: files,
    },
    document.getElementById("root")
  );
  sourceCodeButton.href = convertRawToGitHubURL(entryPointUrl);
};

const queryString = window.location.search;
const urlParams = new URLSearchParams(queryString);
const files = urlParams.getAll("url").reduce((a, url) => (
  { ...a, [new URL(url).pathname.split("/").pop()]: { url } }
), {});
const requirements = urlParams.getAll("req");

mountStlite(files, requirements);
