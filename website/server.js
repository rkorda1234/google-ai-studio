import express from 'express';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const port = parseInt(process.env.PORT) || 3000;
const host = '0.0.0.0';

console.log(`Starting server configuration. Target Port: ${port}`);

const distPath = path.join(__dirname, 'dist');

// Check if build artifacts exist
if (!fs.existsSync(distPath)) {
  console.warn('WARNING: "dist" directory not found. On Cloud Run, this means the build step failed or did not output to "dist".');
} else {
  console.log(`Serving static files from: ${distPath}`);
}

app.use(express.static(distPath));

// Health check endpoint for Cloud Run
app.get('/health', (req, res) => {
  res.status(200).send('OK');
});

// Wildcard route for SPA
app.get('*', (req, res) => {
  const indexPath = path.join(distPath, 'index.html');
  if (fs.existsSync(indexPath)) {
    res.sendFile(indexPath);
  } else {
    res.status(500).send('Application loading...');
  }
});

const server = app.listen(port, host, () => {
  console.log(`Marketingverse server listening on http://${host}:${port}`);
});

process.on('SIGTERM', () => {
  console.log('SIGTERM received, shutting down gracefully.');
  server.close(() => {
    console.log('Server closed.');
    process.exit(0);
  });
});