# Frontend Docker Standard

Create when `/frontend` exists:

```txt
frontend/Dockerfile
frontend/Dockerfile.prod
frontend/.dockerignore
```

Development container:

- Node LTS
- npm by default
- install dependencies with `npm install` or `npm ci` when a lockfile is present and appropriate
- bind dev server to `0.0.0.0`
- expose project dev port, usually `5173`
- support mounted source and hot reload

Production container:

- build static assets
- serve with nginx or another lightweight static server
- used for VPS/container platforms, not Vercel native deploy

Vercel should deploy from `/frontend` with `npm run build` and the framework output directory unless a documented package-manager exception exists.
