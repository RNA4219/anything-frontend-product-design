import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';

const port = Number(process.argv[2] ?? 8074);
if (!Number.isInteger(port) || port < 0 || port > 65535) throw new Error('Port must be an integer between 0 and 65535');
const assets = new Map([
  ['/', ['index.html', 'text/html; charset=utf-8']],
  ['/index.html', ['index.html', 'text/html; charset=utf-8']],
  ['/app.mjs', ['app.mjs', 'text/javascript; charset=utf-8']],
  ['/flow.mjs', ['flow.mjs', 'text/javascript; charset=utf-8']],
  ['/mock-service.mjs', ['mock-service.mjs', 'text/javascript; charset=utf-8']],
]);
const server = createServer(async (request, response) => {
  const asset = assets.get(new URL(request.url, 'http://localhost').pathname);
  if (!asset || !['GET', 'HEAD'].includes(request.method)) {
    response.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
    response.end('Not found');
    return;
  }
  try {
    const body = await readFile(new URL(asset[0], import.meta.url));
    response.writeHead(200, { 'Content-Type': asset[1], 'Cache-Control': 'no-store', 'X-Content-Type-Options': 'nosniff' });
    response.end(request.method === 'HEAD' ? undefined : body);
  } catch {
    response.writeHead(500, { 'Content-Type': 'text/plain; charset=utf-8' });
    response.end('Local asset could not be read');
  }
});
server.listen(port, '127.0.0.1', () => {
  console.log(`Booking change demo: http://127.0.0.1:${server.address().port}`);
});
