import streamlit as st
import datetime
import urllib.parse

st.set_page_config(page_title="政治活動報告・告知投稿", layout="centered")

# --- アプリ全体のデザインスタイル ---
st.markdown("""
<style>
/* アプリ全体の背景色（淡いオレンジ・ピーチトーン） */
.stApp {
    background-color: #FFF6F0;
}

/* アプリ全体の左右の余白を詰めて横幅を最大限に活用する */
.block-container {
    padding-left: 0.8rem !important;
    padding-right: 0.8rem !important;
}
</style>
""", unsafe_allow_html=True)

# --- タイトル ---
st.markdown("<h3 style='text-align: left; font-size: 22px; margin-bottom: 15px; color: #333333;'>政治活動報告・告知 投稿アプリ</h3>", unsafe_allow_html=True)

# 活動場所の定義（曜日ごと）
activities_map = {
    0: ("月", "穂積駅南口（挨拶活動）"),
    1: ("火", "国道21号線沿い（街頭報告）"),
    3: ("木", "本田団地南側ENEOS交差点（挨拶活動）"),
    4: ("金", "穂積駅南口（挨拶活動）"),
}

# 共通のハッシュタグ設定
default_tags = ["#瑞穂市", "#福祉", "#障がい福祉", "#WithYou", "#松田けんじ"]

# --- ① 最初の入り口：告知用か報告用かの選択 ---
st.markdown("#### 📌 投稿の種類を選択してください")
post_type = st.radio(
    "投稿の種類",
    ["1）活動告知用", "2）活動報告用"],
    label_visibility="collapsed",
    horizontal=True
)

st.markdown("---")

# ==========================================
# 【1】活動告知用紙の場合
# ==========================================
if "1）活動告知用" in post_type:
    st.markdown("#### 📣 活動告知の設定")
    
    notice_timing = st.radio(
        "告知のタイミング",
        ["当日用（日付を入れない）", "明日以降（カレンダーで日付を指定）"],
        horizontal=True
    )
    
    notice_date = None
    if "明日以降" in notice_timing:
        notice_date = st.date_input("告知対象の日付を選択", value=datetime.date.today() + datetime.timedelta(days=1))
    
    notice_text = st.text_area(
        "💬 告知の補足テキストを入力（任意）",
        placeholder="例：本日は〇〇にて街頭活動を行います！お気軽にお声がけください。",
        height=100
    )
    
    # ハッシュタグ選択
    st.markdown("#### #️⃣ ハッシュタグの選択")
    extra_tag_input_n = st.text_input("追加したいハッシュタグ（半角スペース区切り）", placeholder="例：#街頭活動 #朝のご挨拶", key="extra_tag_n")
    added_tags_n = []
    if extra_tag_input_n.strip():
        for t in extra_tag_input_n.split():
            if not t.startswith("#"): t = "#" + t
            added_tags_n.append(t)
    
    all_tags_n = default_tags + added_tags_n
    selected_hashtags_n = []
    tag_cols_n = st.columns(2)
    for idx, tag in enumerate(all_tags_n):
        with tag_cols_n[idx % 2]:
            if st.checkbox(tag, value=True, key=f"htag_n_{idx}_{tag}"):
                selected_hashtags_n.append(tag)

    if st.button("📝 告知用原稿を生成する", type="primary", use_container_width=True):
        text_parts = []
        if notice_date and "明日以降" in notice_timing:
            date_str_n = notice_date.strftime('%Y年%m月%d日')
            text_parts.append(f"【{date_str_n} 告知】")
        
        if notice_text.strip():
            text_parts.append(notice_text.strip())
            
        hashtags_str_n = " ".join(selected_hashtags_n)
        
        if text_parts:
            final_post_text = "\n\n".join(text_parts) + "\n\n" + hashtags_str_n
        else:
            final_post_text = hashtags_str_n  # テキストがない場合はハッシュタグのみ
            
        st.session_state["final_post_text"] = final_post_text

