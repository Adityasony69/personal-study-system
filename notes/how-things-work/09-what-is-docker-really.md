# What is Docker really

Docker packs your app **plus everything it needs** (the right Python version, packages, system libraries, settings) into one bundle called an **image**. Running an image gives a **container**: your app in its own sealed-off space. It runs the same on your laptop, a friend's laptop and a cloud server. It is the real fix for "it works on my machine".

> Honesty note: Docker is not installed on this PC, so the `docker` commands in this note were **not** run here. They are the standard commands from Docker's docs. Everything else in this series was run for real.

## What it is NOT: a virtual machine
| | Virtual machine | Container |
|---|---|---|
| What runs inside | A whole separate operating system | Just your app's process |
| Start-up time | Minutes | About a second |
| Size | Gigabytes | Often 50-200 MB |
| How | Fake hardware (hypervisor) | Linux kernel features that hide other processes and files from your app |

A container is really just a normal process on the host, with blinkers on: it sees only its own files, its own network, and its own process list. On Windows and Mac, Docker Desktop runs a small hidden Linux VM to provide that Linux kernel.

## The three words
- **Dockerfile**: the recipe (a text file you write).
- **Image**: the cooked, frozen meal. Built from the recipe, never changes.
- **Container**: a running copy of the image. You can run many from one image.

## A real Dockerfile for a small Python API

```dockerfile
FROM python:3.12-slim                 # start from an image that already has Python
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .                              # copy your code in last (see "layers" below)
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## The commands you will use daily
```bash
docker build -t myapi .                 # recipe -> image named "myapi"
docker run -p 8000:8000 myapi           # image -> container; map port 8000 to your PC
docker ps                               # list running containers
docker logs <container-id>              # see its output
docker exec -it <container-id> bash     # open a shell inside it
docker stop <container-id>
docker images                           # list images on your PC
```

`-p 8000:8000` matters: a container has its own network, so without this, `localhost:8000` on your PC reaches nothing.

## Layers: why the Dockerfile order matters
Each line in a Dockerfile makes a **layer**, and Docker caches layers. If a line and everything above it have not changed, Docker reuses the cached layer. That is why `requirements.txt` is copied and installed **before** the code: when you change only your code, the slow `pip install` step is skipped and the rebuild takes seconds instead of minutes.

## Containers forget everything
When a container is deleted, files written inside it are gone. Anything that must survive (a database's data, uploads) goes in a **volume**:

```bash
docker run -v pgdata:/var/lib/postgresql/data postgres:16
```

## Docker Compose: several containers together
A real app is often API + database + Redis. `docker-compose.yml` describes them all, and `docker compose up` starts them together on a shared network where they find each other by name (`db`, `redis`).

```yaml
services:
  api:
    build: .
    ports: ["8000:8000"]
    environment:
      DATABASE_URL: postgresql://postgres:secret@db:5432/app
  db:
    image: postgres:16
    environment:
      POSTGRES_PASSWORD: secret
    volumes: ["pgdata:/var/lib/postgresql/data"]
volumes:
  pgdata:
```

## Why employers care
Almost every backend job uses containers for deploying. Cloud services (Render, Railway, Google Cloud Run, AWS) take a Docker image and run it. Kubernetes, which you will hear about, is a system for running many containers across many servers.

## When you are ready to try
Docker Desktop for Windows is a system-wide install (needs WSL2). Install it yourself when you start a backend project, then build the Dockerfile above around a tiny FastAPI app.
