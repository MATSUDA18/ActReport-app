import streamlit as st
import datetime
import urllib.parse
import os
from PIL import Image

st.set_page_config(page_title="活動報告投稿アプリ", layout="centered")

# --- スマホ画面で必ず横3列にスッキリ収めるための強化スタイル ---
st.markdown("""
<style>
/* アプリ全体の背景色（淡いオレンジ・ピーチトーン） */
.stApp {
    background-color: #FFF6F0;
}

/* スマホでもカラムを絶対に横3列に強制固定する */
@media screen and (max-width: 768px) {
    div[data-testid="stHorizontal"],
    div[data-testid="horizontalBlock"],
    .stHorizontal {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        width: 100% !important;
        gap: 4px !important;
    }
    
    div[data-testid="stHorizontal"] > div[data-testid="stColumn"],
    div[data-testid="stHorizontal"] > div[data-testid="column"],
    div[data-testid="horizontalBlock"] > div,
    .stColumn {
        width: 32% !important;
        min-width: 32% !important;
        max-width: 33% !important;
        flex: 1 1 32% !important;
        padding: 0px !important;
        box-sizing: border-box !important;
    }
}

/* サムネイルを囲むスペースと画像をコンパクトな縦長にスリム化 */
div[data-testid="stColumn"] img,
.stColumn img {
    width: 75px !important;  /* 横幅を小さく固定して3列に収める */
    height: 100px !important; /* 縦長比率を維持 */
    object-fit: cover !important;
    background-color: #faebe2;
    border-radius: 4px;
    display: block;
    margin: 0 auto;
}
</style>
""", unsafe_allow_html=True)

# --- タイトル ---
st.markdown("<h3 style='text-align: left; font-size: 22px; margin-bottom: 15px; color: #333333;'>活動報告投稿アプリ</h3>", unsafe_allow_html=True)

# 曜日と場所の定義
activities = {
    "月": "穂積駅南口（挨拶活動）",
    "火": "国道21号線沿い（街頭報告）",
    "木": "本田団地南側ENEOS交差点（挨拶活動）",
    "金": "穂積駅南口（挨拶活動）",
}

# ① 曜日選択
st.markdown("#### ① 活動した曜日を選択してください")
selected_days = []
c_mon = st.checkbox("月曜日（穂積駅南口）", key="day_mon")
c_tue = st.checkbox("火曜日（国道21号線沿い）", key="day_tue")
c_thu = st.checkbox("木曜日（本田団地南側ENEOS交差点）", key="day_thu")
c_fri = st.checkbox("金曜日（穂積駅南口）", key="day_fri")

if c_mon: selected_days.append("月")
if c_tue: selected_days.append("火")
if c_thu: selected_days.append("木")
if c_fri: selected_days.append("金")

# 曜日ごとの同行者設定
day_attendees = {}
if selected_days:
    st.markdown("---")
    st.markdown("#### 👥 曜日ごとの同行者設定")
    for day in selected_days:
        st.markdown(f"**【{day}曜日】の同行者を選択**（複数可）")
        col_a1, col_a2 = st.columns(2)
        with col_a1:
            att_none = st.checkbox("なし", key=f"att_none_{day}", value=True)
            att_mori = st.checkbox("森はるひさ県議", key=f"att_mori_{day}")
        with col_a2:
            att_miya = st.checkbox("宮川しょうけん市議", key=f"att_miya_{day}")
            att_mizu = st.checkbox("瑞穂市議の皆様", key=f"att_mizu_{day}")
        
        chosen = []
        if att_none: chosen.append("なし")
        if att_mori: chosen.append("森はるひさ県議")
        if att_miya: chosen.append("宮川しょうけん市議")
        if att_mizu: chosen.append("瑞穂市議の皆様")
        day_attendees[day] = chosen

# ② 冒頭の挨拶
st.markdown("---")
st.markdown("#### ② 原稿の冒頭の挨拶を選んでください")
greeting_options = [
    "おはようございます！",
    "こんにちは！",
    "皆様お疲れ様です。",
    "本日はまとめて活動報告をさせていただきます。",
    "本日はここ数日の活動報告をさせていただきます。",
    "本日は今週の活動報告をまとめてさせていただきます。",
    "選択なし"
]
selected_greeting = st.radio("挨拶を選択", greeting_options, index=0, label_visibility="collapsed")

# フォルダ準備
IMAGE_DIR = "preset_images"
if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

TEMP_DIR = "temp_uploads"
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

saved_images = sorted(os.listdir(IMAGE_DIR))
day_selected_images = {}

