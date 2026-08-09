import streamlit as st
import datetime
import urllib.parse
import os
from PIL import Image

st.set_page_config(page_title="政治活動報告投稿", layout="centered")

# --- スマホ画面で確実に横3列に収めるための極限スリム化スタイル ---
st.markdown("""
<style>
/* アプリ全体の背景色（淡いオレンジ・ピーチトーン） */
.stApp {
    background-color: #FFF6F0;
}

/* アプリ全体の左右の余白を詰めて横幅を最大限に活用する */
.block-container {
    padding-left: 0.5rem !important;
    padding-right: 0.5rem !important;
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
        gap: 2px !important;
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

/* サムネイル画像をさらにスリムにし、3列できれいに収める */
div[data-testid="stColumn"] img,
.stColumn img {
    width: 50px !important;  
    height: 70px !important; 
    object-fit: cover !important;
    background-color: #faebe2;
    border-radius: 4px;
    display: block;
    margin: 0 auto;
}
</style>
""", unsafe_allow_html=True)

# --- タイトル ---
st.markdown("<h3 style='text-align: left; font-size: 22px; margin-bottom: 15px; color: #333333;'>政治活動報告投稿アプリ</h3>", unsafe_allow_html=True)

# 活動場所の定義（曜日ごと）
activities_map = {
    0: ("月", "穂積駅南口（挨拶活動）"),
    1: ("火", "国道21号線沿い（街頭報告）"),
    3: ("木", "本田団地南側ENEOS交差点（挨拶活動）"),
    4: ("金", "穂積駅南口（挨拶活動）"),
}

# --- ① 日付の選択（カレンダー入力・複数日対応） ---
st.markdown("#### ① 活動した日付を選択してください")
st.caption("※カレンダーで報告したい期間（または単日）を選んでください。自動で曜日の場所が割り当てられます。")

today = datetime.date.today()
date_range = st.date_input(
    "活動日を選択",
    value=(today - datetime.timedelta(days=3), today),
    label_visibility="collapsed"
)

target_dates = []
if isinstance(date_range, tuple):
    if len(date_range) == 2:
        start_d, end_d = date_range
        delta = end_d - start_d
        for i in range(delta.days + 1):
            target_dates.append(start_d + datetime.timedelta(days=i))
    elif len(date_range) == 1:
        target_dates = [date_range[0]]
else:
    target_dates = [date_range]

active_days_data = []
for d in target_dates:
    wd = d.weekday() 
    if wd in activities_map:
        day_char, loc_name = activities_map[wd]
        date_str = d.strftime('%Y年%m月%d日')
        active_days_data.append({
            "date_obj": d,
            "date_str": date_str,
            "day_char": day_char,
            "location": loc_name
        })

if not active_days_data:
    st.warning("⚠️ 選択した期間内に活動日（月・火・木・金）が含まれていません。日付の範囲を広げてください。")

# --- 曜日（日付）ごとの同行者設定 ---
day_attendees = {}
if active_days_data:
    st.markdown("---")
    st.markdown("#### 👥 選択した活動日の同行者設定")
    for item in active_days_data:
        d_key = str(item["date_obj"])
        label_title = f"【{item['date_str']} ({item['day_char']}曜日)】 {item['location']}"
        st.markdown(f"**{label_title}** の同行者を選択（複数可）")
        
        col_a1, col_a2 = st.columns(2)
        with col_a1:
            att_none = st.checkbox("なし", key=f"att_none_{d_key}", value=True)
            att_mori = st.checkbox("森はるひさ県議", key=f"att_mori_{d_key}")
            att_mayor = st.checkbox("森市長", key=f"att_mayor_{d_key}")
        with col_a2:
            att_miya = st.checkbox("宮川しょうけん市議", key=f"att_miya_{d_key}")
            att_mizu = st.checkbox("瑞穂市議の皆様", key=f"att_mizu_{d_key}")
        
        chosen = []
        if att_none: chosen.append("なし")
        if att_mori: chosen.append("森はるひさ県議")
        if att_mayor: chosen.append("森市長")
        if att_miya: chosen.append("宮川しょうけん市議")
        if att_mizu: chosen.append("瑞穂市議の皆様")
        day_attendees[d_key] = chosen

# --- ② 冒頭の挨拶 & フリー本文入力 ---
st.markdown("---")
st.markdown("#### ② 原稿の冒頭の挨拶と本文")
greeting_options = [
    "おはようございます！",
    "こんにちは！",
    "皆様お疲れ様です。",
    "本日はまとめて活動報告をさせていただきます。",
    "本日はここ数日の活動報告をさせていただきます。",
    "本日は今週の活動報告をまとめてさせていただきます。",
    "選択なし"
]
selected_greeting = st.radio("挨拶を選択", greeting_options, index=0)

# 【追加機能】フリー本文入力
free_text_input = st.text_area(
    "💬 フリー本文・補足メッセージを入力（任意）",
    placeholder="例：本日は多くの方にお声がけいただき、大変励みになりました！温かいご声援ありがとうございます。",
    height=100
)

