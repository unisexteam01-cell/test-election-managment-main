**Deploying backend to Fly.io (automatic on push to `main`)**

This repository includes a GitHub Actions workflow that will deploy the `backend/` service to Fly.io whenever you push to `main`.

Files added:
- `backend/fly.toml` — Fly.io app configuration (uses `backend/Dockerfile`).
- `.github/workflows/deploy-fly.yml` — GitHub Actions workflow that runs `flyctl deploy` on push to `main`.

Required setup steps (one-time):

1. Install Fly CLI locally and create an app (optional but recommended):
   ```bash
   brew install flyctl
   fly auth login
   # Launch interactively (create app and generate fly.toml) OR create app via web UI
   fly apps create election-backend --org personal
   ```

2. In the Fly dashboard or via `flyctl`, set app-level secrets OR use the GitHub Actions workflow to set them during CI. Recommended secrets (store in GitHub repository secrets):
   - `FLY_API_TOKEN` — Fly API token (create from https://fly.io/account/tokens)
   - `FLY_APP_NAME` — The Fly app name (e.g. `election-backend`)
   - `MONGO_URL` — Your MongoDB Atlas connection string (URL-encode password if necessary)
   - `DB_NAME` — Database name (e.g. `test-election`)
   - `JWT_SECRET_KEY` — Strong JWT secret for production

3. Add the above secrets to your GitHub repository (Settings → Secrets → Actions).

How the workflow works:
- On push to `main`, GitHub Actions runs `flyctl deploy --config backend/fly.toml --app $FLY_APP_NAME --remote-only`.
- Before deploy the workflow runs `flyctl secrets set` to write `MONGO_URL`, `DB_NAME`, and `JWT_SECRET_KEY` into the Fly app's secret store.

Notes & troubleshooting:
- If the workflow fails because `flyctl` cannot find the app, ensure `FLY_APP_NAME` is correct and that `FLY_API_TOKEN` has access to the app.
- If your MongoDB Atlas cluster restricts IPs, you may need to allow Fly's outbound IP ranges or temporarily open access (0.0.0.0/0) during deploy/testing.
- The `backend/Dockerfile` exposes port `8000`; Fly sets `$PORT` automatically. If you want to use the environment variable, update `CMD` in `Dockerfile` to use `$PORT`.

Custom domains, monitoring and scale are managed through the Fly dashboard.

If you'd like, I can also:
- Create a GitHub Actions workflow for Google Cloud Run instead (requires GCP service account secret), or
- Create a `render.yaml` and a Render deploy pipeline instead.
