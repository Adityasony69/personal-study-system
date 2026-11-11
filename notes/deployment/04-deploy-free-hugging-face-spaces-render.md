# Deploy free: Hugging Face Spaces and Render

Goal: get the Iris API from the earlier notes onto a public URL for free. Two good options for beginners.

> **Honest test status:** deploying needs your accounts, so I could not do it from here. Tested locally: the app boots with `uvicorn`, `/health` returns `{"status":"ok"}`, `/docs` returns 200, and the pinned `requirements.txt` installs cleanly. The platform settings below are from how these services work at the time of writing. Free-tier limits change, so check each site's pricing page.

## Pick one
| | Hugging Face Spaces | Render |
|---|---|---|
| Best for | ML demos, Gradio/Streamlit, Docker apps | Normal web APIs |
| How it deploys | Push files (git) to a Space repo | Connects to your GitHub repo, auto-deploys on push |
| Needs Docker? | Optional (Docker SDK), or use Gradio/Streamlit | No, it builds from `requirements.txt` |
| Free-tier catch | Sleeps when idle, small CPU | Sleeps after ~15 min idle, first request after sleep takes ~30-60 s |

Both free tiers **sleep** and have no persistent disk. Fine for a portfolio demo, not for real traffic.

## Before either: make the repo deploy-ready
1. Code and `requirements.txt` committed (see the FastAPI and Docker notes).
2. The app must **read the port from the environment** on platforms that tell you one (Render sets `PORT`).
3. The model must exist at runtime. Easiest: commit a small `model.joblib`, or run `train.py` in the build step.
4. No secrets in the repo.

---

## Option A: Hugging Face Spaces (Docker)

1. Make a free account at huggingface.co, then **New Space**. Choose SDK **Docker**, hardware **CPU basic (free)**.
2. A Space is a git repo. Clone it and copy your files in:
```bash
git clone https://huggingface.co/spaces/YOUR_USER/iris-api
cd iris-api
# copy main.py train.py requirements.txt Dockerfile here
```
3. The `README.md` at the top of the Space must start with this settings block:
```yaml
---
title: Iris API
emoji: 🌸
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
---
```
4. Spaces expects your app on port **7860** (set above). Change the last two lines of the Dockerfile:
```dockerfile
EXPOSE 7860
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
```
Spaces runs containers as user id 1000, which is why the Docker note created `appuser` with `-u 1000`.
5. Push:
```bash
git add .
git commit -m "Deploy"
git push
```
The Space page shows **Building**, then **Running**. Your API lives at `https://YOUR_USER-iris-api.hf.space` (docs at `/docs`).
```bash
curl https://YOUR_USER-iris-api.hf.space/health
```

**Even easier for ML demos:** skip FastAPI and use Gradio. Choose SDK **Gradio**, add `app.py` with a Gradio interface and a `requirements.txt`. Spaces runs it for you with no Dockerfile.

---

## Option B: Render (no Docker)

1. Push your project to a GitHub repo.
2. At render.com sign in with GitHub, **New**, **Web Service**, pick the repo.
3. Fill the form:

| Field | Value |
|---|---|
| Runtime | Python 3 |
| Build Command | `pip install -r requirements.txt && python train.py` |
| Start Command | `uvicorn main:app --host 0.0.0.0 --port $PORT` |
| Instance type | Free |
| Health Check Path | `/health` |

4. Set the Python version with an environment variable `PYTHON_VERSION` = `3.12.9` (Render's default may be different).
5. **Create Web Service.** Watch the log; when it says the service is live you get `https://your-name.onrender.com`.
6. Every `git push` to the connected branch redeploys automatically.

Optional, keep the settings in the repo with a `render.yaml`:
```yaml
services:
  - type: web
    name: iris-api
    runtime: python
    plan: free
    buildCommand: pip install -r requirements.txt && python train.py
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    healthCheckPath: /health
    envVars:
      - key: PYTHON_VERSION
        value: 3.12.9
```

---

## After it is live
- Open `/docs` on your public URL and try `/predict`.
- Put the URL in your README and portfolio.
- First request after idle is slow (cold start). Mention it so nobody thinks it is broken.
- Add the CI workflow from the previous note so only passing code reaches the deploy branch.
- Watch the logs (Render: Logs tab; Spaces: Logs on the Space page) when something fails.

## Mistakes to avoid
- Listening on `127.0.0.1` or a fixed port when the platform assigns one. Use `0.0.0.0` and `$PORT` (Render) or 7860 (Spaces).
- Forgetting `train.py` in the build, so `model.joblib` is missing at startup and the app crashes.
- Heavy libraries (full PyTorch) on a small free instance: out-of-memory crash. Keep models small.
- Committing secrets. Use the platform's secret / environment variable settings.
- Saving user uploads to disk and expecting them to persist. Free disks are wiped on restart.

## Check yourself
- Why do free services feel slow on the first request?
- Where does Render tell your app which port to use?
- Which port does a Docker Space expect, and where do you declare it?
- Why must the model file exist before the server starts?
