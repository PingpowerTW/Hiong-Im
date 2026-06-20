# 鄉音 (Hiong-Im) — 偏鄉長輩台語 AI 語音伴聊與客服助理
> **Hiong-Im (Homeland Accent) — A Taiwanese Hokkien AI Voice Companion for Rural Elders**

本專案旨在透過聯發科開源的台語大語言模型與語音模型（`Breeze-ASR-26` / `BreezyVoice`），為偏鄉長輩建立一個完全使用**台語（台灣閩南語）**進行雙向語音對話的 AI 智慧助理。長輩只需發送台語語音，助理便會以親切、有耐心的台語語音進行陪伴與解答，藉此拉近偏鄉長輩與數位設備的距離。

本專案由 [PingpowerTW/Hiong-Im](https://github.com/PingpowerTW/Hiong-Im) 管理。

---

## 🛠 系統架構

```mermaid
graph TD
    User([台語長輩]) -- "語音訊息 (台語)" --> Telegram[Telegram Bot]
    Telegram --> Gateway[Hermes Gateway]
    
    subgraph 本機/邊緣端加速 (Edge CPU/GPU)
        Gateway -- "語音檔 (.ogg)" --> ASR[Breeze-ASR-26-int8]
        ASR --> STT_Text[台語漢字文字]
        STT_Text --> LLM[AI 語言模型]
        LLM --> LLM_Reply[台語回覆文字]
        LLM_Reply --> TTS[BreezyVoice API Server]
        TTS --> TTS_Wav[台語回覆語音 .wav]
    end
    
    TTS_Wav --> Gateway
    Gateway -- "語音訊息" --> Telegram
    Telegram --> User
```

---

## 📊 硬體規格與部署手冊 (Specifications & Deployment)

為了適應不同的偏鄉落地場景與硬體預算，本專案提供三種部署模式：**「本機 CPU 測試現況」**、**「GPU 加速最佳解」**、以及**「偏鄉完全斷網落地體」**。

### 1. 三種部署模式比較表

| 模式 | 1. 本機 CPU 測試 (現況) | 2. GPU 加速模式 (最佳解) | 3. 完全斷網落地模式 (落地體) |
| :--- | :--- | :--- | :--- |
| **ASR 語音辨識** | 本機 CPU (INT8) | 本機 GPU (INT8) | 本機 GPU (INT8) |
| **LLM 智慧對話** | 雲端 API (Agnes/Gemini) | 雲端 API (Agnes/Gemini) | 本機 GPU (7B/8B 量化) |
| **TTS 語音合成** | 本機 CPU (INT8/FP16) | 本機 GPU (FP16) | 本機 GPU (FP16) |
| **網路依賴度** | 需要低流量網路 (LLM API) | 需要低流量網路 (LLM API) | **100% 離線運行 (無網可通)** |
| **預估推論延遲** | **1 ~ 2 分鐘** (因 CPU 運算緩慢) | **3 ~ 5 秒** (秒回體驗) | **5 ~ 8 秒** (視 LLM 大小而定) |
| **最低硬體需求** | 16GB RAM / 無顯卡限制 | 8GB VRAM (如 RTX 4060) | 16GB VRAM (如 RTX 4060 Ti 16G) |
| **推薦硬體規格** | 32GB RAM / CPU 8核以上 | **12GB VRAM** (如 **RTX 3060 12G**) | **24GB VRAM** (如 **RTX 3090 / 4090**) |

---

### 2. 核心模型選型說明 (Model Configuration)

#### A. ASR (語音轉文字)
* **推薦模型**：`MediaTek-Research/Breeze-ASR-26`
* **部署格式**：透過 `faster-whisper` 加載 `WizardForest/faster-whisper-Breeze-ASR-26-int8` 量化版。
* **說明**：專為台灣台語/繁體中文最佳化的 Whisper-large 架構，在 INT8 量化下能大幅降低記憶體開銷（約需 4.5G VRAM），且保留極高辨識率。

#### B. LLM (語言模型)
* **雲端模式 (1 & 2)**：`agnes-2.0-flash` 或 `gemini-2.5-flash`（低延遲、省本機算力）。
* **本機離線模式 (3)**：`MediaTek-Research/Breeze-7B-32k-Instruct-v1_0` 或 `Llama-3-8B-Instruct-Q4_K_M`。
* **說明**：本機執行時需配合 `ollama` 或 `llama.cpp` 將 LLM 進行 4-bit 量化，VRAM 佔用控制在 6G 左右。

#### C. TTS (語音合成)
* **推薦模型**：`MediaTek-Research/BreezyVoice`
* **部署格式**：基於 CozyVoice 300M 架構，執行 `api.py` 啟動 OpenAI 相容服務。
* **說明**：包含 G2PW 漢字注音轉換、Matcha-TTS 聲學模型與 HiFT 聲碼器，語音合成約需 4.5G VRAM。

---

## ⚙️ 快速配置指引 (Quick Start)

### 1. 本機 ASR 配置 (Hermes)
編輯 `~/.hermes/config.yaml` 啟用 ASR 服務：
```yaml
stt:
  enabled: true
  provider: local
  local:
    model: WizardForest/faster-whisper-Breeze-ASR-26-int8
    language: zh
```

### 2. 本機 TTS API 服務配置
執行 `/home/pipadmin/BreezyVoice/api.py` 啟動語音合成伺服器（預設監聽 8080 埠），並在 `~/.hermes/config.yaml` 設定：
```yaml
tts:
  provider: openai
  openai:
    model: MediaTek-Research/BreezyVoice
    voice: default
    base_url: http://localhost:8080/v1
```

### 3. 啟用自動語音回覆 (Auto-TTS)
編輯 `~/.hermes/config.yaml` 確保對話會自動以語音發送：
```yaml
voice:
  auto_tts: true
```

### 4. 長輩專屬貼心台語人格 (Taigi Personality)
```yaml
agent:
  personalities:
    taigi: "您是一個會說台語的貼心助理。請全程使用台語（以台灣閩南語常用的傳統漢字書寫）回答長輩問題。語氣要非常溫柔、有耐心、親切，就像是長輩的孫子或晚輩一樣。避免使用生硬科技詞彙。"
```

---

## ⚡ 測試與監控指令 (Testing & Monitoring)

* **TTS 語音合成測試**（合成「逐家好，我是一個會說台語的助理，真高興認識你！」）：
  ```bash
  /home/pipadmin/BreezyVoice/venv/bin/python /home/pipadmin/BreezyVoice/test_tts_server.py
  ```
  合成音檔將存放於 `/home/pipadmin/BreezyVoice/results/speech_test.wav`。

* **監控 Gateway 運行日誌**：
  ```bash
  tail -f ~/.hermes/logs/gateway.log
  ```

* **重啟 Gateway 以套用設定**：
  ```bash
  hermes gateway restart
  ```
