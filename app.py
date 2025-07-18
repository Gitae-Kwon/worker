import streamlit as st
from datetime import datetime, timedelta, date, time
import pandas as pd
import holidays

# 설정
st.set_page_config(page_title="근무시간 계산기", page_icon="🕒")
st.title("🕒 근무시간 계산기")

# 🌐 국가 선택 (공휴일 반영)
country_display = {
    "대한민국": "KR",
    "프랑스": "FR",
    "미국": "US",
    "일본": "JP",
    "영국": "UK",
}
country_name = st.selectbox("현재 국가 선택 (공휴일 반영)", list(country_display.keys()), index=0)
country_code = country_display[country_name]

# 입력값
work_hours_per_day = st.number_input("하루 기준 근무시간 (시간)", min_value=1.0, max_value=24.0, value=8.0)
lunch_break_hours = st.number_input("점심시간 (시간)", min_value=0.0, max_value=3.0, value=1.0)
start_time = st.time_input("오늘 출근시간 입력", value=time(hour=9, minute=0))
target_date = st.date_input("특정 날짜까지 남은 근무시간 확인", value=None)

# 현재 시각 및 오늘 기준
now = datetime.now()
today = now.date()
start_datetime = datetime.combine(today, start_time)
end_datetime = start_datetime + timedelta(hours=work_hours_per_day + lunch_break_hours)

# 오늘 남은 근무시간 계산
if now >= end_datetime:
    today_remaining = 0
else:
    remaining_seconds = (end_datetime - now).total_seconds()
    today_remaining = round(remaining_seconds / 3600, 2)
today_ratio = (today_remaining / work_hours_per_day) * 100 if work_hours_per_day > 0 else 0

# 공휴일 목록
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

# 기준 날짜 계산
weekday = today.weekday()
start_of_week = today - timedelta(days=weekday)
end_of_week = start_of_week + timedelta(days=4)
start_of_month = today.replace(day=1)
next_month = (start_of_month.replace(day=28) + timedelta(days=4)).replace(day=1)
end_of_month = next_month - timedelta(days=1)

# 근무일 수 계산
week_remaining_days = get_remaining_workdays(today, end_of_week, holidays_set)
month_remaining_days = get_remaining_workdays(today, end_of_month, holidays_set)
week_total_days = get_total_workdays(start_of_week, end_of_week, holidays_set)
month_total_days = get_total_workdays(start_of_month, end_of_month, holidays_set)

# 남은 근무시간 계산
week_remaining_hours = today_remaining + work_hours_per_day * week_remaining_days
month_remaining_hours = today_remaining + work_hours_per_day * month_remaining_days
week_total_hours = work_hours_per_day * week_total_days
month_total_hours = work_hours_per_day * month_total_days

week_ratio = (week_remaining_hours / week_total_hours * 100) if week_total_hours > 0 else 0
month_ratio = (month_remaining_hours / month_total_hours * 100) if month_total_hours > 0 else 0

# 출력
st.subheader("📊 오늘 기준 근무시간")
st.metric("오늘 남은 근무시간", f"{today_remaining:.2f}시간 ({today_ratio:.0f}%)")
st.metric("이번주 남은 근무시간", f"{week_remaining_hours:.2f}시간 ({week_ratio:.0f}%)")
st.metric("이번달 남은 근무시간", f"{month_remaining_hours:.2f}시간 ({month_ratio:.0f}%)")

# 특정 날짜까지 계산
if target_date and target_date > today:
    target_remaining_days = get_remaining_workdays(today, target_date, holidays_set)
    total_days = get_total_workdays(today, target_date, holidays_set)
    target_remaining_hours = today_remaining + work_hours_per_day * target_remaining_days
    total_target_hours = work_hours_per_day * total_days
    target_ratio = (target_remaining_hours / total_target_hours * 100) if total_target_hours > 0 else 0

    st.subheader(f"📆 {target_date}까지")
    st.metric("남은 근무시간", f"{target_remaining_hours:.2f}시간 ({target_ratio:.0f}%)")
