var http = require('http');

function handleRequest(req, res) {
    console.log("Request received");
    res.writeHead(200, {'Content-Type': 'text/plain'});
    res.end('Hello, World!');
}

var server = http.createServer(handleRequest);

server.listen(8000, function(){
    console.log("Server listening on: http://localhost:8000");
});
