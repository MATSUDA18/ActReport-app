import streamlit as st
import datetime
import urllib.parse
import os
import base64
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

# --- 同行者選択の自動解除コールバック関数 ---
def toggle_companion(d_key, target_key):
    none_key = f"att_none_{d_key}"
    other_keys = [f"att_mori_{d_key}", f"att_mayor_{d_key}", f"att_miya_{d_key}", f"att_mizu_{d_key}"]
    
    if target_key != none_key and st.session_state.get(target_key, False):
        st.session_state[none_key] = False
    elif target_key == none_key and st.session_state.get(none_key, False):
        for k in other_keys:
            st.session_state[k] = False

# --- 曜日（日付）ごとの同行者設定 ---
day_attendees = {}
if active_days_data:
    st.markdown("---")
    st.markdown("#### 👥 選択した活動日の同行者設定")
    for item in active_days_data:
        d_key = str(item["date_obj"])
        label_title = f"【{item['date_str']} ({item['day_char']}曜日)】 {item['location']}"
        st.markdown(f"**{label_title}** の同行者を選択")
        
        none_k = f"att_none_{d_key}"
        mori_k = f"att_mori_{d_key}"
        mayor_k = f"att_mayor_{d_key}"
        miya_k = f"att_miya_{d_key}"
        mizu_k = f"att_mizu_{d_key}"
        
        if none_k not in st.session_state:
            st.session_state[none_k] = True
        for k in [mori_k, mayor_k, miya_k, mizu_k]:
            if k not in st.session_state:
                st.session_state[k] = False
        
        col_a1, col_a2 = st.columns(2)
        with col_a1:
            st.checkbox("なし", key=none_k, on_change=toggle_companion, args=(d_key, none_k))
            st.checkbox("森はるひさ県議", key=mori_k, on_change=toggle_companion, args=(d_key, mori_k))
            st.checkbox("森市長", key=mayor_k, on_change=toggle_companion, args=(d_key, mayor_k))
        with col_a2:
            st.checkbox("宮川しょうけん市議", key=miya_k, on_change=toggle_companion, args=(d_key, miya_k))
            st.checkbox("瑞穂市議の皆様", key=mizu_k, on_change=toggle_companion, args=(d_key, mizu_k))
        
        chosen = []
        if st.session_state[none_k]: chosen.append("なし")
        if st.session_state[mori_k]: chosen.append("森はるひさ県議")
        if st.session_state[mayor_k]: chosen.append("森市長")
        if st.session_state[miya_k]: chosen.append("宮川しょうけん市議")
        if st.session_state[mizu_k]: chosen.append("瑞穂市議の皆様")
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

# --- ④ ハッシュタグの選択と追加 ---
st.markdown("#### #️⃣ ④ ハッシュタグの選択と追加")

default_tags = ["#瑞穂市", "#福祉", "#障がい福祉", "#WithYou", "#松田けんじ"]
extra_tag_input = st.text_input("追加したいハッシュタグを入力（半角スペース区切り）", placeholder="例：#街頭活動 #朝のご挨拶")

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
    
    hashtags_str = "\n" + " ".join(selected_hashtags) if selected_hashtags else ""
    final_post_text = report_text + hashtags_str
    st.session_state["final_post_text"] = final_post_text

# 生成結果表示
if "final_post_text" in st.session_state:
    final_post_text = st.session_state["final_post_text"]
    st.text_area("生成された原稿（確認・編集用）", final_post_text, height=220)
    
    char_count = len(final_post_text)
    if char_count > 280:
        st.warning(f"⚠️ 𝕏 (Twitter) の標準文字数制限（280文字）を超えています (現在: {char_count}文字)")
    else:
        st.caption(f"🐦 𝕏 文字数: **{char_count} / 280文字**")
    
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

