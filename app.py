import streamlit as st
import datetime
import urllib.parse
import os
from PIL import Image

st.set_page_config(page_title="活動報告投稿アプリ", layout="centered")

# --- iPhoneでも絶対に横3列に並ぶための強力なCSS ---
st.markdown("""
<style>
/* Streamlitのカラムを強制的に3等分・横並びにする */
[data-testid="column"] {
    width: 32% !important;
    flex: 0 0 32% !important;
    min-width: 0px !important;
    padding: 1px !important;
    display: inline-block !important;
}
/* 行のラップ設定 */
.row-widget.stHorizontal {
    display: flex;
    flex-wrap: wrap;
}
</style>
""", unsafe_allow_html=True)

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
selected_days = st.multiselect("① 活動した曜日を選択してください", list(activities.keys()))

# --- 曜日ごとの同行者設定 ---
day_attendees = {}
if selected_days:
    st.markdown("#### 👥 曜日ごとの同行者設定")
    attendee_options = ["なし", "森はるひさ県議", "宮川しょうけん市議", "瑞穂市議の皆様"]
    
    for day in selected_days:
        chosen = st.multiselect(f"【{day}曜日】の同行者（複数可、なしは「なし」）", attendee_options, default=["なし"], key=f"att_{day}")
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
selected_greeting = st.selectbox("② 原稿の冒頭の挨拶を選んでください", greeting_options)

# --- プリセット画像の保存フォルダ準備 ---
IMAGE_DIR = "preset_images"
if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

TEMP_DIR = "temp_uploads"
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

# --- プリセット画像の読み込み ---
saved_images = sorted(os.listdir(IMAGE_DIR))

# --- 曜日ごとの画像選択（固定画像横3列 ＋ その下のアルバム追加） ---
day_selected_images = {}

if selected_days:
    st.markdown("---")
    st.subheader("🖼️ ③ 曜日ごとの画像選択")
    st.caption("※固定画像からサクッと選んだあと、必要に応じてアルバムから追加できます。")
    
    for day in selected_days:
        st.markdown(f"**📅 【{day}曜日】の画像**")
        
        day_chosen_imgs = []
        
        # 1. まず【登録済みの固定画像】を横3列のコンパクトなサムネイルで並べる
        if saved_images:
            st.write("・登録済み画像から選択：")
            # 3つずつグループに分けて横並び生成
            for i in range(0, len(saved_images), 3):
                row_items = saved_images[i:i+3]
                cols = st.columns(3)
                for col_idx, img_name in enumerate(row_items):
                    with cols[col_idx]:
                        img_path = os.path.join(IMAGE_DIR, img_name)
                        try:
                            # スクロール短縮のためサイズを少し小さめ（幅55px）に調整
                            st.image(Image.open(img_path), width=55)
                        except Exception:
                            pass
                        
                        is_checked = st.checkbox(f"選択", key=f"chk_{day}_{img_name}")
                        if is_checked:
                            day_chosen_imgs.append((img_name, img_path))
        else:
            st.info("登録済みの固定画像はありません（一番下の管理から追加できます）。")
        
        # 2. 【その下】にスマホアルバムからの追加機能を配置
        st.write("")
        day_temp_key = f"day_upload_{day}"
        uploaded_day_files = st.file_uploader(f"・スマホアルバムから写真を追加する【{day}】", type=["jpg", "jpeg", "png"], accept_multiple_files=True, key=day_temp_key)
        
        if uploaded_day_files:
            st.write("追加された写真：")
            cols_add = st.columns(3)
            for idx, uf in enumerate(uploaded_day_files):
                temp_path = os.path.join(TEMP_DIR, f"{day}_{uf.name}")
                with open(temp_path, "wb") as tw:
                    tw.write(uf.getbuffer())
                
                with cols_add[idx % 3]:
                    try:
                        st.image(Image.open(temp_path), width=55)
                    except:
                        pass
                    is_added_checked = st.checkbox(f"追加選択", key=f"chk_temp_{day}_{uf.name}")
                    if is_added_checked:
                        day_chosen_imgs.append((uf.name, temp_path))
        
        day_selected_images[day] = day_chosen_imgs
        st.markdown("---")

# --- 原稿生成ボタン ---
if st.button("📝 原稿を生成する", type="primary"):
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
    
    # 曜日ごとの選択画像確認プレビュー
    st.markdown("#### 📁 曜日ごとに選択された画像一覧")
    for day in selected_days:
        imgs = day_selected_images.get(day, [])
        if imgs:
            st.write(f"**【{day}曜日】の画像 ({len(imgs)}枚):**")
            cols_prev = st.columns(3)
            for idx, (img_name, img_path) in enumerate(imgs):
                with cols_prev[idx % 3]:
                    if os.path.exists(img_path):
                        st.image(Image.open(img_path), width=70)
        else:
            st.write(f"**【{day}曜日】の画像:** なし")

# --- SNS直接投稿・一括投稿メニュー ---
if "final_post_text" in st.session_state:
    text_to_share = st.session_state["final_post_text"]
    encoded_text = urllib.parse.quote(text_to_share)
    
    st.markdown("---")
    st.subheader("🚀 SNSへ投稿する")
    
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
