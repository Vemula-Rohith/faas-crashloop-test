// Post-ready crash-loop test function for Tower FaaS (#15 degraded-health).
// Listens on PORT (so Knative marks it Ready -> function goes 'running'), serves
// normal traffic, then exits non-zero after a delay so kubelet restarts it into
// CrashLoopBackOff *after* it was Ready. GET /healthz stays 200 for readiness.
const http = require('http');
const port = process.env.PORT || 8080;
const CRASH_AFTER_MS = Number(process.env.CRASH_AFTER_MS || 30000);

const server = http.createServer((req, res) => {
  if (req.url === '/crash') { console.error('explicit /crash requested'); process.exit(1); }
  res.writeHead(200, { 'content-type': 'text/plain' });
  res.end('ok\n');
});
server.listen(port, () => console.log(`listening on ${port}; will crash in ${CRASH_AFTER_MS}ms`));

// Delayed post-ready crash: long enough to pass readiness and reach 'running'.
setTimeout(() => { console.error('simulated post-ready crash (exit 1)'); process.exit(1); }, CRASH_AFTER_MS);
