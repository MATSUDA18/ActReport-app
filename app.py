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

# --- プリセット画像の読み込み ---
saved_images = sorted(os.listdir(IMAGE_DIR))

# --- 【変更】曜日ごとの画像選択機能（iPhoneでも確実に横3列に並ぶHTMLテーブル方式） ---
day_selected_images = {}

if selected_days:
    st.markdown("---")
    st.subheader("🖼️ 曜日ごとの画像選択")
    st.info("選択した曜日ごとに、使いたい画像にチェックを入れてください。")
    
    if saved_images:
        for day in selected_days:
            st.markdown(f"#### 📅 【{day}曜日】に載せる画像")
            
            # iPhoneでも崩れず必ず横3列に並ぶHTMLテーブルを構築
            html_code = "<table style='width:100%; border:none;'><tr>"
            for i, img_name in enumerate(saved_images):
                if i > 0 and i % 3 == 0:
                    html_code += "</tr><tr>"
                
                # 画像のパス（Streamlit上で表示させるためプレースホルダー的に処理）
                img_path = os.path.join(IMAGE_DIR, img_name)
                html_code += f"<td style='text-align:center; padding:5px; width:33%;'>"
                html_code += f"<b>No.{i+1}</b><br>"
                html_code += f"</td>"
            html_code += "</tr></table>"
            
            # サムネイルをプレビューしつつ、下のチェックボックスで選べるようにする
            # Streamlitのエレメントを3つずつ綺麗に並べる
            cols = st.columns(3)
            day_chosen_imgs = []
            
            for i, img_name in enumerate(saved_images):
                img_path = os.path.join(IMAGE_DIR, img_name)
                col_idx = i % 3
                with cols[col_idx]:
                    try:
                        img = Image.open(img_path)
                        # iPhoneで見やすい小さめサイズ
                        st.image(img, width=80)
                    except Exception:
                        pass
                    
                    is_checked = st.checkbox(f"選択", key=f"chk_{day}_{img_name}")
                    if is_checked:
                        day_chosen_imgs.append(img_name)
            
            day_selected_images[day] = day_chosen_imgs
            st.markdown("---")
    else:
        st.info("登録済みの画像がありません。画面一番下の「画像の管理」から画像を追加してください。")

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
            report_text += f"・{day}曜日：{loc}にて活動を行いました。\n"
        else:
            actual_att = [a for a in att_list if a != "なし"]
            if not actual_att:
                report_text += f"・{day}曜日：{loc}にて活動を行いました。\n"
            else:
                attendee_str = f"、多様な仲間の皆様" if "瑞穂市議の皆様" in actual_att else f"、{', '.join(actual_att)}の皆様"
                report_text += f"・{day}曜日：{loc}にて{attendee_str}と活動を行いました。\n"
    
    hashtags = "\n#瑞穂市 #福祉 #障がい福祉 #WithYou #松田けんじ"
    final_post_text = report_text + hashtags
    
    st.session_state["final_post_text"] = final_post_text
    
    st.text_area("生成された原稿（確認・編集用）", final_post_text, height=200)
    
    # 曜日ごとの選択画像確認
    st.markdown("#### 📁 曜日ごとに選択された画像一覧")
    total_selected_count = 0
    for day in selected_days:
        imgs = day_selected_images.get(day, [])
        if imgs:
            st.write(f"**【{day}曜日】の画像 ({len(imgs)}枚):**")
            cols_prev = st.columns(3)
            for idx, img_name in enumerate(imgs):
                with cols_prev[idx % 3]:
                    img_path = os.path.join(IMAGE_DIR, img_name)
                    if os.path.exists(img_path):
                        st.image(Image.open(img_path), width=100)
                total_selected_count += 1
        else:
            st.write(f"**【{day}曜日】の画像:** なし")

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

# --- 一番下の画像の登録・削除管理機能 ---
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
