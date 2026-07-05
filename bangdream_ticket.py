import json
import os
import time
import requests
from bs4 import BeautifulSoup

# === ここだけ設定してください ===
WEBHOOK_URL = "https://discord.com/api/webhooks/1523316971490377748/8y0vURekOGDQazKPdTrhFv82_CokB8DnJfAwQQkSyEAbdmH7bDPPxI0j9nOVCw03mRaZ"
# ================================

TARGET_URL = "https://bang-dream.com/events/"
SAVE_FILE = "bangdream_data.json"

def send_discord(message):
    if not WEBHOOK_URL.startswith("http"):
        print("【エラー】Webhook URLが設定されていません。")
        return
    try:
        requests.post(WEBHOOK_URL, json={"content": message})
    except Exception as e:
        print(f"Discordの送信に失敗しました: {e}")

def check_bangdream_events():
    print("バンドリ公式イベントページを確認中...")
    current_events = {}
    
    # 🌟人間のブラウザからのアクセスに見せかける魔法の設定🌟
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        # サイトにシンプルにアクセス
        response = requests.get(TARGET_URL, headers=headers, timeout=15)
        response.raise_for_status()
        
        # BeautifulSoupという軽量ツールで文字を解析
        soup = BeautifulSoup(response.content, 'html.parser')
        links = soup.find_all("a")
        
        for link in links:
            href = link.get("href")
            text = link.get_text(separator='\n', strip=True)
            
            # リンクURLに /events/ が含まれるものを抽出
            if href and ("/events/" in href or "bang-dream.com/events" in href) and text:
                if href.endswith("/events/") or href.endswith("/events"):
                    continue
                    
                if not href.startswith("http"):
                    href = "https://bang-dream.com" + href
                
                status = "ℹ️ イベント情報公開"
                if "受付" in text or "先行" in text or "発売" in text or "抽選" in text:
                    status = "🟢 【チケット受付・先行開始の可能性あり】"
                elif "終了" in text or "完売" in text:
                    status = "❌ 【受付終了/完売】"
                
                lines = [line.strip() for line in text.split('\n') if line.strip() != '']
                title = lines[0] if lines else "バンドリ！イベント"
                details = " / ".join(lines[1:]) if len(lines) > 1 else ""
                
                current_events[href] = {
                    "title": title,
                    "details": details,
                    "status": status,
                    "link": href
                }
                
    except Exception as e:
        print(f"ページの読み込みに失敗しました: {e}")
        return

    if not current_events:
        print("イベント情報が見つかりませんでした。")
        return

    # === 過去のデータと比較して差分を通知 ===
    old_events = {}
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, 'r', encoding='utf-8') as f:
            old_events = json.load(f)

    for href, info in current_events.items():
        if href not in old_events:
            msg = f"🌟 **バンドリ！の新規イベントページが公開されました！**\n**【{info['title']}】**\n{info['details']}\n状態: {info['status']}\nリンク: {info['link']}"
            send_discord(msg)
            time.sleep(1)
            print(f"新規通知: {info['title']}")
            
        else:
            old_info = old_events[href]
            if old_info['status'] != info['status'] or old_info['details'] != info['details']:
                msg = f"🎫 **バンドリ！のイベント・チケット情報が更新されました！**\n**【{info['title']}】**\n更新前: {old_info['details']} ({old_info['status']})\n➡️ **更新後: {info['details']} ({info['status']})**\nリンク: {info['link']}"
                send_discord(msg)
                time.sleep(1)
                print(f"更新通知: {info['title']}")

    # 今回のデータを保存
    with open(SAVE_FILE, 'w', encoding='utf-8') as f:
        json.dump(current_events, f, ensure_ascii=False, indent=2)
    print("すべてのチェックが完了しました。")

if __name__ == "__main__":
    check_bangdream_events()
