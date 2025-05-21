# llm_processor.py
import google.generativeai as genai
import os
import traceback

# ---------------------------------------------------------------------------
# 如果希望此檔案在獨立執行時也能讀取 .env，則需要取消註解以下兩行
# 這樣執行 python llm_processor.py 時，它會自己載入 .env
# ---------------------------------------------------------------------------
# from dotenv import load_dotenv
# load_dotenv() 
# ---------------------------------------------------------------------------
# 或者，更推薦的做法是，在 if __name__ == '__main__': 區塊內處理 .env 的載入，
# 這樣就不會影響 main.py (如果 main.py 已經有 load_dotenv())

def process_transcript_with_gemini(api_key, transcript_text, video_title=""):
    """
    使用 Gemini API 處理逐字稿文字，根據設計好的 prompt 進行整理。
    (函數內容與之前相同，此處省略以節省篇幅，請保留你之前的函數內容)
    """
    if not api_key:
        print("[LLM Processor] 錯誤：未提供 Gemini API 金鑰。")
        return None
    if not transcript_text:
        print("[LLM Processor] 錯誤：沒有逐字稿內容可以處理。")
        return None

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        prompt = f"""
        作為一個專業的影片內容分析師和筆記整理專家，請仔細閱讀以下來自 YouTube 影片「{video_title}」的逐字稿。
        你的任務是將這份逐字稿整理成一份結構清晰、重點突出、易於理解的文檔。

        請依照以下格式和要求進行整理：

        1.  **影片核心宗旨**：
            用一到兩句話總結這部影片最核心的主題或目的是什麼。

        2.  **內容摘要 (Summary)**：
            * 提供一段約 200-300 字的流暢敘述性摘要，概括影片的主要內容和流程。

        3.  **重點條列 (Key Takeaways)**：
            * 以條列方式 (bullet points) 列出影片中所有提到的重要觀點、關鍵資訊或技巧。
            * 每個條列點應簡潔，但有完整資訊，如技巧的使用流程、技巧的快捷鍵等等。

        4.  **詳細大綱 (Detailed Outline)**：
            * 根據影片內容的邏輯順序，產生一個結構化的層次大綱 (例如使用 1., 1.1, 1.1.1, 2. 等標號)。
            * 大綱應能反映影片的段落和主要討論點。

        5.  **延伸思考或建議行動 (Further Thoughts / Actionable Steps) (可選)**：
            * 如果影片內容具有啟發性或知識性，可以提出 1-2 個相關的延伸思考問題。
            * 如果影片是教學或指南性質，可以列出 1-3 個觀眾看完影片後可以採取的具體行動步驟。
            * 如果此部分不適用，可以省略或註明「無」。

        請確保你的輸出是純文字格式，並且各個區塊標題清晰 (例如使用粗體或 ## 標記)。

        以下是影片逐字稿內容：
        ---
        {transcript_text}
        ---

        請開始整理這份逐字稿：
        """
        print(f"[LLM Processor] 正在向 Gemini API (模型: {model.model_name}) 發送請求...")
        generation_config = genai.types.GenerationConfig(max_output_tokens=8192)
        response = model.generate_content(prompt, generation_config=generation_config)
        
        if response.parts:
            processed_text = response.text
            print("[LLM Processor] 已成功從 Gemini API 獲取回應。")
            return processed_text
        else:
            print("[LLM Processor] 警告：Gemini API 回應為空或不完整。")
            if hasattr(response, 'prompt_feedback') and response.prompt_feedback:
                 print(f"[LLM Processor] Prompt Feedback: {response.prompt_feedback}")
                 if response.prompt_feedback.block_reason:
                     print(f"[LLM Processor] 內容可能因以下原因被阻擋: {response.prompt_feedback.block_reason_message}")
            return None
    except Exception as e:
        print(f"[LLM Processor] 與 Gemini API 互動時發生錯誤：{e}")
        traceback.print_exc()
        return None

if __name__ == '__main__':
    print("--- 正在單獨測試 llm_processor.py ---")

    # 嘗試載入 .env 檔案 (僅在直接執行此腳本時)
    try:
        from dotenv import load_dotenv
        # load_dotenv() 會尋找當前目錄或父目錄中的 .env 檔案
        # 如果 .env 檔案與 llm_processor.py 在同一層級，這通常能成功
        if load_dotenv(): 
            print("[Tester] .env 檔案已嘗試載入。")
        else:
            print("[Tester] python-dotenv 未能找到 .env 檔案 (load_dotenv() 返回 False)。")
    except ImportError:
        print("[Tester] 警告：python-dotenv 套件未安裝。如果使用 .env 檔案，請執行 'pip install python-dotenv'")
    except Exception as e_dotenv:
        print(f"[Tester] 載入 .env 檔案時發生錯誤: {e_dotenv}")

    # 從環境變數中獲取 API Key
    test_api_key = os.getenv("GOOGLE_API_KEY")

    if not test_api_key:
        print("\n[Tester] 錯誤：未能在環境變數中找到 GOOGLE_API_KEY。")
        print("請確認以下事項：")
        print("1. 專案根目錄下是否存在名為 '.env' 的檔案。")
        print("2. '.env' 檔案中是否包含一行 'GOOGLE_API_KEY=\"你的API金鑰\"'。")
        print("3. 如果未使用 .env 檔案，是否已將 GOOGLE_API_KEY 設定為作業系統的環境變數，並且已重開終端機/IDE。")
        print("4. (如果使用 .env) python-dotenv 套件是否已安裝在目前的虛擬環境中 ('pip install python-dotenv')。")
    else:
        sample_transcript = """
        歡迎來到今天的烹飪教室！今天我們要學習如何製作一道美味的番茄炒蛋。
        首先，準備材料：新鮮番茄兩顆，雞蛋三顆，蔥花少許，鹽和糖適量。
        步驟一：將番茄切塊，雞蛋打散。步驟二：熱鍋下油，先將蛋液炒至半熟後盛出。
        步驟三：鍋中再加少許油，放入番茄塊翻炒，加入少許水，煮至番茄變軟出汁。
        步驟四：加入之前炒好的雞蛋，以及鹽和糖調味，快速拌炒均勻。
        最後，起鍋前撒上蔥花即可。這道菜簡單又營養，非常適合家庭日常。
        希望大家喜歡今天的教學，下次再見！
        """
        sample_title = "家常番茄炒蛋教學"
        
        key_preview = f"{test_api_key[:5]}...{test_api_key[-5:]}" if len(test_api_key) > 10 else test_api_key
        print(f"\n[Tester] 將使用 API 金鑰 (預覽: {key_preview}) 進行測試...")
        
        processed_content = process_transcript_with_gemini(test_api_key, sample_transcript, sample_title)
        
        if processed_content:
            print("\n--- Gemini 處理結果 ---")
            print(processed_content)
        else:
            print("\n[Tester] LLM 處理失敗。")
    print("\n--- llm_processor.py 單獨測試結束 ---")