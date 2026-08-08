import streamlit as st
import datetime
import urllib.parse

# 画面幅を広く使ってスマホ表示を安定させる
st.set_page_config(page_title="活動報告投稿アプリ", layout="centered")

# --- タイトルを1行でスッキリ綺麗に表示するための調整 ---
st.markdown("<h2 style='text-align: left; font-size: 24px;'>活動報告投稿アプリ</h2>", unsafe_allow_html=True)

# 曜日と場所の定義
activities = {
    "月": "穂積駅南口（挨拶活動）",
    "火": "国道21号線沿い（街頭報告）",
    "木": "本田団地南側ENEOS交差点（挨拶活動）",
    "金": "穂積駅南口（挨拶活動）",
}

# 選択フォーム
selected_days = st.multiselect("活動した曜日を選択してください", list(activities.keys()))

# 同行者の選択（誰も選択しない場合も想定）
attendee_options = ["森はるひさ県議", "宮川しょうけん市議", "瑞穂市議の皆様"]
attendees = st.multiselect("同行者を選択（選択しない場合は空欄にしてください）", attendee_options)

# --- 冒頭の挨拶（書き出し）の選択 ---
greeting_options = [
    "おはようございます！",
    "こんにちは！",
    "皆様お疲れ様です。",
    "本日はまとめて活動報告をさせていただきます。",
    "本日はここ数日の活動報告をさせていただきます。",
    "本日は今週の活動報告をまとめてさせていただきます。",
    "選択なし"
]
selected_greeting = st.selectbox("原稿の冒頭の挨拶を選んでください", greeting_options)

# --- 画像選択・アップロード機能 ---
st.subheader("画像の選択")
image_mode = st.radio("画像の選び方を選んでください", ["決まった画像（約10枚）から選ぶ", "新しい画像をアップロードする"])

selected_images = []

if image_mode == "決まった画像（約10枚）から選ぶ":
    preset_images = [f"sample_{i}.jpg" for i in range(1, 11)]
    selected_images = st.multiselect("用意された画像から選択（複数可）", preset_images)
else:
    uploaded_files = st.file_uploader("画像を新規に選択・アップロード（複数可）", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
    if uploaded_files:
        selected_images = uploaded_files

# --- 原稿生成 ---
if st.button("原稿を生成"):
    # 冒頭の挨拶の組み立て
    report_text = ""
    if selected_greeting != "選択なし":
        report_text += f"{selected_greeting}\n\n"
    
    report_text += "【活動報告】\n\n"
    
    # 同行者が誰も選択されていない場合の判定
    if len(attendees) == 0:
        for day in selected_days:
            loc = activities[day]
            report_text += f"{day}曜日は{loc}にて活動を行いました。\n\n"
    else:
        for day in selected_days:
            loc = activities[day]
            attendee_str = f"、{', '.join(attendees)}の皆様"
            report_text += f"{day}曜日は{loc}にて{attendee_str}と活動を行いました。\n"
    
    # ハッシュタグ
    hashtags = "\n#瑞穂市 #福祉 #障がい福祉 #WithYou #松田けんじ"
    final_post_text = report_text + hashtags
    
    # セッション状態に保存してSNSボタン等でも使えるようにする
    st.session_state["final_post_text"] = final_post_text
    
    st.text_area("生成された原稿（確認・編集用）", final_post_text, height=200)
    
    # 選択された画像のプレビュー表示
    if selected_images:
        st.write(f"選択された画像数: {len(selected_images)}枚")
        for img in selected_images:
            if hasattr(img, "name"):
                st.image(img, width=150)
            else:
                st.write(f"・{img}")

# 投稿用のテキストがすでにある場合（ボタンを押したあと保持する用）
if "final_post_text" in st.session_state:
    text_to_share = st.session_state["final_post_text"]
    encoded_text = urllib.parse.quote(text_to_share)
    
    # --- SNS直接投稿・一括投稿の選択メニュー ---
    st.markdown("---")
    st.subheader("SNSへ投稿する")
    
    # 投稿先の選択肢に「すべて一括」を追加
    sns_choice = st.selectbox(
        "投稿方法・送り先を選んでください",
        [
            "𝕏 (Twitter) で投稿する",
            "Instagramを開いて投稿する（テキスト自動コピー）",
            "Facebookでシェアする",
            "🚀 すべてのSNS（X・Instagram・FB）へまとめて準備・一括投稿する"
        ]
    )
    
    if "𝕏 (Twitter)" in sns_choice or "すべて" in sns_choice:
        x_url = f"https://twitter.com/intent/tweet?text={encoded_text}"
        st.markdown(f"[🐦 𝕏 (Twitter) の投稿画面を開く]({x_url})", unsafe_allow_html=True)
        
    if "Instagram" in sns_choice or "すべて" in sns_choice:
        st.info("Instagramはセキュリティ上、文章を直接ハメ込んで開けないため、下のボタンでテキストをコピーしてからInstagramアプリを開いてください。")
        st.code(text_to_share, language="text")
        st.markdown("[📷 Instagramアプリを開く（※上のテキストをコピーしてから開いてください）](https://www.instagram.com/)", unsafe_allow_html=True)
        
    if "Facebook" in sns_choice or "すべて" in sns_choice:
        fb_url = f"https://www.facebook.com/sharer/sharer.php?u=&quote={encoded_text}"
        st.markdown(f"[📘 Facebookのシェア画面を開く]({fb_url})", unsafe_allow_html=True)