# フォルダ準備
IMAGE_DIR = "preset_images"
if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

TEMP_DIR = "temp_uploads"
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

saved_images = sorted(os.listdir(IMAGE_DIR))
day_selected_images = {}

# --- ③ 日付ごとの画像選択（横3列スリム） ---
if active_days_data:
    st.markdown("---")
    st.markdown("#### 🖼️ ③ 活動日ごとの画像選択")
    st.caption("※コンパクトな縦長サムネイルが横3列に並びます。")
    
    for item in active_days_data:
        d_key = str(item["date_obj"])
        st.markdown(f"**📅 【{item['date_str']} ({item['day_char']}曜日)】の画像**")
        day_chosen_imgs = []
        
        if saved_images:
            st.write("・登録済み画像から選択（横3列）:")
            for i in range(0, len(saved_images), 3):
                row_items = saved_images[i:i+3]
                cols = st.columns(3)
                for col_idx, img_name in enumerate(row_items):
                    with cols[col_idx]:
                        img_path = os.path.join(IMAGE_DIR, img_name)
                        try:
                            st.image(Image.open(img_path), width=50)
                        except Exception:
                            pass
                        is_checked = st.checkbox(f"選択 {i+col_idx+1}", key=f"chk_{d_key}_{img_name}")
                        if is_checked:
                            day_chosen_imgs.append((img_name, img_path))
        else:
            st.info("登録済みの固定画像はありません。下のメニューから追加できます。")
        
        st.write("")
        uploaded_day_files = st.file_uploader(
            f"・スマホアルバムから写真追加【{item['date_str']}】",
            type=["jpg", "jpeg", "png"],
            accept_multiple_files=True,
            key=f"day_upload_{d_key}"
        )
        
        if uploaded_day_files:
            st.write("追加された写真：")
            for i in range(0, len(uploaded_day_files), 3):
                row_files = uploaded_day_files[i:i+3]
                cols_add = st.columns(3)
                for col_idx, uf in enumerate(row_files):
                    temp_path = os.path.join(TEMP_DIR, f"{d_key}_{uf.name}")
                    with open(temp_path, "wb") as tw:
                        tw.write(uf.getbuffer())
                    with cols_add[col_idx]:
                        try:
                            st.image(Image.open(temp_path), width=50)
                        except Exception:
                            pass
                        is_added_checked = st.checkbox(f"追加 {i+col_idx+1}", key=f"chk_temp_{d_key}_{uf.name}", value=True)
                        if is_added_checked:
                            day_chosen_imgs.append((uf.name, temp_path))
        
        day_selected_images[d_key] = day_chosen_imgs
        st.markdown("---")

# --- ④ 【追加機能】ハッシュタグの設定 ＆ SNS制限の確認 ---
st.markdown("#### #️⃣ ④ ハッシュタグの選択と追加")

default_tags = ["#瑞穂市", "#福祉", "#障がい福祉", "#WithYou", "#松田けんじ"]
extra_tag_input = st.text_input("追加したいハッシュタグを入力（半角スペース区切り）", placeholder="例：#街頭活動 #朝のご挨拶")

# 追加タグの分解
added_tags = []
if extra_tag_input.strip():
    for t in extra_tag_input.split():
        if not t.startswith("#"):
            t = "#" + t
        added_tags.append(t)

all_available_tags = default_tags + added_tags

st.write("使用するハッシュタグにチェックを入れてください：")
selected_hashtags = []
tag_cols = st.columns(2)
for idx, tag in enumerate(all_available_tags):
    with tag_cols[idx % 2]:
        if st.checkbox(tag, value=True, key=f"htag_{idx}_{tag}"):
            selected_hashtags.append(tag)

# ハッシュタグ制限表示
ig_tag_count = len(selected_hashtags)
if ig_tag_count > 30:
    st.error(f"⚠️ Instagramのハッシュタグ上限（30個）を超えています！ (現在: {ig_tag_count}個)")
else:
    st.caption(f"📸 Instagramハッシュタグ数: **{ig_tag_count} / 30個**")

# 原稿生成ボタン
if st.button("📝 原稿を生成する", type="primary", use_container_width=True):
    report_text = ""
    if selected_greeting != "選択なし":
        report_text += f"{selected_greeting}\n\n"
    
    # フリー本文がある場合は挿入
    if free_text_input.strip():
        report_text += f"{free_text_input.strip()}\n\n"
    
    report_text += "【活動報告】\n\n"
    
    for item in active_days_data:
        d_key = str(item["date_obj"])
        loc = item["location"]
        day_c = item["day_char"]
        date_s = item["date_str"]
        
        att_list = day_attendees.get(d_key, ["なし"])
        actual_att = [a for a in att_list if a != "なし"]
        
        if not actual_att:
            report_text += f"・{date_s}（{day_c}）：{loc}にて活動を行いました。\n"
        elif "瑞穂市議の皆様" in actual_att:
            report_text += f"・{date_s}（{day_c}）：{loc}にて、多様な仲間の皆様と活動を行いました。\n"
        else:
            attendee_str = f"、{', '.join(actual_att)}の皆様"
            report_text += f"・{date_s}（{day_c}）：{loc}にて{attendee_str}と活動を行いました。\n"
    
    # ハッシュタグ結合
    hashtags_str = "\n" + " ".join(selected_hashtags) if selected_hashtags else ""
    final_post_text = report_text + hashtags_str
    st.session_state["final_post_text"] = final_post_text

