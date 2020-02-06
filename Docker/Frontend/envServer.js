const http = require('http');
const url = require('url');

const port = 8081;

http.createServer(function (req, res) {

  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'OPTIONS, GET',
    'Access-Control-Max-Age': 2592000, // 30 days
    'Content-Type': 'application/json'
  };

  if (req.method === 'OPTIONS') {
    res.writeHead(204, headers);
    res.end();
    return;
  }

  if (['GET'].indexOf(req.method) > -1) {
    
    res.writeHead(200, headers);
    
    const url = req.url.replace(/\//g, '').toUpperCase();
    console.log('Request url', url);

    let envs;    
    if (process.env[url]) {
      envs = JSON.stringify(process.env[url]);
    } else {
      // for debugging purposes
      // envs = JSON.stringify(process.env);
      envs = JSON.stringify('');
    }

    res.end(envs);
    return;
  }

  res.writeHead(405, headers);
  res.end(`${req.method} is not allowed for the request.`);

}).listen(port, function() {
  console.log('Server listening on port', port);
}); 