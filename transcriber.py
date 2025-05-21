import os
import whisper  # 官方 OpenAI Whisper 套件
import torch    # PyTorch 用於檢查 CUDA 和設定 device
import traceback # 用於印出更詳細的錯誤訊息

def transcribe_audio_locally(audio_file_path, model_name="base", target_language=None):
    """
    使用本地執行的 Whisper 模型將音訊檔案轉錄為文字。

    參數:
    audio_file_path (str): 要轉錄的音訊檔案路徑 (例如 .mp3)。
    model_name (str): 要使用的 Whisper 模型名稱
                       (e.g., "tiny", "base", "small", "medium", "large").
    target_language (str, optional): 音訊的語言代碼 (例如 "zh" 代表中文, "en" 代表英文)。
                                     如果為 None，Whisper 會自動偵測。

    返回:
    str: 辨識後的逐字稿文字，如果失敗則返回 None。
    """
    if not os.path.exists(audio_file_path):
        print(f"錯誤 (transcriber)：找不到音訊檔案 {audio_file_path}")
        return None

    print(f"\n[Transcriber] 正在載入 Whisper 模型 '{model_name}'... (首次使用可能需要下載)")
    try:
        # 檢查是否有可用的 GPU (PyTorch 方式)
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"[Transcriber] Whisper 將使用 '{device}' 執行。")
        
        # fp16 (半精度浮點數) 在 GPU 上可以加速並減少 VRAM 使用，但在 CPU 上應為 False。
        use_fp16 = (device == "cuda") 

        model = whisper.load_model(model_name, device=device)
        print(f"[Transcriber] 模型 '{model_name}' 載入完成。")
        print(f"[Transcriber] 開始轉錄音訊檔案：'{os.path.basename(audio_file_path)}'...")
        
        transcribe_options = {"fp16": use_fp16}
        if target_language:
            transcribe_options["language"] = target_language
            print(f"[Transcriber] 指定語言進行轉錄：{target_language}")
        else:
            print(f"[Transcriber] 將自動偵測語言。")

        # 執行轉錄
        # verbose=None 會使用預設的詳細程度，verbose=True 會印出更多進度
        result = model.transcribe(audio_file_path, verbose=None, **transcribe_options)
        
        transcript_text = result["text"]
        detected_language = result.get("language", "未知") # .get() 避免如果 'language' 鍵不存在時出錯
        print(f"[Transcriber] 轉錄完成！偵測到的語言：{detected_language}")
        
        return transcript_text

    except ModuleNotFoundError as e:
        if 'torch' in str(e).lower():
            print("[Transcriber] 錯誤：PyTorch 未正確安裝或找不到。請依照指示安裝 PyTorch。")
        else:
            print(f"[Transcriber] 錯誤：缺少必要的模組 - {e}")
        return None
    except Exception as e:
        print(f"[Transcriber] 使用 Whisper 進行本地轉錄時發生錯誤：{e}")
        traceback.print_exc() # 印出完整的錯誤堆疊，方便除錯
        return None

# --- 用於單獨測試 transcriber.py 的區塊 ---
if __name__ == '__main__':
    print("--- 正在單獨測試 transcriber.py ---")
    
    # 你需要一個實際存在的 MP3 檔案來進行測試
    # 將一個 MP3 檔案放到與 transcriber.py 同層的目錄，或指定完整路徑
    # 例如: test_audio_file = os.path.join("downloads", "TestVideoName", "TestVideoName.mp3")
    test_audio_file = "test_audio.mp3" 
    
    if not os.path.exists(test_audio_file):
        print(f"測試錯誤：找不到測試音訊檔案 '{test_audio_file}'。")
        print(f"請將一個名為 '{os.path.basename(test_audio_file)}' 的音訊檔案放在此目錄下，或修改 test_audio_file 變數的路徑。")
    else:
        test_model = "tiny" # 使用 "tiny" 或 "base" 進行快速測試
        print(f"將使用 '{test_model}' 模型測試 '{test_audio_file}'")
        
        transcript = transcribe_audio_locally(test_audio_file, model_name=test_model)
        
        if transcript:
            print("\n--- 測試逐字稿結果 ---")
            print(transcript)
        else:
            print("\n測試轉錄失敗。")
    print("--- transcriber.py 單獨測試結束 ---")