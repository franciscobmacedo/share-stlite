const isObjectEmpty = (objectName) => {
  return Object.keys(objectName).length === 0;
};

const mountStlite = (files, requirements) => {
    sourceCodeButton = document.getElementById("source-code-button");
  if (isObjectEmpty(files)) {
    stlite.mount(
      `import streamlit as st\nst.write("Stlite - streamlit in the browser")\nst.write("Ensure you have the correct url setup.")`,
      document.getElementById("root")
    );
    sourceCodeButton.style.display = "none";
    return;
  } else {
    const entryPointName = Object.keys(files)[0];
    const entryPointUrl = files[entryPointName]['url'];
    stlite.mount(
      {
        requirements: requirements, // Packages to install
        entrypoint: entryPointName, // The target file of the `streamlit run` command - use the first file present
        files: files,
      },
      document.getElementById("root")
    );
    sourceCodeButton.href = entryPointUrl;
  }
  
};

const queryString = window.location.search;
const urlParams = new URLSearchParams(queryString);
const files = urlParams
  .getAll("url")
  .reduce(
    (a, url) => ({ ...a, [new URL(url).pathname.split("/").pop()]: { url } }),
    {}
  );
const requirements = urlParams.getAll("req");

mountStlite(files, requirements);
