# Docker your ML app

"It works on my machine" is the problem Docker solves. A **Docker image** is a frozen package: your code, Python, the exact libraries, and the model file. A **container** is a running copy of that image. Whoever runs it (your laptop, a server, a teammate) gets the same thing.

> **Honest test status:** Docker is not installed on the machine these notes were written on, so I could **not** run `docker build` or `docker run`. What I did test: the exact `requirements.txt` below installed into a clean virtual environment, and the app trained, started and passed its tests there. That is the same sequence the Dockerfile performs. Run the Docker commands yourself once and fix any typo before trusting them.

## Words
| Word | Plain meaning |
|---|---|
| Image | The frozen package, built once |
| Container | A running instance of an image. Start and stop many |
| Dockerfile | The text recipe for building an image |
| Layer | Each instruction in the Dockerfile; Docker caches them |
| Registry | A place to store images (Docker Hub, GitHub Container Registry) |

## Project layout
```
iris-api/
  main.py
  train.py
  test_main.py
  requirements.txt
  requirements-dev.txt
  Dockerfile
  .dockerignore
```

`requirements.txt` (runtime only; versions pinned):
```
fastapi==0.136.3
uvicorn[standard]==0.51.0
scikit-learn==1.9.1
joblib==1.6.0
pydantic==2.13.4
```
`requirements-dev.txt` (only for tests, kept out of the image):
```
pytest==9.2.0
httpx==0.28.1
```

## The Dockerfile
```dockerfile
FROM python:3.12-slim

WORKDIR /app

# 1) install dependencies first: this layer is cached until requirements.txt changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2) copy the code, then train so the model file is baked into the image
COPY main.py train.py ./
RUN python train.py

# 3) don't run as root (the model file is created by root, readable by everyone)
RUN useradd -m -u 1000 appuser
USER appuser

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Line by line:
- `FROM python:3.12-slim`: a small Python image. Much smaller than the default and fine for scikit-learn (it ships prebuilt wheels).
- Dependencies are copied and installed **before** the code. Code changes constantly, requirements rarely; this order means rebuilds skip the slow pip step.
- `RUN python train.py` bakes the model into the image so the container works with no extra files. For a bigger real model, copy or download a pre-trained file instead of training at build time.
- `USER appuser`: if someone breaks into the app they are not root.
- `--host 0.0.0.0` is **essential**. The default `127.0.0.1` means "only inside the container", so your browser could never reach it.
- `EXPOSE` is documentation only. The port is actually published with `-p`.

## `.dockerignore`
Keeps junk out of the build and keeps builds fast. Same idea as `.gitignore`.
```
__pycache__/
*.pyc
.venv/
venv/
.git/
.pytest_cache/
model.joblib
test_main.py
requirements-dev.txt
Dockerfile
```
(`model.joblib` is excluded because the image trains its own.)

## Build and run
```bash
docker build -t iris-api .
docker run --rm -p 8000:8000 iris-api
```
- `-t iris-api` names the image.
- `-p 8000:8000` maps `your-computer-port:container-port`.
- `--rm` deletes the container when it stops.

Then, from another terminal (same call I tested against the bare app):
```bash
curl http://127.0.0.1:8000/health
# {"status":"ok"}
```

## Everyday commands
```bash
docker images                  # list images
docker ps                      # running containers
docker ps -a                   # including stopped ones
docker logs <container>        # see output / errors
docker exec -it <container> sh # open a shell inside
docker stop <container>
docker rmi iris-api            # delete an image
docker system prune            # clean unused stuff (asks first)
```
Run in the background with `-d`: `docker run -d --name iris -p 8000:8000 iris-api`.

## Keeping images small and safe
- Use `-slim` bases and `--no-cache-dir` for pip.
- Pin versions in requirements so builds are repeatable.
- Never `COPY` secrets (`.env`, API keys) into an image; pass them at run time: `docker run -e API_KEY=xyz ...`.
- Point your platform's health check at `/health`.
- One process per container.

## Mistakes to avoid
- `--host 127.0.0.1` (or no host flag) inside the container: "connection refused" from outside.
- `COPY . .` before `pip install`: every code edit re-installs all libraries.
- Using `latest` tags: the base image changes under you. Pin `python:3.12-slim`.
- Saving the model with one scikit-learn version and loading with another. Training inside the image (as above) avoids this.
- Storing data inside a container and expecting it to survive. Containers are throwaway; use a volume (`-v`) or a database.

## Check yourself
- What is the difference between an image and a container?
- Why is `requirements.txt` copied before the code?
- Why must the app listen on `0.0.0.0` in a container?
- What does `-p 8000:8000` mean?
