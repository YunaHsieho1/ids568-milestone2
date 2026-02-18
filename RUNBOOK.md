# Operations Runbook — ML Inference Service (Milestone 2)

This document describes deployment workflow, dependency strategy, image optimization, security, and troubleshooting for this project.

---

## 1. Dependency Pinning Strategy

- **Goal**: Ensure reproducible builds and identical runtime environments.
- **Practice**:
  - **App dependencies**: All packages in `app/requirements.txt` use **pinned versions** (e.g. `flask==3.0.0`). Unpinned or range specs (e.g. `flask>=3.0.0`) are avoided.
  - **Test dependencies**: `requirements-dev.txt` includes app deps via `-r app/requirements.txt` and pins `pytest==8.0.0`.
  - **Docker base image**: The Dockerfile uses `python:3.11-slim` to lock Python major version and variant and avoid drift from base image updates.
- **Updating**: After upgrading any dependency, run tests locally, update the requirement files, commit, and rebuild the image and run CI.

---

## 2. Image Optimization

- **Strategy**:
  - **Multi-stage build**: Builder stage only runs `pip install`; the runtime stage copies only `/root/.local` and `app/`, with no build tools or raw requirements in the final image.
  - **Layer order**: `COPY app/requirements.txt` then `RUN pip install`, then `COPY app/`, so code changes only invalidate the last layers and cache is reused.
  - **Slim base**: Use `python:3.11-slim` instead of the full image to reduce size.
  - **.dockerignore**: Exclude `.git`, `.github`, `__pycache__`, `tests`, `*.md`, etc., to shrink build context and layers.
- **Result**: The runtime image contains only Python and Flask. Check size with `docker images` after a local build and compare with a single-stage or non-slim build if needed.

---

## 3. Security Considerations

- **Minimal attack surface**: The runtime stage does not install gcc, build-essential, or other build tools; only runtime dependencies are present.
- **Running as root**: The container currently runs as root; for hardening, add a non-root user in the Dockerfile and run `app.py` as that user.
- **Secrets**: No registry credentials in code or Dockerfile. CI uses GitHub Secrets (`GCP_SA_KEY`, `REGISTRY`, `ARTIFACT_REGISTRY_REPO`); locally use `gcloud auth configure-docker` or env vars.
- **Vulnerability scanning (optional)**: Add Trivy or Snyk in CI to scan the built image and document results and remediation in this runbook.

---

## 4. CI/CD Workflow

- **Triggers**:
  - On every **push/PR** to `main` or `master`: run the **test** job (pytest).
  - On **push to main/master** or **push of a version tag (v*)**: after test passes, run the **build** job (build Docker image).
  - **Only on push of a version tag** (e.g. v0.1.0): log in to the container registry and **push** the image with that semantic version tag.
- **Steps**:
  1. **test**: Checkout → install `requirements-dev.txt` → `pytest tests/ -v`.
  2. **build**: Checkout → Docker Buildx → build image (no push) → if version tag, log in to registry (GCP or generic) → push image.
- **GCP Artifact Registry**: Set GitHub **Variable** `REGISTRY_TYPE=gcp` and **Secrets** `REGISTRY`, `ARTIFACT_REGISTRY_REPO`, `GCP_SA_KEY`. See `docs/GCP_ARTIFACT_REGISTRY_SETUP.md`.

---

## 5. Versioning Strategy (Semantic Versioning)

- **Image tags**: Images are pushed only when a **Git tag matching v*** (e.g. v0.1.0, v1.2.3) is pushed; the image tag matches the Git tag.
- **Semantic versioning**: Use **vX.Y.Z** (major.minor.patch): bump X for breaking changes, Y for new features, Z for fixes.
- **How to release**:
  ```bash
  git tag v0.1.0
  git push origin v0.1.0
  ```
  The image is pushed to the registry with that tag (e.g. `us-central1-docker.pkg.dev/PROJECT/REPO/ml-service:v0.1.0`).

---

## 6. Registry Verification (GCP Result)

To satisfy the assignment requirement for proof of a successful image push:

### Option A — Screenshot in the repo

1. In GCP Console go to **Artifact Registry** → your repository (e.g. `milestone2`) → open the **ml-service** image and select a tag (e.g. `v0.1.4`).
2. Take a screenshot showing the repository name, image name, and tag.
3. Save it in the repo, e.g. `docs/registry-verification.png` or `docs/gcp-artifact-registry.png`.
4. Reference it in this runbook or in the README, for example:

   ```markdown
   ### Registry verification
   Image successfully pushed to GCP Artifact Registry:
   ![Registry verification](docs/registry-verification.png)
   ```

### Option B — Link and image path in README/RUNBOOK

1. In GCP Console, open your Artifact Registry repository and the **ml-service** image.
2. Copy the browser URL (or note the full image path).
3. In **RUNBOOK.md** or **README.md** add a “Registry verification” section with:
   - The **full image path**, e.g.  
     `us-central1-docker.pkg.dev/milestone2-tzuyu/milestone2/ml-service:v0.1.4`
   - Optional: “Verified in GCP Console: Artifact Registry → [repository] → ml-service → tag v0.1.4” (no need to paste a shareable link; the path is enough for graders to know where to look).

### Example section for RUNBOOK or README

```markdown
## Registry verification
- **Registry**: GCP Artifact Registry
- **Image**: `us-central1-docker.pkg.dev/<PROJECT_ID>/<REPO_NAME>/ml-service:v0.1.4`
- **Proof**: See screenshot [docs/registry-verification.png](docs/registry-verification.png) (or: verified in GCP Console under Artifact Registry.)
```

Replace `<PROJECT_ID>` and `<REPO_NAME>` with your actual values (e.g. `milestone2-tzuyu` and `milestone2`).

---

## 7. Troubleshooting

| Symptom | Likely cause | Action |
|--------|----------------|--------|
| CI error "Username and password required" | Using GCP but workflow used generic registry login | Add **Variable** `REGISTRY_TYPE=gcp` in GitHub (under Variables, not Secrets). |
| "Repository xxx not found" | Wrong registry path or repo does not exist | Confirm GCP project ID and repository name; `ARTIFACT_REGISTRY_REPO` must be `project-id/repo-name` (e.g. `milestone2-tzuyu/milestone2`). |
| Tests pass locally but fail in CI | Path or dependency differences | Run `pip install -r requirements-dev.txt && pytest tests/ -v` from repo root; check for absolute paths or missing dependencies. |
| Docker build slow or image too large | Layer order or large context | Ensure Dockerfile copies requirements before app code; check `.dockerignore` excludes unneeded files. |
| 403 / Permission denied on push | Insufficient service account permissions | Ensure the GCP service account has **Artifact Registry Writer**; ensure `GCP_SA_KEY` is the full JSON key content. |

---

## Related files

- **CI workflow**: `.github/workflows/build.yml`
- **GCP setup**: `docs/GCP_ARTIFACT_REGISTRY_SETUP.md`
- **Project overview**: `README.md`
