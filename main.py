# main.py
import re
import os
import shutil # 用於複製檔案

# 載入環境變數 (從 .env 檔案)
from dotenv import load_dotenv
load_dotenv() # 確保這行在腳本較早的位置被執行

# 從其他模組導入函數
from download_audio import download_youtube_audio, sanitize_for_path 
from transcriber import transcribe_audio_locally
from llm_processor import process_transcript_with_gemini

def format_and_save_transcript_to_txt(transcript_text, output_folder, base_filename_stem):
    """
    將逐字稿格式化 (句末換行) 並儲存到 .txt 檔案。
    """
    if not transcript_text:
        print("[Saver-TXT] 錯誤：沒有逐字稿內容可以儲存。")
        return None
    formatted_text = re.sub(r'([。．\.])\s*', r'\1\n', transcript_text)
    lines = formatted_text.split('\n')
    cleaned_lines = [line.strip() for line in lines if line.strip()]
    final_formatted_text = '\n'.join(cleaned_lines)
    if not os.path.isdir(output_folder):
        print(f"[Saver-TXT] 警告：輸出資料夾 {output_folder} 不存在，嘗試建立。")
        try:
            os.makedirs(output_folder, exist_ok=True)
        except OSError as e:
            print(f"[Saver-TXT] 錯誤：無法建立資料夾 {output_folder} - {e}")
            return None
    transcript_filename = f"{base_filename_stem}_transcript.txt"
    transcript_filepath = os.path.join(output_folder, transcript_filename)
    try:
        with open(transcript_filepath, 'w', encoding='utf-8') as f:
            f.write(final_formatted_text)
        print(f"[Saver-TXT] 原始逐字稿已成功儲存至：{transcript_filepath}")
        return transcript_filepath
    except IOError as e:
        print(f"[Saver-TXT] 錯誤：無法將原始逐字稿儲存至檔案 {transcript_filepath} - {e}")
        return None

def save_text_to_markdown(content_text, output_folder, base_filename_stem, suffix="_gemini_output.md"):
    """
    將文字內容直接儲存到 Markdown (.md) 檔案。
    """
    if not content_text:
        print("[Saver-MD] 錯誤：沒有內容可以儲存到 Markdown 檔案。")
        return None
    if not os.path.isdir(output_folder):
        print(f"[Saver-MD] 警告：輸出資料夾 {output_folder} 不存在，嘗試建立。")
        try:
            os.makedirs(output_folder, exist_ok=True)
        except OSError as e:
            print(f"[Saver-MD] 錯誤：無法建立資料夾 {output_folder} - {e}")
            return None
    markdown_filename = f"{base_filename_stem}{suffix}"
    markdown_filepath = os.path.join(output_folder, markdown_filename)
    try:
        with open(markdown_filepath, 'w', encoding='utf-8') as f:
            f.write(content_text)
        print(f"[Saver-MD] Gemini 處理結果已成功儲存至：{markdown_filepath}")
        return markdown_filepath
    except IOError as e:
        print(f"[Saver-MD] 錯誤：無法將 Gemini 處理結果儲存至檔案 {markdown_filepath} - {e}")
        return None

def copy_file_to_destination(source_filepath, destination_folder):
    """
    將指定的來源檔案複製到目標資料夾。
    """
    if not source_filepath or not os.path.exists(source_filepath):
        print(f"[Copier] 錯誤：來源檔案 '{source_filepath}' 不存在或無效。")
        return None
    if not destination_folder: # 檢查 destination_folder 是否為 None 或空字串
        print(f"[Copier] 錯誤：未提供有效的目標資料夾路徑。")
        return None
    if not os.path.isdir(destination_folder):
        print(f"[Copier] 錯誤：目標資料夾 '{destination_folder}' 不存在或不是一個有效的資料夾。")
        print("[Copier] 請確認 Obsidian Vault 的路徑是否已在 .env 中正確設定，並且該資料夾已存在。")
        return None
    try:
        filename = os.path.basename(source_filepath)
        destination_filepath = os.path.join(destination_folder, filename)
        shutil.copy2(source_filepath, destination_filepath)
        print(f"[Copier] 檔案已成功複製到：{destination_filepath}")
        return destination_filepath
    except Exception as e:
        print(f"[Copier] 複製檔案 '{source_filepath}' 到 '{destination_folder}' 時發生錯誤：{e}")
        return None

