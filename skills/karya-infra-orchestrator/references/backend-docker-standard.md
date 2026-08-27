# Backend Docker Standard

Create when `/backend` exists:

```txt
backend/Dockerfile
backend/Dockerfile.prod
backend/.dockerignore
backend/entrypoint.sh
```

Development container:

- install Python dependencies
- expose `8000`
- run Django development server
- mount source code
- use environment variables

Production container:

- slim Python image
- install only runtime dependencies
- run migrations explicitly or through a controlled entrypoint
- collect static files when needed
- run gunicorn
- do not hardcode secrets

Container hosts may include VPS, Render, Railway, Fly.io or similar services.

