# 從零開始：GCP Artifact Registry + GitHub Actions 設定教學

從在 GCP 建立 Artifact Registry 開始，到 GitHub 自動 push 映像為止，一步步操作。

---

## 第一步：GCP 建立專案並啟用 API

1. 打開 [Google Cloud Console](https://console.cloud.google.com/)。
2. **建立或選擇專案**
   - 頂部專案下拉選單 → **新增專案**（或選現有專案）。
   - 記下 **專案 ID**（例如 `my-mlops-project`），後面會用到。
3. **啟用 Artifact Registry API**
   - 左側選單：**API 與服務** → **程式庫**。
   - 搜尋 **Artifact Registry API** → 點進去 → **啟用**。

---

## 第二步：建立 Artifact Registry 存放區

1. 左側選單：**Artifact Registry** → **存放區**（或直接搜尋 "Artifact Registry"）。
2. 點 **建立存放區**。
3. 設定：
   - **名稱**：例如 `ml-service`（自訂，之後當成 REPO_NAME）。
   - **格式**：選 **Docker**。
   - **模式**：標準。
   - **位置類型**：選 **區域**，再選一個區域（例如 `us-central1` 或 `asia-east1`）。
4. 點 **建立**。
5. 記下三件事：
   - **專案 ID**：例如 `my-mlops-project`
   - **存放區名稱**：例如 `ml-service`
   - **區域**：例如 `us-central1`  
   映像完整位址會是：`REGION-docker.pkg.dev/PROJECT_ID/REPO_NAME/IMAGE:TAG`  
   例如：`us-central1-docker.pkg.dev/my-mlops-project/ml-service/ml-service:v0.1.0`  
   （第一個 `ml-service` 是 repo 名，第二個是 image 名，可一樣或不同。）

---

## 第三步：建立服務帳號給 GitHub Actions 用

1. 左側選單：**IAM 與管理** → **服務帳號**。
2. 點 **建立服務帳號**。
   - **名稱**：例如 `github-actions-push`。
   - **說明**：選填，例如 "Push images from GitHub Actions"。
3. 點 **建立並繼續**。
4. **角色**：點 **新增角色** → 搜尋並選擇 **Artifact Registry 寫入者**（Artifact Registry Writer）。
5. 點 **繼續** → **完成**。
6. 在服務帳號清單中，點剛建立的帳號（例如 `github-actions-push@...`）。
7. 切到 **金鑰** 分頁 → **新增金鑰** → **建立新金鑰** → 選 **JSON** → **建立**。  
   瀏覽器會下載一個 JSON 檔，**請妥善保存、不要 commit 到 Git**。  
   這個檔案的「整個內容」等一下要貼到 GitHub Secret。

---

## 第四步：在 GitHub 設定 Variable 與 Secrets

1. 打開你的 **GitHub 專案** → **Settings** → **Secrets and variables** → **Actions**。
2. **Variables 分頁** → **New repository variable**：
   - **Name**: `REGISTRY_TYPE`
   - **Value**: `gcp`  
   （這樣 workflow 才會走 GCP 登入與 push；用其他 registry 時不要設或改成其他值。）
3. **Secrets 分頁** → **New repository secret**，依序新增：

| Secret 名稱 | 值 | 說明 |
|-------------|----|------|
| `REGISTRY` | `us-central1-docker.pkg.dev` | 把 `us-central1` 換成你在第二步選的區域。 |
| `ARTIFACT_REGISTRY_REPO` | `你的專案ID/存放區名稱` | 例如 `my-mlops-project/ml-service`（專案 ID + 存放區名稱，中間一個 `/`）。 |
| `GCP_SA_KEY` | （整份 JSON 內容） | 第三步下載的 JSON 檔，用編輯器打開，**整份複製貼上**（從 `{` 到 `}`）。 |

- 若你用的是「一般 registry」（例如 Docker Hub 或學校給的），則**不要設** `REGISTRY_TYPE` 或設成非 `gcp`，並設 Secrets：`REGISTRY`、`REGISTRY_USERNAME`、`REGISTRY_PASSWORD`。

---

## 第五步：打版本 tag 觸發 Push

本教學的 workflow 會在「**推送版本 tag**」時，把映像 push 到 Artifact Registry。

在專案根目錄執行（請先 commit 並 push 所有變更）：

```bash
git tag v0.1.0
git push origin v0.1.0
```

到 GitHub **Actions** 分頁看是否有 **Build and Push** workflow 跑成功；成功後映像會出現在 GCP **Artifact Registry** → 你的存放區裡。

---

## 第六步：本地用 gcloud 登入並手動 push（選用）

若要從本機 push 到同一個 Artifact Registry：

1. 安裝 [Google Cloud SDK (gcloud)](https://cloud.google.com/sdk/docs/install)。
2. 登入並設預設專案：
   ```bash
   gcloud auth login
   gcloud config set project 你的專案ID
   ```
3. 設定 Docker 使用 gcloud 認證：
   ```bash
   gcloud auth configure-docker us-central1-docker.pkg.dev
   ```
   （把 `us-central1` 換成你的區域。）
4. 建置並打上完整映像名稱後 push：
   ```bash
   docker build -t us-central1-docker.pkg.dev/你的專案ID/ml-service/ml-service:v0.1.0 .
   docker push us-central1-docker.pkg.dev/你的專案ID/ml-service/ml-service:v0.1.0
   ```

---

## 映像路徑對照

| 項目 | 範例 |
|------|------|
| 區域 | `us-central1` |
| 專案 ID | `my-mlops-project` |
| 存放區名稱 | `ml-service` |
| 映像名稱（在 workflow 裡） | `ml-service` |
| 完整映像路徑 | `us-central1-docker.pkg.dev/my-mlops-project/ml-service/ml-service:v0.1.0` |

所以：
- `REGISTRY` = `us-central1-docker.pkg.dev`
- `ARTIFACT_REGISTRY_REPO` = `my-mlops-project/ml-service`

---

## 常見問題

- **Push 時 403 / Permission denied**  
  確認服務帳號角色有 **Artifact Registry 寫入者**，且 GitHub Secret `GCP_SA_KEY` 是整份 JSON、沒有多餘空白或換行漏掉。

- **找不到映像**  
  到 GCP Console → Artifact Registry → 你的存放區 → **映像** 分頁檢查 tag 是否為 `v0.1.0`（或你 push 的 tag）。

- **想換區域**  
  改 `REGISTRY`（例如改成 `asia-east1-docker.pkg.dev`），並在 GCP 該區域建立一個 Docker 存放區，再更新 `ARTIFACT_REGISTRY_REPO`（若專案或 repo 名有改）。

完成以上步驟後，你就會有一個「從 GCP 建立 Artifact Registry 開始」到「GitHub 自動建置並 push 映像」的完整流程。