def run_workflow():
    print("--- YouTube 影音轉逐字稿自動化流程開始 ---")
    
    # 獲取 API 金鑰和路徑設定
    gemini_api_key = os.getenv("GOOGLE_API_KEY")
    obsidian_notes_target_folder = os.getenv("path_to_obsidian_workspace") # 從 .env 讀取 Obsidian 路徑

    if not gemini_api_key:
        print("[Main Workflow] 警告：未能在環境變數或 .env 檔案中找到 GOOGLE_API_KEY。")
        user_provided_key = input("請手動輸入您的 Gemini API 金鑰 (或直接按 Enter 跳過 LLM 步驟)：").strip()
        if user_provided_key:
            gemini_api_key = user_provided_key
        else:
            print("[Main Workflow] 未提供 Gemini API 金鑰，LLM 處理步驟將被跳過。")

    if obsidian_notes_target_folder:
        print(f"[Main Workflow] Obsidian Notes 目標資料夾已設定為: {obsidian_notes_target_folder}")
    else:
        print("[Main Workflow] 警告: 未在 .env 檔案中找到 'path_to_obsidian_workspace' 設定。檔案將不會複製到 Obsidian。")


    youtube_link = input("請輸入 YouTube 影片的網址： ")
    if not youtube_link.strip():
        print("未輸入 YouTube 網址，流程結束。")
        return

    desired_name = input("請輸入您希望的檔案基礎名稱 (將用於資料夾和檔名)： ")
    if not desired_name.strip():
        print("未輸入有效的檔案基礎名稱，流程結束。")
        return

    keep_video_input = input("是否要保留下載的主要影片檔案 (MP4/WebM等)？ (y/N，預設為 N)： ")
    should_keep_video = keep_video_input.strip().lower() == 'y'

    whisper_model_size = input("請輸入您希望運行的語音轉文字模型大小 (tiny/ base/ small/ medium/ large)： ")
    models = {"tiny", "base", "small", "medium", "large"}
    if whisper_model_size not in models:
        print("未輸入有效的模型類別，流程結束。")
        return
    
    base_download_dir = "downloads" 

    # --- 步驟 1: 下載音訊 ---
    print("\n--- 步驟 1: 開始下載音訊 ---")
    download_info = download_youtube_audio(
        youtube_link, 
        desired_name, 
        output_directory=base_download_dir,
        keep_video_file=should_keep_video
    )

    if not download_info:
        print("[Main Workflow] 音訊下載失敗或未找到檔案，流程中止。")
        return

    mp3_file_path = download_info["mp3_filepath"]
    video_output_folder = download_info["output_folder"] 
    file_basename = download_info["basename"]          

    print(f"[Main Workflow] 音訊檔案已成功處理。主要 MP3 檔案：{mp3_file_path}")

    # --- 步驟 2: 音訊轉逐字稿 ---
    print("\n--- 步驟 2: 開始進行語音轉文字 ---")
    print(f"[Main Workflow] 將使用 Whisper 模型：'{whisper_model_size}'")
    target_lang = None 

    transcript = transcribe_audio_locally(
        mp3_file_path, 
        model_name=whisper_model_size, 
        target_language=target_lang
    )

    if not transcript:
        print("[Main Workflow] 語音轉文字失敗，流程中止。")
        return
    
    print("\n--- 原始逐字稿內容 (預覽前 300 字元) ---")
    preview_length = 300
    print(transcript[:preview_length] + "..." if len(transcript) > preview_length else transcript)

    # --- 步驟 3: 儲存原始逐字稿至 TXT 檔案 ---
    print("\n--- 步驟 3: 儲存格式化逐字稿至 TXT 檔案 ---")
    transcript_txt_path = format_and_save_transcript_to_txt(
        transcript,
        video_output_folder, 
        file_basename        
    )
    if transcript_txt_path:
        print(f"[Main Workflow] 原始逐字稿文字檔處理完成。")
    else:
        print("[Main Workflow] 儲存原始逐字稿文字檔失敗。")

    # --- 步驟 4: LLM (Gemini) 資料統整 ---
    gemini_processed_content = None
    gemini_md_path = None # 初始化 gemini_md_path
    if gemini_api_key:
        print("\n--- 步驟 4: LLM (Gemini) 資料統整 ---")
        video_title_for_llm = desired_name 
        
        gemini_processed_content = process_transcript_with_gemini(
            gemini_api_key,
            transcript, 
            video_title=video_title_for_llm
        )

        if gemini_processed_content:
            print("\n--- Gemini 處理後內容 (預覽前 500 字元) ---")
            preview_llm_length = 500
            print(gemini_processed_content[:preview_llm_length] + "..." if len(gemini_processed_content) > preview_llm_length else gemini_processed_content)
            
            print("\n--- 步驟 4.1: 儲存 Gemini 處理結果至 Markdown 檔案 ---")
            gemini_md_path = save_text_to_markdown( # 將回傳值賦給 gemini_md_path
                gemini_processed_content,
                video_output_folder,
                file_basename 
            )
            if gemini_md_path:
                print(f"[Main Workflow] Gemini 輸出 Markdown 檔案處理完成。")
            else:
                print("[Main Workflow] 儲存 Gemini 輸出 Markdown 檔案失敗。")
        else:
            print("[Main Workflow] Gemini 處理失敗或沒有內容返回。")
    else:
        print("\n[Main Workflow] 跳過 LLM (Gemini) 資料統整步驟 (未提供 API 金鑰)。")

    # --- 步驟 4.2 (或步驟 6 的一部分): 複製 Markdown 檔案到 Obsidian Vault ---
    copied_to_obsidian_path = None # 初始化
    if gemini_md_path and os.path.exists(gemini_md_path) and obsidian_notes_target_folder:
        print("\n--- 步驟 4.2: 複製 Markdown 檔案至 Obsidian Vault ---")
        print(f"[Main Workflow] 準備將檔案 '{gemini_md_path}' 複製到 Obsidian 資料夾: {obsidian_notes_target_folder}")
        copied_to_obsidian_path = copy_file_to_destination(gemini_md_path, obsidian_notes_target_folder)

        if copied_to_obsidian_path:
            print(f"[Main Workflow] 檔案已成功複製到 Obsidian Vault。")
        else:
            print("[Main Workflow] 複製檔案到 Obsidian Vault 失敗。")
    elif gemini_md_path and not obsidian_notes_target_folder:
        print("[Main Workflow] 已產生 Gemini Markdown 檔案，但未設定 Obsidian 目標資料夾，跳過複製步驟。")
    elif gemini_api_key and not gemini_md_path :
         print("[Main Workflow] 未能產生 Gemini Markdown 檔案，無法複製到 Obsidian。")

    # --- 步驟 6: (更新) 同步至 Obsidian 狀態 ---
    print("\n--- 步驟 5: 同步至 Obsidian 狀態 ---")
    if copied_to_obsidian_path:
         print(f"Markdown 檔案 ({copied_to_obsidian_path}) 已複製到指定 Obsidian 路徑。")
    elif gemini_md_path: 
         print(f"Markdown 檔案 ({gemini_md_path}) 已在本地準備好 ({video_output_folder})，但未複製到指定 Obsidian 路徑 (可能未設定路徑或複製失敗)。")
    elif transcript_txt_path: 
         print(f"原始逐字稿 TXT 檔案 ({transcript_txt_path}) 已準備好，可供參考。")

    print("\n--- 流程執行完畢 ---")

if __name__ == "__main__":
    run_workflow()