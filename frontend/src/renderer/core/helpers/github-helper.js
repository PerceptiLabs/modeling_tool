export const extractGithubUsernameFromURL = (urlString) => {
    if (!urlString) { return; }

    const regexpExpression = /github\.com\/(\w*)\/(\w*)/;
    const tokens = urlString.match(regexpExpression);

    if (!tokens || tokens.length < 2) { return; }

    return tokens[1] || '';
}