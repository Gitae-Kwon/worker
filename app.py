# -*- coding: utf-8 -*-

# 근무시간 계산기 (시/분 단위 입력 + 과거일 안내 포함)

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
st.set_page_config(page_title="얼마나 남았니?", page_icon="🕒")
st.title("🕒 얼마나 남았니?")

# 🌐 국가 선택
country_name = st.selectbox("현재 국가 선택 (공휴일 및 시간대 반영)", list(country_display.keys()), index=0)
country_code = country_display[country_name]
local_timezone = ZoneInfo(timezone_map.get(country_code, "Asia/Seoul"))

# 📥 사용자 입력 (시/분 단위)
col1, col2 = st.columns(2)
with col1:
    work_hours = st.number_input("하루 근무시간 (시)", min_value=0, max_value=24, value=8)
with col2:
    work_minutes = st.number_input("하루 근무시간 (분)", min_value=0, max_value=59, value=0)

col3, col4 = st.columns(2)
with col3:
    lunch_hours = st.number_input("점심시간 (시)", min_value=0, max_value=3, value=1)
with col4:
    lunch_minutes = st.number_input("점심시간 (분)", min_value=0, max_value=59, value=0)

# 총 소수점 환산 시간
work_hours_per_day = work_hours + work_minutes / 60
lunch_break_hours = lunch_hours + lunch_minutes / 60

start_time = st.time_input("오늘 출근시간 입력", value=time(hour=9, minute=0))
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
    st.subheader(f"{title} 남은 근무시간")
    st.markdown(f"### {format_hours_to_hm(remaining_hours)} ({remaining_ratio:.0f}%)")
    st.markdown(f"**{title} 일한시간:** {worked_text} &nbsp;&nbsp;&nbsp; **남은시간:** {remaining_text}")
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
