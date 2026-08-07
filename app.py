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
attendees = st.multiselect("同行者を選択", ["森はるひさ県議", "宮川しょうけん市議", "瑞穂市議の皆様"])

# 原稿生成
if st.button("原稿を生成"):
    report_text = "【活動報告】\n\n"
    for day in selected_days:
        loc = activities[day]
        attendee_str = f"、{', '.join(attendees)}の皆様" if attendees else ""
        report_text += f"{day}曜日は{loc}にて{attendee_str}と活動を行いました。\n"
    
    st.text_area("生成された原稿", report_text, height=200)
    st.caption("#瑞穂市 #福祉 #障がい福祉 #WithYou #松田けんじ")