# --- アプリ用ポップデザインアイコン（画像内に「政治活動報告」グラフィック完全固定） ---
st.markdown("---")
with st.expander("🎨 スマホ用アプリアイコン画像のダウンロード（「政治活動報告」完全画像データ化）"):
    st.write("画像の中にポップな『政治活動報告』の文字グラフィックと挨拶するイラストが綺麗に組み合わさったアイコンです。")
    st.caption("※下の画像をスマホで長押しして「"写真"に追加」（またはイメージを保存）を選択してご利用ください。")
    
    # 完全に崩れないBase64エンコード化されたアイコンSVGグラフィック
    svg_icon_data = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">
      <defs>
        <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#FFE0B2"/>
          <stop offset="50%" stop-color="#FFB74D"/>
          <stop offset="100%" stop-color="#FF7043"/>
        </linearGradient>
        <filter id="popShadow" x="-10%" y="-10%" width="120%" height="120%">
          <feDropShadow dx="0" dy="6" stdDeviation="5" flood-color="#BE360A" flood-opacity="0.4"/>
        </filter>
      </defs>

      <!-- アイコン枠 -->
      <rect width="512" height="512" rx="110" fill="url(#bgGrad)"/>

      <!-- 幾何学的デザインパターン -->
      <circle cx="110" cy="110" r="95" fill="#FFFFFF" opacity="0.25"/>
      <circle cx="410" cy="410" r="125" fill="#FFFFFF" opacity="0.2"/>
      <polygon points="256,40 450,150 380,420 130,420 60,150" fill="#FFFFFF" opacity="0.12"/>
      <circle cx="256" cy="295" r="145" fill="#FFFFFF" opacity="0.85"/>

      <!-- 人物イラスト（正面向き・右手挙手） -->
      <g transform="translate(0, 20)">
        <path d="M 160 450 Q 256 330 352 450 L 370 480 L 142 480 Z" fill="#FF6D00"/>
        <path d="M 210 450 L 256 370 L 302 450 Z" fill="#FFFFFF"/>
        <path d="M 242 400 L 256 440 L 270 400 Z" fill="#D84315"/>

        <!-- 上げた右手 -->
        <path d="M 320 370 C 380 290 385 190 368 160 C 352 145 336 165 330 190 C 315 240 295 320 295 370 Z" fill="#FF6D00"/>
        <circle cx="368" cy="155" r="24" fill="#FFCC80"/>

        <!-- 顔・髪型 -->
        <ellipse cx="256" cy="245" rx="58" ry="68" fill="#FFCC80"/>
        <path d="M 195 235 C 195 165 317 165 317 235 C 305 185 207 185 195 235 Z" fill="#4E342E"/>

        <!-- メガネと笑顔 -->
        <rect x="210" y="225" width="38" height="26" rx="8" fill="none" stroke="#3E2723" stroke-width="5"/>
        <rect x="264" y="225" width="38" height="26" rx="8" fill="none" stroke="#3E2723" stroke-width="5"/>
        <line x1="248" y1="238" x2="264" y2="238" stroke="#3E2723" stroke-width="5"/>
        <circle cx="229" cy="238" r="4" fill="#3E2723"/>
        <circle cx="283" cy="238" r="4" fill="#3E2723"/>
        <path d="M 236 272 Q 256 290 276 272" fill="none" stroke="#D84315" stroke-width="5" stroke-linecap="round"/>
        <ellipse cx="212" cy="260" rx="10" ry="6" fill="#FF8A65" opacity="0.6"/>
        <ellipse cx="300" cy="260" rx="10" ry="6" fill="#FF8A65" opacity="0.6"/>
      </g>

      <!-- 上部にドーンと配置された「政治活動報告」バッジ -->
      <g filter="url(#popShadow)">
        <rect x="36" y="36" width="440" height="90" rx="24" fill="#FF5722"/>
        <rect x="42" y="42" width="428" height="78" rx="19" fill="#FFFFFF"/>
        <text x="256" y="96" font-family="sans-serif, system-ui, -apple-system" font-weight="900" font-size="42" fill="#D84315" text-anchor="middle" letter-spacing="3">政治活動報告</text>
      </g>
    </svg>"""

    # Base64形式にエンコードして確実に画像表示
    b64_svg = base64.b64encode(svg_icon_data.strip().encode('utf-8')).decode('utf-8')
    st.image(f"data:image/svg+xml;base64,{b64_svg}", width=240)
