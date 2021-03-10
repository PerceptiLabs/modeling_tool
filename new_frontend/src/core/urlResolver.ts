/**
 * Create a promise that fetches a url from a file on the server or returns a default URLdetermined by the following precedence:
 * 1. the <svc>_url file
 * 2. hard-coded localhost:<port>
 *
 * @param urlPath
 * @param defaultUrl
 */

export default async function(
  urlPath: string,
  defaultUrl: string,
): Promise<string> {
  try {
    const res = await fetch(urlPath);
    const fetched = await res.text();
    if (!fetched) {
      return defaultUrl;
    }
    if (fetched.includes("html")) {
      return defaultUrl;
    }
    return fetched;
  } catch (e) {
    return defaultUrl;
  }
}
