const http = require('http');
const { execSync } = require('child_process');

const PORT = 8200;

const requestListener = (req, res) => {
    if (req.method === 'GET') {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        const response = {
            "IP address information": execSync("hostname -I").toString().trim(),
            "Running processes": execSync("ps -ax").toString(),
            "Available disk space": execSync("df -h /").toString(),
            "Time since last boot": execSync("uptime -p").toString()
        };
        res.end(JSON.stringify(response));
    } else {
        res.writeHead(404, { 'Content-Type': 'text/plain' });
        res.end('Not Found');
    }
};


const server = http.createServer(requestListener);
server.listen(PORT, () => {
    console.log(`Service2 running on port ${PORT}`);
});