# ==========================================
# 【2】活動報告用紙の場合
# ==========================================
else:
    st.markdown("#### ① 活動した日付の期間を選択してください")
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

    # 同行者選択の自動解除コールバック
    def toggle_companion(d_key, target_key):
        none_key = f"att_none_{d_key}"
        other_keys = [f"att_mori_{d_key}", f"att_mayor_{d_key}", f"att_miya_{d_key}", f"att_mizu_{d_key}"]
        if target_key != none_key and st.session_state.get(target_key, False):
            st.session_state[none_key] = False
        elif target_key == none_key and st.session_state.get(none_key, False):
            for k in other_keys:
                st.session_state[k] = False

    day_attendees = {}
    if active_days_data:
        st.markdown("---")
        st.markdown("#### ② 選択した活動日の同行者設定")
        for item in active_days_data:
            d_key = str(item["date_obj"])
            label_title = f"【{item['date_str']} ({item['day_char']}曜日)】 {item['location']}"
            st.markdown(f"**{label_title}** の同行者を選択")
            
            none_k = f"att_none_{d_key}"
            mori_k = f"att_mori_{d_key}"
            mayor_k = f"att_mayor_{d_key}"
            miya_k = f"att_miya_{d_key}"
            mizu_k = f"att_mizu_{d_key}"
            
            if none_k not in st.session_state: st.session_state[none_k] = True
            for k in [mori_k, mayor_k, miya_k, mizu_k]:
                if k not in st.session_state: st.session_state[k] = False
            
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

    # 冒頭の挨拶 & フリー本文入力
    st.markdown("---")
    st.markdown("#### ③ 冒頭の挨拶と本文の選択")
    greeting_options = [
        "おはようございます！",
        "こんにちは！",
        "皆様お疲れ様です。",
        "本日はまとめて活動報告をさせていただきます。",
        "本日はここ数日の活動報告をさせていただきます。",
        "本日は直近1週間の活動報告をさせていただきます。",
        "選択なし"
    ]
    selected_greeting = st.radio("挨拶を選択", greeting_options, index=0)

    free_text_input = st.text_area(
        "フリー本文・補足メッセージを入力（任意）",
        placeholder="例：本日は多くの方にお声がけいただき、大変励みになりました！温かいご声援ありがとうございます。",
        height=100
    )

    # ハッシュタグ選択
    st.markdown("---")
    st.markdown("#### ④ ハッシュタグの選択と追加")
    extra_tag_input_r = st.text_input("追加したいハッシュタグを入力（半角スペース区切り）", placeholder="例：#街頭活動 #朝のご挨拶", key="extra_tag_r")
    added_tags_r = []
    if extra_tag_input_r.strip():
        for t in extra_tag_input_r.split():
            if not t.startswith("#"): t = "#" + t
            added_tags_r.append(t)
    
    all_tags_r = default_tags + added_tags_r
    selected_hashtags_r = []
    tag_cols_r = st.columns(2)
    for idx, tag in enumerate(all_tags_r):
        with tag_cols_r[idx % 2]:
            if st.checkbox(tag, value=True, key=f"htag_r_{idx}_{tag}"):
                selected_hashtags_r.append(tag)

    # 報告用原稿生成ボタン
    if st.button("📝 活動報告用原稿を生成する", type="primary", use_container_width=True):
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
                report_text += f"・{date_s}（{day_c}）：{loc}にて、多様な仲間の皆様にご一緒させていただきました。\n"
            else:
                attendee_str = f"、{', '.join(actual_att)}"
                report_text += f"・{date_s}（{day_c}）：{loc}にて{attendee_str}の皆様にご一緒させていただきました。\n"
        
        hashtags_str = "\n" + " ".join(selected_hashtags_r) if selected_hashtags_r else ""
        final_post_text = report_text + hashtags_str
        st.session_state["final_post_text"] = final_post_text

# ==========================================
# 生成結果 & SNS共有エリア（共通）
# ==========================================
if "final_post_text" in st.session_state:
    st.markdown("---")
    st.markdown("#### 📝 生成された原稿（確認・編集用）")
    final_post_text = st.session_state["final_post_text"]
    st.text_area("原稿プレビュー", final_post_text, height=220, label_visibility="collapsed")
    
    char_count = len(final_post_text)
    if char_count > 280:
        st.warning(f"⚠️ 𝕏 (Twitter) の標準文字数制限（280文字）を超えています (現在: {char_count}文字)")
    else:
        st.caption(f"🐦 𝕏 文字数: **{char_count} / 280文字**")
    
    text_to_share = final_post_text
    encoded_text = urllib.parse.quote(text_to_share)
    
    st.markdown("---")
    st.subheader("🚀 SNSへ投稿する（複数選択可）")
    st.caption("※投稿したいSNSにチェックを入れ、文章をコピーするかボタンから投稿してください。")
    
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