# ③ 曜日ごとの画像選択（横3列スリム・縦長比率・サイズ小型化）
if selected_days:
    st.markdown("---")
    st.markdown("#### 🖼️ ③ 曜日ごとの画像選択")
    st.caption("※縦長のコンパクトなサムネイルが横3列に並びます。")
    
    for day in selected_days:
        st.markdown(f"**📅 【{day}曜日】の画像**")
        day_chosen_imgs = []
        
        # 1. 固定画像（横3列・小型縦長表示）
        if saved_images:
            st.write("・登録済み画像から選択（横3列）:")
            for i in range(0, len(saved_images), 3):
                row_items = saved_images[i:i+3]
                cols = st.columns(3)
                for col_idx, img_name in enumerate(row_items):
                    with cols[col_idx]:
                        img_path = os.path.join(IMAGE_DIR, img_name)
                        try:
                            # 幅を75pxに固定してスリムに表示
                            st.image(Image.open(img_path), width=75)
                        except Exception:
                            pass
                        is_checked = st.checkbox(f"選択 {i+col_idx+1}", key=f"chk_{day}_{img_name}")
                        if is_checked:
                            day_chosen_imgs.append((img_name, img_path))
        else:
            st.info("登録済みの固定画像はありません（一番下の管理メニューから追加できます）。")
        
        # 2. スマホアルバムからの追加
        st.write("")
        uploaded_day_files = st.file_uploader(
            f"・スマホのアルバムから写真を追加する【{day}曜日】",
            type=["jpg", "jpeg", "png"],
            accept_multiple_files=True,
            key=f"day_upload_{day}"
        )
        
        if uploaded_day_files:
            st.write("追加された写真：")
            for i in range(0, len(uploaded_day_files), 3):
                row_files = uploaded_day_files[i:i+3]
                cols_add = st.columns(3)
                for col_idx, uf in enumerate(row_files):
                    temp_path = os.path.join(TEMP_DIR, f"{day}_{uf.name}")
                    with open(temp_path, "wb") as tw:
                        tw.write(uf.getbuffer())
                    with cols_add[col_idx]:
                        try:
                            st.image(Image.open(temp_path), width=75)
                        except Exception:
                            pass
                        is_added_checked = st.checkbox(f"追加 {i+col_idx+1}", key=f"chk_temp_{day}_{uf.name}", value=True)
                        if is_added_checked:
                            day_chosen_imgs.append((uf.name, temp_path))
        
        day_selected_images[day] = day_chosen_imgs
        st.markdown("---")

# 原稿生成ボタン
if st.button("📝 原稿を生成する", type="primary", use_container_width=True):
    report_text = ""
    if selected_greeting != "選択なし":
        report_text += f"{selected_greeting}\n\n"
    
    report_text += "【活動報告】\n\n"
    
    for day in selected_days:
        loc = activities[day]
        att_list = day_attendees.get(day, ["なし"])
        
        actual_att = [a for a in att_list if a != "なし"]
        if not actual_att:
            report_text += f"・{day}曜日：{loc}にて活動を行いました。\n"
        elif "瑞穂市議の皆様" in actual_att:
            report_text += f"・{day}曜日：{loc}にて、多様な仲間の皆様と活動を行いました。\n"
        else:
            attendee_str = f"、{', '.join(actual_att)}の皆様"
            report_text += f"・{day}曜日：{loc}にて{attendee_str}と活動を行いました。\n"
    
    hashtags = "\n#瑞穂市 #福祉 #障がい福祉 #WithYou #松田けんじ"
    final_post_text = report_text + hashtags
    st.session_state["final_post_text"] = final_post_text

# 生成結果表示
if "final_post_text" in st.session_state:
    final_post_text = st.session_state["final_post_text"]
    st.text_area("生成された原稿（確認・編集用）", final_post_text, height=200)
    
    # 曜日ごとの選択画像確認プレビュー
    st.markdown("#### 📁 曜日ごとに選択された画像一覧")
    for day in selected_days:
        imgs = day_selected_images.get(day, [])
        if imgs:
            st.write(f"**【{day}曜日】の画像 ({len(imgs)}枚):**")
            for i in range(0, len(imgs), 3):
                row_imgs = imgs[i:i+3]
                cols_prev = st.columns(3)
                for idx, (img_name, img_path) in enumerate(row_imgs):
                    with cols_prev[idx]:
                        if os.path.exists(img_path):
                            st.image(Image.open(img_path), width=75)
        else:
            st.write(f"**【{day}曜日】の画像:** なし")

# --- SNS直接投稿・複数選択メニュー ---
if "final_post_text" in st.session_state:
    text_to_share = st.session_state["final_post_text"]
    encoded_text = urllib.parse.quote(text_to_share)
    
    st.markdown("---")
    st.subheader("🚀 SNSへ投稿する（複数選択可）")
    st.caption("※投稿したいSNSにいくつでもチェックを入れてください。")
    
    post_x = st.checkbox("🐦 𝕏 (Twitter) で投稿する")
    post_ig = st.checkbox("📷 Instagram（テキスト自動コピー＋アプリ起動）")
    post_fb = st.checkbox("📘 Facebookでシェアする")
    
    if post_x:
        x_url = f"https://twitter.com/intent/tweet?text={encoded_text}"
        st.markdown(f"[➡️ 𝕏 (Twitter) の投稿画面を開く]({x_url})", unsafe_allow_html=True)
        
    if post_ig:
        st.info("Instagramは文章を直接ハメ込めないため、下のボタンでコピーしてからアプリを開いてください。")
        st.code(text_to_share, language="text")
        st.markdown("[➡️ Instagramアプリを開く](https://www.instagram.com/)", unsafe_allow_html=True)
        
    if post_fb:
        fb_url = f"https://www.facebook.com/sharer/sharer.php?u=&quote={encoded_text}"
        st.markdown(f"[➡️ Facebookのシェア画面を開く]({fb_url})", unsafe_allow_html=True)

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
            col_a, col_b, col_c = st.columns([1, 3, 1])
            with col_a:
                try:
                    st.image(Image.open(os.path.join(IMAGE_DIR, img_name)), width=45)
                except Exception:
                    pass
            with col_b:
                st.write(img_name)
            with col_c:
                if st.button("削除", key=f"del_{img_name}"):
                    os.remove(os.path.join(IMAGE_DIR, img_name))
                    st.rerun()
    else:
        st.info("登録されている画像はありません。上のフォームから画像を追加してください。")
