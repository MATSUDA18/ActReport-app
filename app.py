import streamlit as st
import datetime
import urllib.parse
import os
from PIL import Image

st.set_page_config(page_title="活動報告投稿アプリ", layout="centered")

# --- タイトルを1行でスッキリ綺麗に表示 ---
st.markdown("<h2 style='text-align: left; font-size: 24px;'>活動報告投稿アプリ</h2>", unsafe_allow_html=True)

# 曜日と場所の定義
activities = {
    "月": "穂積駅南口（挨拶活動）",
    "火": "国道21号線沿い（街頭報告）",
    "木": "本田団地南側ENEOS交差点（挨拶活動）",
    "金": "穂積駅南口（挨拶活動）",
}

# 選択フォーム（曜日）
selected_days = st.multiselect("活動した曜日を選択してください", list(activities.keys()))

# --- 曜日ごとの同行者設定 ---
day_attendees = {}
if selected_days:
    st.markdown("#### 👥 曜日ごとの同行者設定")
    attendee_options = ["なし", "森はるひさ県議", "宮川しょうけん市議", "瑞穂市議の皆様"]
    
    for day in selected_days:
        chosen = st.multiselect(f"【{day}曜日】の同行者を選択（複数可、なしの場合は「なし」を選択）", attendee_options, default=["なし"])
        day_attendees[day] = chosen

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

# --- プリセット画像の保存フォルダ準備 ---
IMAGE_DIR = "preset_images"
if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

# --- 画像の選択（アイコン・サムネイル表示対応） ---
st.markdown("---")
st.subheader("🖼️ 画像の選択")
image_mode = st.radio("画像の選び方を選んでください", ["登録済みの画像から選ぶ（アイコン選択）", "今回の投稿用の画像を新しくアップロードする"])

selected_images = []

if image_mode == "登録済みの画像から選ぶ（アイコン選択）":
    saved_images = sorted(os.listdir(IMAGE_DIR))
    if saved_images:
        st.write("使いたい画像にチェックを入れてください：")
        # 横に並べて見やすくするためのカラム分割
        cols = st.columns(3)
        selected_images = []
        for i, img_name in enumerate(saved_images):
            img_path = os.path.join(IMAGE_DIR, img_name)
            with cols[i % 3]:
                try:
                    img = Image.open(img_path)
                    st.image(img, width=100)
                except Exception:
                    st.write(f"({img_name})")
                
                # チェックボックスで選択
                is_checked = st.checkbox(img_name, key=f"chk_{img_name}")
                if is_checked:
                    selected_images.append(img_name)
    else:
        st.info("登録済みの画像がありません。画面一番下の「画像の管理」から画像を追加してください。")
else:
    uploaded_files = st.file_uploader("今回の投稿用画像をアップロード（複数可）", type=["jpg", "jpeg", "png"], accept_multiple_files=True, key="post_upload")
    if uploaded_files:
        selected_images = uploaded_files

# --- 原稿生成ボタン ---
if st.button("原稿を生成"):
    report_text = ""
    if selected_greeting != "選択なし":
        report_text += f"{selected_greeting}\n\n"
    
    report_text += "【活動報告】\n\n"
    
    for day in selected_days:
        loc = activities[day]
        att_list = day_attendees.get(day, ["なし"])
        
        if "なし" in att_list or not att_list:
            report_text += f"{day}曜日は{loc}にて活動を行いました。\n"
        else:
            actual_att = [a for a in att_list if a != "なし"]
            if not actual_att:
                report_text += f"{day}曜日は{loc}にて活動を行いました。\n"
            else:
                attendee_str = f"、{', '.join(actual_att)}の皆様"
                report_text += f"{day}曜日は{loc}にて{attendee_str}と活動を行いました。\n"
    
    hashtags = "\n#瑞穂市 #福祉 #障がい福祉 #WithYou #松田けんじ"
    final_post_text = report_text + hashtags
    
    st.session_state["final_post_text"] = final_post_text
    
    st.text_area("生成された原稿（確認・編集用）", final_post_text, height=200)
    
    # 選択された画像のプレビュー
    if selected_images:
        st.write(f"選択された画像数: {len(selected_images)}枚")
        for img in selected_images:
            if hasattr(img, "name"):
                st.image(img, width=150)
            else:
                img_path = os.path.join(IMAGE_DIR, img)
                if os.path.exists(img_path):
                    st.image(img_path, width=150)

# --- SNS直接投稿・一括投稿メニュー ---
if "final_post_text" in st.session_state:
    text_to_share = st.session_state["final_post_text"]
    encoded_text = urllib.parse.quote(text_to_share)
    
    st.markdown("---")
    st.subheader("SNSへ投稿する")
    
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

# --- 【一番下に移動】画像の登録・削除管理機能 ---
st.markdown("---")
with st.expander("⚙️ 【普段は閉じています】用意された画像の登録・削除管理"):
    new_preset = st.file_uploader("新しいプリセット画像を登録する（複数可）", type=["jpg", "jpeg", "png"], accept_multiple_files=True, key="preset_upload")
    if new_preset:
        for f in new_preset:
            save_path = os.path.join(IMAGE_DIR, f.name)
            with open(save_path, "wb") as w:
                w.write(f.getbuffer())
        st.success("新しい画像を登録しました！ページを更新して反映させてください。")
    
    existing_images = os.listdir(IMAGE_DIR)
    if existing_images:
        st.write("現在登録されている画像:")
        for img_name in existing_images:
            col_a, col_b, col_c = st.columns([1, 2, 1])
            with col_a:
                try:
                    st.image(os.path.join(IMAGE_DIR, img_name), width=50)
                except:
                    pass
            with col_b:
                st.write(img_name)
            with col_c:
                if st.button("削除", key=f"del_{img_name}"):
                    os.remove(os.path.join(IMAGE_DIR, img_name))
                    st.rerun()
    else:
        st.info("登録されている画像はありません。上のフォームから画像を追加してください。")
