import streamlit as st
import datetime

st.set_page_config(page_title="活動報告投稿アプリ", layout="centered")

st.title("活動報告投稿アプリ")

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

# --- 画像選択・アップロード機能 ---
st.subheader("画像の選択")
image_mode = st.radio("画像の選び方を選んでください", ["決まった画像（約10枚）から選ぶ", "新しい画像をアップロードする"])

selected_images = []

if image_mode == "決まった画像（約10枚）から選ぶ":
    # 決まった画像のサンプルリスト（必要に応じてファイル名やパスを変更できます）
    preset_images = [f"sample_{i}.jpg" for i in range(1, 11)]
    selected_images = st.multiselect("用意された画像から選択（複数可）", preset_images)
else:
    uploaded_files = st.file_uploader("画像を新規に選択・アップロード（複数可）", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
    if uploaded_files:
        selected_images = uploaded_files

# --- 原稿生成 ---
if st.button("原稿を生成"):
    report_text = "【活動報告】\n\n"
    
    # 同行者が誰も選択されていない場合の判定
    if len(attendees) == 0:
        # 本文を作らずハッシュタグのみ、あるいはシンプルな形式にする
        report_text = ""
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
    
    st.text_area("生成された原稿（確認・編集用）", final_post_text, height=200)
    
    # 選択された画像のプレビュー表示
    if selected_images:
        st.write(f"選択された画像数: {len(selected_images)}枚")
        # 簡易的にアップロードされたファイルを表示
        for img in selected_images:
            if hasattr(img, "name"): # アップロードされたファイルの場合
                st.image(img, width=150)
            else: # プリセット画像名の場合
                st.write(f"・{img}")

    # --- SNS直接投稿（連携ボタン） ---
    st.markdown("---")
    st.subheader("SNSへ投稿する")
    st.info("※各SNSの仕様上、テキストのコピーや公式の投稿画面への連携を行います。")
    
    # X（旧Twitter）用の投稿リンク作成
    import urllib.parse
    encoded_text = urllib.parse.quote(final_post_text)
    x_url = f"https://twitter.com/intent/tweet?text={encoded_text}"
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"[𝕏 (Twitter) で投稿]({x_url})" , unsafe_allow_html=True)
    with col2:
        if st.button("Instagram用テキストをコピー"):
            st.success("テキストをコピーしました！（スマホやPCの機能で貼り付けてください）")
    with col3:
        if st.button("Facebook用テキストをコピー"):
            st.success("Facebook用の準備ができました！")