# 生成結果表示
if "final_post_text" in st.session_state:
    final_post_text = st.session_state["final_post_text"]
    st.text_area("生成された原稿（確認・編集用）", final_post_text, height=220)
    
    # X (Twitter) の文字数チェック表示
    char_count = len(final_post_text)
    if char_count > 280:
        st.warning(f"⚠️ 𝕏 (Twitter) の標準文字数制限（280文字）を超えています (現在: {char_count}文字)")
    else:
        st.caption(f"🐦 𝕏 文字数: **{char_count} / 280文字**")
    
    # 選択された画像確認プレビュー
    st.markdown("#### 📁 日付ごとに選択された画像一覧")
    for item in active_days_data:
        d_key = str(item["date_obj"])
        imgs = day_selected_images.get(d_key, [])
        if imgs:
            st.write(f"**【{item['date_str']}】の画像 ({len(imgs)}枚):**")
            for i in range(0, len(imgs), 3):
                row_imgs = imgs[i:i+3]
                cols_prev = st.columns(3)
                for idx, (img_name, img_path) in enumerate(row_imgs):
                    with cols_prev[idx]:
                        if os.path.exists(img_path):
                            st.image(Image.open(img_path), width=50)
        else:
            st.write(f"**【{item['date_str']}】の画像:** なし")

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
        fb_target_url = "https://www.facebook.com/share/1BzqwwS4bH/?mibextid=wwXIfr"
        encoded_fb_target = urllib.parse.quote(fb_target_url)
        fb_url = f"https://www.facebook.com/sharer/sharer.php?u={encoded_fb_target}"
        
        st.info("Facebookは仕様上、文章の自動ペーストができないため、下の文章をコピーしてからシェア画面を開いてください。")
        st.code(text_to_share, language="text")
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
                    st.image(Image.open(os.path.join(IMAGE_DIR, img_name)), width=40)
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

# --- アプリ用デザインアイコンの作成＆保存エリア ---
st.markdown("---")
with st.expander("🎨 スマホ用アプリアイコン画像のダウンロード"):
    st.write("木曜日の挨拶活動（本田団地南側ENEOS交差点風）をモチーフにしたマンガ風デザインのアイコンです。")
    st.caption("※以下の画像をスマホで長押し（または右クリック）して「写真に保存」してください。")
    
    # SVG形式でデフォルメデザインアイコンを生成
    svg_icon = """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="220" height="220">
      <rect width="512" height="512" rx="110" fill="#FF8A65"/>
      <circle cx="256" cy="256" r="230" fill="#FFA726" opacity="0.3"/>
      <!-- Intersection / Road -->
      <path d="M 120 440 L 392 440 L 350 340 L 162 340 Z" fill="#555"/>
      <line x1="256" y1="340" x2="256" y2="440" stroke="#FFF" stroke-width="6" stroke-dasharray="10,10"/>
      <!-- Gas station icon -->
      <rect x="360" y="260" width="70" height="80" rx="8" fill="#E65100"/>
      <text x="395" y="310" font-family="sans-serif" font-size="28" fill="#FFF" text-anchor="middle">⛽</text>
      <!-- Waving Character -->
      <path d="M 190 350 Q 256 310 320 350 L 330 440 L 180 440 Z" fill="#FF6D00"/>
      <circle cx="256" cy="250" r="55" fill="#FFCC80"/>
      <circle cx="235" cy="250" r="13" fill="none" stroke="#333" stroke-width="4"/>
      <circle cx="277" cy="250" r="13" fill="none" stroke="#333" stroke-width="4"/>
      <path d="M 240 275 Q 256 290 272 275" fill="none" stroke="#D84315" stroke-width="4" stroke-linecap="round"/>
      <circle cx="365" cy="210" r="16" fill="#FFCC80"/>
      <path d="M 310 320 Q 350 250 365 210" stroke="#FF6D00" stroke-width="24" stroke-linecap="round" fill="none"/>
      <!-- Manga Title Badge -->
      <rect x="35" y="35" width="442" height="115" rx="25" fill="#FFF" stroke="#D84315" stroke-width="8"/>
      <text x="256" y="85" font-family="'Comic Sans MS', 'Hiragino Kaku Gothic ProN', sans-serif" font-weight="900" font-size="38" fill="#D84315" text-anchor="middle">政治活動報告</text>
      <text x="256" y="128" font-family="'Comic Sans MS', 'Hiragino Kaku Gothic ProN', sans-serif" font-weight="900" font-size="30" fill="#333" text-anchor="middle">投稿アプリ</text>
    </svg>
    """
    st.markdown(svg_icon, unsafe_allow_html=True)
