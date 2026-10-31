# Hosting the POLLEN shot explorer (GitHub Pages)

Public repo: https://github.com/apalikodath-cloud/pollen-shot-explorer

- `main` holds the project source (built by `viz/explorer/export_public.ps1`).
- `gh-pages` holds the built site (built by `viz/explorer/build_site.py`, published by `viz/explorer/deploy_pages.ps1`).
- Live site: https://apalikodath-cloud.github.io/pollen-shot-explorer/

Note: the repo is public, so the model data in `data/` is public.

## Pages setting (once)

1. Open the repo > **Settings** > **Pages** (left sidebar).
2. Source: **Deploy from a branch**.
3. Branch: **gh-pages**, folder **/ (root)**.
4. Click **Save**. After about 1 minute the site is live.

## Update the site

1. `python -B viz/explorer/build_site.py` (writes `viz/explorer/site/`).
2. `powershell -File viz/explorer/deploy_pages.ps1` is a dry run; add `-Push` to publish
   (a normal commit on `gh-pages`, never a force push).

## Update the source on main

1. Commit the change in this repo.
2. `powershell -File viz/explorer/export_public.ps1` builds the clean public tree in
   `%LOCALAPPDATA%\pollen-shot-explorer-public` and commits it on a local `main` on top of the remote `main`.
   It leaves out internal tooling (`.af/`, `.claude/`, `CLAUDE.md`, `docs/handoff/`).
3. Check it, then rerun with `-Push` (a normal push to `main`, never a force push).

Alternatives for the site: Netlify Drop (drag the `site` folder onto app.netlify.com/drop); Cloudflare Pages
(connect a repo or upload the folder).
