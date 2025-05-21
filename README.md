# Youtube Video to Article

一個 Python 自動化腳本，能從 YouTube 下載影片、進行本地語音轉文字、使用 Google Gemini API 整理逐字稿，並將結果保存為文字檔和 Markdown 檔案。

## 主要功能

* **自動化流程**：一鍵完成從 YouTube 影片到結構化筆記的轉換。
* **Youtube 影片音訊下載**：使用 `yt-dlp` 下載最佳音訊並轉為 MP3。
* **本地語音轉錄**：利用 `openai-whisper` 在本機進行高效準確的語音轉文字，保護隱私。
    * 支援 CPU 及 NVIDIA GPU 加速。
* **智能內容整理**：透過 Google Gemini API，根據客製化提示詞 (Prompt) 對逐字稿進行摘要、重點提煉、大綱生成等。
* **多格式輸出**：
    * 原始逐字稿 (句末優化換行) 存為 `.txt`。
    * Gemini 處理後的結構化內容存為 `.md` (Markdown)。
* **彈性設定**：
    * 可選擇是否保留原始影片檔案。
    * 可自訂輸出檔案和資料夾的基礎名稱。
    * 透過 `.env` 檔案安全管理 API 金鑰和路徑。

## 環境需求與事前準備 (Prerequisites)

在開始之前，請確保你的系統已安裝以下軟體：

1.  **Python**: 版本 3.8 或更高。可從 [Python 官網](https://www.python.org/downloads/) 下載。
2.  **FFmpeg**: `yt-dlp` 和 `openai-whisper` 都需要它來處理影音檔案。
    * **Windows**: 從 [FFmpeg官網](https://ffmpeg.org/download.html) (推薦 [gyan.dev](https://www.gyan.dev/ffmpeg/builds/)) 下載，解壓縮後將 `bin` 目錄加入系統 `PATH`。
    * **macOS**: `brew install ffmpeg`
    * **Linux**: `sudo apt update && sudo apt install ffmpeg` (Debian/Ubuntu) 或 `sudo dnf install ffmpeg` (Fedora)。
    * 安裝後，在終端機執行 `ffmpeg -version` 檢查是否成功。

## 安裝與設定 (Installation & Setup)

1.  **取得專案檔案**：
    * 如果你是從 GitHub 複製 (clone) 本專案：
        ```bash
        git clone <你的專案GitHub連結>
        cd <專案資料夾名稱>
        ```
    * 或者，直接下載本專案的所有 `.py` 檔案 (`main.py`, `download_audio.py`, `transcriber.py`, `llm_processor.py`) 及 `requirements.txt` (內容如本文件開頭所示)，並將它們放在同一個資料夾中。

2.  **建立並啟動 Python 虛擬環境** (強烈建議)：
    在你的專案資料夾根目錄下執行：
    ```bash
    python -m venv .venv
    ```
    啟動虛擬環境：
    * Windows (PowerShell): `.\.venv\Scripts\Activate.ps1`
    * Windows (CMD): `.\.venv\Scripts\activate.bat`
    * Linux/macOS: `source .venv/bin/activate`

3.  **安裝 Python 依賴套件**：
    確保虛擬環境已啟動，然後執行：

    * **(可選，但推薦給 NVIDIA GPU 使用者)** 為了 Whisper 的 GPU 加速，請先安裝與你 CUDA 版本相容的 PyTorch。前往 [PyTorch 官方網站](https://pytorch.org/get-started/locally/)，獲取並執行對應的 `pip install torch ...` 指令。

    * 安裝 `requirements.txt` 中的所有套件：
        ```bash
        pip install -r requirements.txt
        ```

4.  **設定環境設定檔 (`.env`)**：
    1.  在專案根目錄下，複製或建立一個名為 `.env` 的檔案。
    2.  編輯 `.env` 檔案，填入以下內容，並替換成你自己的值：
        ```env
        GOOGLE_API_KEY="YOUR_GEMINI_API_KEY_HERE"
        path_to_obsidian_workspace="YOUR_FULL_OBSIDIAN_NOTES_FOLDER_PATH_HERE"
        ```
        * `GOOGLE_API_KEY`: 你的 Google Gemini API 金鑰。可從 [Google AI Studio](https://aistudio.google.com/app/apikey) 取得。
        * `path_to_obsidian_workspace`: (可選) 你的 Obsidian Vault 中存放筆記的資料夾**完整路徑**。若留空或不設定，則不會執行複製到 Obsidian 的步驟。
            * Windows 範例: `C:\Users\YourUser\Documents\ObsidianVault\Notes`
            * macOS/Linux 範例: `/Users/YourUser/Documents/ObsidianVault/Notes`

    3.  **重要**: 如果你的專案使用 Git，請務必將 `.env` 檔案加入到 `.gitignore` 中，以防 API 金鑰外洩。
        在 `.gitignore` 中新增一行：
        ```
        .env
        ```

## 使用教學 (Usage)

完成安裝與設定後，即可執行主腳本。

1.  **執行主腳本**：
    在專案根目錄下的終端機/PowerShell 中執行（請在執行前確認虛擬環境已啟動）：
    ```bash
    python main.py
    ```

2.  **依照提示輸入資訊**：
    * **YouTube 影片網址**: 貼上目標 YouTube 影片的 URL。
    * **檔案基礎名稱**: 輸入一個名稱，用於建立子資料夾和相關檔案（例如「Python異步教學筆記」）。
    * **是否保留影片檔案 (y/N)**: 輸入 `y` 保留原始影片，否則按 Enter 或輸入 `n`。
    * **(如果需要)** 如果腳本未從 `.env` 找到 `GOOGLE_API_KEY`，會提示你手動輸入。

3.  **等待處理**：
    腳本會自動執行下載、轉錄、Gemini 處理和存檔等步驟。本地轉錄（尤其是 CPU）可能耗時較長。

4.  **查看成果**：
    * 所有輸出檔案將位於 `downloads/<你指定的基礎名稱>/` 資料夾內。
    * 主要檔案包括：
        * `基礎名稱.mp3`
        * `基礎名稱_transcript.txt` (原始逐字稿)
        * `基礎名稱_gemini_output.md` (Gemini 整理後的筆記)
        * (可選) 影片檔 (如 `基礎名稱.mp4`)
    * 若設定了 `path_to_obsidian_workspace`，`.md` 筆記將被複製到該路徑。

## 專案檔案結構 (Project Structure)

當執行上面的步驟後，專案的結構應該會如下圖所示：

![image](https://github.com/user-attachments/assets/5d4c09ec-175d-4b35-80ba-cd0de650f9ab)

## 注意事項

* **API 費用**: Google Gemini API 的使用可能產生費用。請參考 [Google AI Studio 定價頁面](https://ai.google.dev/pricing)了解免費額度和詳細費率。
* **API 金鑰安全**: 務必妥善保管您的 `GOOGLE_API_KEY`。
* **Whisper 效能**: 在 CPU 上執行 Whisper 轉錄長音訊或使用大型模型會非常耗時。建議使用支援 CUDA 的 NVIDIA GPU 並正確設定 PyTorch 以獲得最佳效能。
* **FFmpeg**: 請確保 FFmpeg 已正確安裝並可在系統 `PATH` 中被找到。
