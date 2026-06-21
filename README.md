# 鄉音 (Hiong-Im) — 偏鄉長輩台語 AI 語音伴聊與客服助理
> **Hiong-Im (Homeland Accent) — A Taiwanese Hokkien AI Voice Companion for Rural Elders**

本專案旨在透過開源的台語語音技術與大語言模型，為偏鄉長輩建立一個完全使用**台語（台灣閩南語）**進行雙向語音對話的 AI 智慧助理。長輩只需發送台語語音，助理便會以親切、有耐心的台語語音進行陪伴與解答，藉此拉近偏鄉長輩與數位設備的距離。

本專案由 [PingpowerTW/Hiong-Im](https://github.com/PingpowerTW/Hiong-Im) 管理。

---

## 🛠️ 最優硬體與系統架構規劃 (RTX 3050 8G / 6G 適用)

本專案經過評估與優化，採用 **「本地雙向語音加速 + 雲端智慧推理」** 的混合架構。此架構能適應不同顯存規格的顯示卡，將 VRAM 佔用控制在安全範圍內，避免 OOM (記憶體溢出) 崩潰，同時達成秒級語音回應體驗。

```mermaid
graph TD
    User([台語長輩]) -- "語音訊息 (台語)" --> Telegram[Telegram Bot]
    Telegram --> Gateway[Hermes Gateway]
    
    subgraph 混合雲與本地 GPU 加速 (RTX 3050 邊緣端)
        Gateway -- "語音檔 (.ogg)" --> ASR[Breeze-ASR-26-int8 on GPU]
        ASR -- "台語漢字文字" --> LLM[雲端 LLM API: Gemini/Agnes]
        LLM -- "台語回覆文字" --> TTS[OmniVoice-Hokkien API on GPU]
        TTS -- "台語回覆語音 .wav" --> Gateway
    end
    
    Gateway -- "語音訊息" --> Telegram
    Telegram --> User
```

### 1. 顯示記憶體 (VRAM) 分配與規格對比

| 模組 | 使用模型 | VRAM 佔用 | 運行位置 / 預估推論時間 | 說明 |
| :--- | :--- | :--- | :--- | :--- |
| **ASR (聽得懂)** | `Breeze-ASR-26-int8` | **約 4.5 GB** | 🟢 本地 GPU (CUDA)<br>⚡ **< 1.5 秒** | 保持最強台語辨識模型在 GPU 執行，確保「聽得懂」。 |
| **LLM (想得快)** | `Gemini 2.5 Flash` | **0 GB** (雲端) | ☁️ 雲端 API<br>⚡ **< 1.0 秒** | 使用雲端 API，節省顯卡 VRAM 資源。 |
| **TTS (講得順)** | `MERaLiON-OmniVoice-Hokkien-TTS` | **約 1.0 GB** | 🟢 本地 GPU (CUDA)<br>⚡ **< 0.5 秒** | 基於 OmniVoice 架構，專為閩南語/台語設計的輕量級合成模型。 |

---

### 2. 顯示卡規格選擇與佈署策略

#### 🟢 方案 A：RTX 3050 8G (或 3060 12G) 方案
*   **VRAM 安全預算**：4.5G (ASR) + 1.0G (TTS) + 1.0G (系統畫面) = **約 6.5 GB VRAM**。完美控制在 8GB 限制內。
*   **硬體供電**：RTX 3050 8G 功耗約 130W，需配備至少 **450W 電源供應器**，且通常需要 **1 個 PCIe 8-pin 外接電源接頭**。

#### 🟢 方案 B：RTX 3050 6G 「免換電源」極限低配方案
*   **適用場景**：主機為套裝電腦（如 Acer Veriton），電源供應器僅有 220W-300W 且無 8-pin 供電頭，無法隨易升級大電源。
*   **運作原理（純運算卡模式）**：
    將螢幕訊號線接在**主機板**上，利用 CPU (i7-3770) 的內建顯卡（Intel HD 4000）輸出畫面（不吃獨顯顯存）。將 RTX 3050 6G 專門作為 AI 運算卡（顯示開銷降為 0）。
*   **VRAM 安全預算**：4.5G (ASR) + 1.0G (TTS) + 0G (無顯示輸出) = **約 5.5 GB VRAM**。在 6GB 限制內安全運行不崩潰。

---

## 🔌 3050 6G 純運算卡之 BIOS 內顯設定步驟

若採用 **方案 B**，插上顯示卡後必須手動在 BIOS 開啟內顯，否則將螢幕接在主機板會無畫面：

1.  **進入 BIOS**：開機時連續按鍵盤上的 **`Del` 鍵**（或 Acer 主機按 **`F2` 鍵**）。
2.  **變更顯示設定**：
    進入 **`Advanced`（進階）** ➡️ **`Chipset`（晶片組）** ➡️ **`Graphics Configuration`**：
    *   將 **`Primary Display`** (主顯示裝置) 設定為 **`IGFX`** (或 `Onboard` / `CPU`)。
    *   將 **`IGPU Multi-Monitor`** (內顯多螢幕支援) 設定為 **`Enabled`（啟用）**。
3.  **插線與存檔**：
    *   按 **`F10`** 儲存重啟。
    *   **將螢幕線插在主機板的孔上**。
4.  **驗證**：在終端機輸入 `nvidia-smi`，若顯存使用量為 `0MiB / 6144MiB`，即代表設定成功，顯卡已進入純運算模式。

---

## ⚡ 快速配置與部署指南

### 1. 本地 ASR 配置 (Hermes)
編輯您的 `~/.hermes/config.yaml`，啟用本地 ASR 服務：
```yaml
stt:
  enabled: true
  provider: local
  local:
    model: WizardForest/faster-whisper-Breeze-ASR-26-int8
    language: zh
```

### 2. 啟動台語 TTS API 服務
我們在專案中提供了相容於 OpenAI 規範的本地語音合成服務腳本 [api_omnivoice.py](file:///home/pipadmin/Hiong-Im/api_omnivoice.py)。

1.  **進入虛擬環境並安裝依賴**：
    ```bash
    source venv/bin/activate
    pip install omnivoice soundfile fastapi uvicorn pydantic-settings
    ```
2.  **啟動服務（預設監聽 8080 埠）**：
    ```bash
    nohup python api_omnivoice.py > tts_api.log 2>&1 &
    ```
3.  **在 `~/.hermes/config.yaml` 中配置 TTS 指向本地服務**：
    ```yaml
    tts:
      provider: openai
      openai:
        model: MERaLiON/MERaLiON-OmniVoice-Hokkien-TTS
        voice: default
        base_url: http://localhost:8080/v1
    ```

### 3. 啟用自動語音回覆 (Auto-TTS)與人格
確保 `~/.hermes/config.yaml` 中：
```yaml
voice:
  auto_tts: true
agent:
  personalities:
    taigi: "您是一個會說台語的貼心助理。請全程使用台語（以台灣閩南語常用的傳統漢字書寫）回答長輩問題。語氣要非常溫柔、有耐心、親切，就像是長輩的孫子或晚輩一樣。避免使用生硬科技詞彙。"
```

---

## 🧪 測試與驗證指令

*   **ASR 語音辨識測試**：
    ```bash
    python test_breeze_asr.py
    ```
*   **TTS 語音合成測試**（合成「逐家好，真高興認識你！」）：
    ```bash
    python test_tts_server.py
    ```
    音檔將儲存於 `../BreezyVoice/results/speech_test.wav`。
