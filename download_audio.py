import subprocess
import os
import re

def sanitize_for_path(name):
    """
    清理字串，使其適用於檔案或資料夾名稱。
    移除在 Windows 和其他作業系統中常見的非法字元。
    """
    if not name:
        return "untitled"
    # 移除 Windows 和 Linux/macOS 路徑中非法的字元: < > : " / \ | ? * 以及控制字元
    name = re.sub(r'[<>:"/\\|?*\x00-\x1F]', '', name)
    # 移除檔名開頭和結尾的點 (.) 和空白
    name = name.strip('. ')
    # 如果清理後名稱為空，則使用預設名稱
    if not name:
        return "untitled"
    return name

def download_youtube_audio(video_url, desired_basename, output_directory="downloads", keep_video_file=False):
    """
    下載指定 YouTube 影片的音訊，並使用使用者指定的基礎名稱儲存。
    可選擇是否保留原始下載的影片檔，並會嘗試清理中繼檔案。

    返回:
    dict: 包含 "mp3_filepath", "output_folder", "basename" 的字典，如果失敗則返回 None。
    """
    sanitized_basename = sanitize_for_path(desired_basename)
    if not sanitized_basename or (sanitized_basename == "untitled" and desired_basename.strip() != "untitled"):
        print(f"警告：提供的基礎名稱 '{desired_basename}' 清理後變為 '{sanitized_basename}'。")
        if sanitized_basename == "untitled" and not desired_basename.strip(): # 如果原名是空的
             print("錯誤：基礎名稱無效，無法下載。")
             return None

    video_specific_folder = os.path.join(output_directory, sanitized_basename)

    # 建立基礎儲存下載檔案的資料夾 (如果不存在)
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
        print(f"[Downloader] 已建立基礎資料夾：{output_directory}")

    # 建立影片專用的子資料夾 (如果不存在)
    if not os.path.exists(video_specific_folder):
        os.makedirs(video_specific_folder)
        print(f"[Downloader] 已建立影片專用資料夾：{video_specific_folder}")
    
    output_template_path = os.path.join(video_specific_folder, sanitized_basename + ".%(ext)s")
    expected_mp3_path = os.path.join(video_specific_folder, sanitized_basename + ".mp3")

    command = [
        "yt-dlp",
        "--no-progress",  # 不顯示下載進度條
        "--console-title", # 在視窗標題顯示進度 (如果適用)
        "-x",             # 提取音訊
        "--audio-format", "mp3", # 指定音訊格式為 mp3
        "--audio-quality", "0",  # 最佳音質
    ]

    if keep_video_file:
        command.append("-k") # 或 --keep-video
        # 如果保留影片，明確要求 yt-dlp 合併格式以獲得最佳影片
        # 否則 -x 可能只下載音訊流而不下載影片流
        command.extend(["--merge-output-format", "mp4/webm/mkv"])


    command.extend(["-o", output_template_path, video_url])

    print(f"\n[Downloader] 正在準備下載：{video_url}")
    print(f"[Downloader] 將使用基礎名稱 '{sanitized_basename}' 儲存。")
    if keep_video_file:
        print("[Downloader] 將會保留主要影片檔案。")
    print(f"[Downloader] 執行命令：{' '.join(command)}")

    download_result_info = None

    try:
        process = subprocess.run(command, check=True, capture_output=True, text=True, encoding='utf-8')
        
        if process.stdout:
            print("\n--- yt-dlp 輸出摘要 ---")
            for line in process.stdout.splitlines():
                if "Destination:" in line or "Deleting" in line or "ERROR:" in line or "WARNING:" in line or "Keeping video" in line or "Merging formats" in line:
                    print(line)
        
        if os.path.exists(expected_mp3_path):
            print(f"\n[Downloader] 音訊成功下載並儲存於：{expected_mp3_path}")
            download_result_info = {
                "mp3_filepath": expected_mp3_path,
                "output_folder": video_specific_folder,
                "basename": sanitized_basename
            }
            
            if keep_video_file:
                found_video_files = []
                clean_video_extensions = ['.mp4', '.webm', '.mkv', '.flv', '.avi', '.mov', '.ogg'] 
                for ext in clean_video_extensions:
                    normalized_ext = ext if ext.startswith('.') else '.' + ext
                    video_file_path_to_check = os.path.join(video_specific_folder, sanitized_basename + normalized_ext)
                    if os.path.exists(video_file_path_to_check) and os.path.isfile(video_file_path_to_check) and video_file_path_to_check != expected_mp3_path:
                         found_video_files.append(video_file_path_to_check)
                
                if found_video_files:
                    print("\n[Downloader] 偵測到以下主要影片檔案被保留：")
                    for vf_path in list(set(found_video_files)): # 使用 set 去除重複
                        print(f"- {vf_path}")
                else:
                    print("\n[Downloader] 已選擇保留影片，但未自動偵測到「乾淨」的影片檔案。")
                    print("[Downloader] yt-dlp 可能下載了非預期副檔名的影片，或所有影片檔都帶有格式代碼。")
        else:
            print(f"\n[Downloader] 警告：預期的 MP3 檔案 '{expected_mp3_path}' 未在指定位置找到。")
            # download_result_info 保持為 None

    except subprocess.CalledProcessError as e:
        print(f"\n[Downloader] yt-dlp 執行失敗，返回碼 (Return Code): {e.returncode}")
        print("--- yt-dlp STDOUT (原始標準輸出) ---")
        if e.stdout:
            print(e.stdout.strip()) # strip() 去除前後多餘空白或換行
        else:
            print(" (stdout 為空或未捕獲)")
        print("--- yt-dlp STDERR (原始錯誤輸出) ---")
        if e.stderr:
            print(e.stderr.strip()) # strip() 去除前後多餘空白或換行
        else:
            print(" (stderr 為空或未捕獲)") # yt-dlp 的主要錯誤訊息通常在這裡
        return None # 確保錯誤時返回 None
    except FileNotFoundError:
        print("[Downloader] 錯誤：找不到 'yt-dlp' 命令。請確認 yt-dlp 已安裝並加入到系統 PATH。")
        return None
    except Exception as e:
        print(f"[Downloader] 發生未預期的錯誤：{e}")
        return None
    finally:
        # 清理中繼檔案的邏輯
        if os.path.isdir(video_specific_folder):
            print("\n[Downloader] 檢查並清理中繼檔案...")
            intermediate_file_pattern = re.compile(
                r"^" + re.escape(sanitized_basename) + r"\.f\d+\..+$"
            )
            cleaned_count = 0
            try:
                for filename_in_folder in os.listdir(video_specific_folder):
                    full_file_path = os.path.join(video_specific_folder, filename_in_folder)
                    if os.path.isfile(full_file_path) and intermediate_file_pattern.match(filename_in_folder):
                        try:
                            os.remove(full_file_path)
                            print(f"- 已刪除中繼檔案：{full_file_path}")
                            cleaned_count += 1
                        except OSError as e_remove:
                            print(f"- 無法刪除檔案 {full_file_path}: {e_remove}")
            except Exception as e_listdir:
                 print(f"[Downloader] 讀取資料夾內容時發生錯誤：{e_listdir}")

            if cleaned_count == 0:
                print("[Downloader] 沒有找到符合模式需要清理的中繼檔案。")
        
    return download_result_info

if __name__ == '__main__':
    print("--- 正在單獨測試 download_audio.py ---")
    test_url = input("請輸入測試用的 YouTube 連結：")
    if test_url.strip():
        test_basename = input("請輸入測試用的基礎檔名：")
        if test_basename.strip():
            test_keep_video = input("是否保留影片 (y/N)? ").strip().lower() == 'y'
            result = download_youtube_audio(test_url, test_basename, keep_video_file=test_keep_video)
            if result:
                print("\n測試下載成功，回傳資訊：")
                print(result)
            else:
                print("\n測試下載失敗。")
        else:
            print("未輸入基礎檔名。")
    else:
        print("未輸入 URL。")
    print("--- download_audio.py 單獨測試結束 ---")