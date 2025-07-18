# -*- coding: utf-8 -*-

# 근무시간 계산기 (모바일 최적화: 근무시간 시 단위, 점심시간 드롭다운, 출근시간 제한)

import streamlit as st
from datetime import datetime, timedelta, date, time
from zoneinfo import ZoneInfo  # Python 3.9+
import pandas as pd
import holidays

# 🌍 국가 코드 및 타임존 맵
country_display = {
    "대한민국": "KR",
    "프랑스": "FR",
    "미국": "US",
    "일본": "JP",
    "영국": "UK",
}
timezone_map = {
    "KR": "Asia/Seoul",
    "FR": "Europe/Paris",
    "US": "America/New_York",
    "JP": "Asia/Tokyo",
    "UK": "Europe/London",
}

# ✅ 설정
st.set_page_config(page_title="근무시간 계산기", page_icon="🕒")
st.title("🕒 근무시간 계산기")

# 🌐 국가 선택
country_name = st.selectbox("현재 국가 선택 (공휴일 및 시간대 반영)", list(country_display.keys()), index=0)
country_code = country_display[country_name]
local_timezone = ZoneInfo(timezone_map.get(country_code, "Asia/Seoul"))

# 📥 사용자 입력
work_hours = st.number_input("하루 근무시간 (시 단위)", min_value=0, max_value=24, value=8)

lunch_options = {
    "30분": 30,
    "1시간": 60,
    "1시간 30분": 90
}
lunch_label = st.selectbox("점심시간 선택", list(lunch_options.keys()), index=1)
lunch_minutes = lunch_options[lunch_label]

# 총 소수점 환산 시간
work_hours_per_day = float(work_hours)
lunch_break_hours = lunch_minutes / 60

# 출근시간 선택 제한 (07:00~10:30, 15분 단위)
available_times = [time(hour=h, minute=m) for h in range(7, 11) for m in (0, 15, 30, 45) if not (h == 10 and m > 30)]
time_labels = [t.strftime("%H:%M") for t in available_times]
selected_label = st.selectbox("오늘 출근시간 입력", time_labels, index=time_labels.index("09:00"))
start_time = datetime.strptime(selected_label, "%H:%M").time()

# 특정일 입력
target_date = st.date_input("특정 날짜까지 남은 근무시간 확인", value=None)

# 🕒 현재 시간
now = datetime.now(local_timezone)
today = now.date()
st.markdown(f"🕒 **{country_name} 현재 시각:** `{now.strftime('%Y-%m-%d %H:%M:%S')}`")

start_datetime = datetime.combine(today, start_time).replace(tzinfo=local_timezone)
end_datetime = start_datetime + timedelta(hours=work_hours_per_day + lunch_break_hours)

if now >= end_datetime:
    today_remaining = 0
else:
    raw_remaining = (end_datetime - now).total_seconds() / 3600
    today_remaining = min(round(raw_remaining, 2), work_hours_per_day)

# 🎌 공휴일
try:
    holiday_list = holidays.CountryHoliday(country_code, years=[today.year, today.year + 1])
except:
    holiday_list = {}
holidays_set = set(holiday_list.keys())

# 근무일 계산 함수
def get_remaining_workdays(start_date, end_date, holidays_set):
    all_days = pd.date_range(start=start_date + timedelta(days=1), end=end_date, freq="D")
    workdays = [d for d in all_days if d.weekday() < 5 and d.date() not in holidays_set]
    return len(workdays)

def get_total_workdays(start_date, end_date, holidays_set):
    all_days = pd.date_range(start=start_date, end=end_date, freq="D")
    workdays = [d for d in all_days if d.weekday() < 5 and d.date() not in holidays_set]
    return len(workdays)

def format_hours_to_hm(hours: float):
    h = int(hours)
    m = int(round((hours - h) * 60))
    return f"{h}시간 {m}분"

def render_block(title, worked_hours, remaining_hours, total_hours):
    worked_ratio = worked_hours / total_hours * 100 if total_hours > 0 else 0
    remaining_ratio = 100 - worked_ratio
    worked_text = f"{format_hours_to_hm(worked_hours)}({worked_ratio:.0f}%)"
    remaining_text = f"{format_hours_to_hm(remaining_hours)}({remaining_ratio:.0f}%)"
    st.markdown(f"**일한 시간:** {worked_text} &nbsp;&nbsp;&nbsp; **남은시간:** {remaining_text}")
    bar_html = f"""
    <div style='display:flex; height:20px; border-radius:4px; overflow:hidden; margin-bottom:30px'>
        <div style='width:{worked_ratio}%; background-color:red;'></div>
        <div style='width:{remaining_ratio}%; background-color:steelblue;'></div>
    </div>
    """
    st.markdown(bar_html, unsafe_allow_html=True)

# 오늘/주/월 계산은 target_date 없을 때만 실행
if not target_date or target_date == today:
    weekday = today.weekday()
    start_of_week = today - timedelta(days=weekday)
    end_of_week = start_of_week + timedelta(days=4)
    start_of_month = today.replace(day=1)
    next_month = (start_of_month.replace(day=28) + timedelta(days=4)).replace(day=1)
    end_of_month = next_month - timedelta(days=1)

    week_remaining_days = get_remaining_workdays(today, end_of_week, holidays_set)
    month_remaining_days = get_remaining_workdays(today, end_of_month, holidays_set)
    week_total_days = get_total_workdays(start_of_week, end_of_week, holidays_set)
    month_total_days = get_total_workdays(start_of_month, end_of_month, holidays_set)

    week_remaining_hours = today_remaining + work_hours_per_day * week_remaining_days
    month_remaining_hours = today_remaining + work_hours_per_day * month_remaining_days
    week_total_hours = work_hours_per_day * week_total_days
    month_total_hours = work_hours_per_day * month_total_days

    render_block("오늘", work_hours_per_day - today_remaining, today_remaining, work_hours_per_day)
    render_block("이번주", week_total_hours - week_remaining_hours, week_remaining_hours, week_total_hours)
    render_block("이번달", month_total_hours - month_remaining_hours, month_remaining_hours, month_total_hours)

# 특정일 선택 시 단독 계산 (당일 제외) 또는 과거일 안내
if target_date:
    if target_date < today:
        st.warning("⚠️ 선택한 날짜가 오늘보다 이전입니다. 미래 날짜를 선택해주세요.")
    elif target_date > today:
        target_date_excluded = target_date - timedelta(days=1)
        target_remaining_days = get_remaining_workdays(today, target_date_excluded, holidays_set)
        total_days = get_total_workdays(today, target_date_excluded, holidays_set)
        target_remaining_hours = today_remaining + work_hours_per_day * target_remaining_days
        total_target_hours = work_hours_per_day * total_days
        render_block(f"{target_date}까지 (당일 제외)", total_target_hours - target_remaining_hours, target_remaining_hours, total_target_hours)
