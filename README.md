# 鄉音 (Hiong-Im) — 偏鄉長輩台語 AI 語音伴聊與客服助理
> **Hiong-Im (Homeland Accent) — A Taiwanese Hokkien AI Voice Companion for Rural Elders**

本專案旨在透過開源的台語語音技術與大語言模型，為偏鄉長輩建立一個完全使用**台語（台灣閩南語）**進行雙向語音對話的 AI 智慧助理。長輩只需發送台語語音，助理便會以親切、有耐心的台語語音進行陪伴與解答，藉此拉近偏鄉長輩與數位設備的距離。

本專案由 [PingpowerTW/Hiong-Im](https://github.com/PingpowerTW/Hiong-Im) 管理。

---

## 🛠️ 最優硬體與系統架構 (以 RTX 3050 8G 規劃)

本專案經過評估與優化，採用 **「本地雙向語音加速 + 雲端智慧推理」** 的混合架構。此架構能完美適應 **RTX 3050 8G (及以上)** 顯示卡，將總 VRAM 控制在 **6.5 GB** 左右，避免 8GB 顯存 OOM (記憶體溢出) 崩潰，同時達成秒級語音回應體驗。

```mermaid
graph TD
    User([台語長輩]) -- "語音訊息 (台語)" --> Telegram[Telegram Bot]
    Telegram --> Gateway[Hermes Gateway]
    
    subgraph 混合雲與本地 GPU 加速 (RTX 3050 8G 邊緣端)
        Gateway -- "語音檔 (.ogg)" --> ASR[Breeze-ASR-26-int8 on GPU]
        ASR -- "台語漢字文字" --> LLM[雲端 LLM API: Gemini/Agnes]
        LLM -- "台語回覆文字" --> TTS[OmniVoice-Hokkien API on GPU]
        TTS -- "台語回覆語音 .wav" --> Gateway
    end
    
    Gateway -- "語音訊息" --> Telegram
    Telegram --> User
```

### 📊 資源與 VRAM 分配表

| 模組 | 角色與模型 | VRAM 佔用 | 部署模式與推論速度 | 說明 |
| :--- | :--- | :--- | :--- | :--- |
| **1. ASR (聽得懂)** | `Breeze-ASR-26-int8` (Whisper Large) | **約 4.5 GB** | **本地 GPU (CUDA)**<br>⚡ **< 1.5 秒** | 聯發創新基地以 10,000 小時台語語料微調，台語辨識度最優。 |
| **2. LLM (想得快)** | `Gemini 2.5 Flash` 或 `Agnes-2.0-Flash` | **0 GB** (雲端) | **雲端低延遲 API**<br>⚡ **< 1.0 秒** | 釋放本地 VRAM，確保高水準的台語對話邏輯與即時回應。 |
| **3. TTS (講得順)** | `MERaLiON-OmniVoice-Hokkien-TTS` | **約 1.0 GB** | **本地 GPU (CUDA)**<br>⚡ **< 0.5 秒** | 基於 OmniVoice 架構，專為閩南語/台語設計的輕量級合成模型。 |
| **系統開銷** | 顯卡系統與 UI 開銷 | **約 1.0 GB** | - | 留作安全緩衝。 |
| **總計 VRAM** | - | **約 6.5 GB** | - | **完美運行在 RTX 3050 8G 顯存限制內！** |

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

### 3. 啟用自動語音回覆 (Auto-TTS)
確保 `~/.hermes/config.yaml` 開啟自動語音回覆：
```yaml
voice:
  auto_tts: true
```

### 4. 長輩專屬貼心台語人格配置
```yaml
agent:
  personalities:
    taigi: "您是一個會說台語的貼心助理。請全程使用台語（以台灣閩南語常用的傳統漢字書寫）回答長輩問題。語氣要非常溫柔、有耐心、親切，就像是長輩的孫子或晚輩一樣。避免使用生硬科技詞彙。"
```

---

## 🔌 顯示卡升級注意事項 (RTX 3050 8G / PCIe 3.0 / i7-3770 平台)

本主機採用 **Intel Core i7-3770 CPU** 與 **Intel Q77 晶片組**，若欲安裝 RTX 3050 8G 顯示卡，請注意：

1.  **PCIe 相容性**：RTX 3050 (PCIe 4.0 x8) 插在主機板的 PCIe 3.0 x16 插槽上會向下相容運作，效能損耗小於 2%，對 AI 推論無影響。
2.  **電源供應器 (PSU) 限制**：RTX 3050 8G 功耗約為 **130W**，整機建議配備至少 **450W** 的電源供應器，且通常需要 **1 個 PCIe 8-pin 外接電源接頭**。升級前請務必確認主機電源供應器規格。
3.  **BIOS 更新**：舊版主機板 BIOS 可能不支援新型 UEFI 顯示卡，安裝顯卡前**建議先將主機板 BIOS 更新至官方最新版本**，並開啟 CSM 模式相容。

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
    音檔將儲存於 `../BreezyVoice/results/speech_test.wav`（或依腳本指定路徑）。
