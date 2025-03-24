/**
 * Utility functions for handling file paths with GitHub Pages compatibility
 */

/**
 * Gets the base path for the application, considering GitHub Pages deployment
 * @returns {string} The base path
 */
export function getBasePath() {
  return import.meta.env?.BASE_URL || "";
}

/**
 * Generates a data file path that works in both development and GitHub Pages
 * @param {string} filename - The name of the data file (without directory)
 * @returns {string} The complete path to the data file
 */
export function getDataPath(filename) {
  const basePath = getBasePath();
  // Ensure proper path construction without double slashes
  const dataPath = basePath ? `${basePath.replace(/\/$/, "")}/data/` : "data/";
  return `${dataPath}${filename}`;
}

/**
 * Handles paths that may come from props (like in theme_circle_pack.svelte)
 * @param {string} path - The path which may start with "/"
 * @returns {string} The path with proper base path handling
 */
export function getFullPath(path) {
  const basePath = getBasePath();

  // If path starts with /, handle with base path
  if (path.startsWith("/")) {
    return basePath
      ? `${basePath.replace(/\/$/, "")}${path}`
      : path.substring(1);
  }

  // Otherwise return the path as is
  return path;
}
