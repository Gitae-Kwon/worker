import streamlit as st
from datetime import datetime, timedelta, date
import pandas as pd
import holidays

# 설정
st.set_page_config(page_title="근무시간 계산기", page_icon="🕒")
st.title("🕒 근무시간 계산기")

# 🌐 국가 선택 (공휴일 판단용)
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
off_time = st.time_input("오늘 퇴근시간 입력", value=datetime.now().time())
target_date = st.date_input("특정 날짜까지 남은 근무시간 확인", value=None)

# 날짜 관련 정보
now = datetime.now()
today = now.date()
today_work_done = datetime.combine(today, off_time) <= now

# 공휴일 목록
try:
    holiday_list = holidays.CountryHoliday(country_code, years=[today.year, today.year + 1])
except:
    holiday_list = {}

# 오늘 남은 근무시간 계산
today_remaining = 0 if today_work_done else work_hours_per_day

# 평일 + 공휴일 제외 계산 함수
def get_remaining_workdays(start_date, end_date, holidays_set):
    all_days = pd.date_range(start=start_date + timedelta(days=1), end=end_date, freq="D")
    workdays = [d for d in all_days if d.weekday() < 5 and d.date() not in holidays_set]
    return len(workdays)

# 기준 날짜
weekday = today.weekday()
start_of_week = today - timedelta(days=weekday)
end_of_week = start_of_week + timedelta(days=4)

start_of_month = today.replace(day=1)
next_month = (start_of_month.replace(day=28) + timedelta(days=4)).replace(day=1)
end_of_month = next_month - timedelta(days=1)

# 남은 근무일 계산
holidays_set = set(holiday_list.keys())
week_remaining_days = get_remaining_workdays(today, end_of_week, holidays_set)
month_remaining_days = get_remaining_workdays(today, end_of_month, holidays_set)

# 출력
st.subheader("📊 오늘 기준 근무시간")
st.metric("오늘 남은 근무시간", f"{today_remaining:.2f}시간")
st.metric("이번주 남은 근무시간", f"{today_remaining + work_hours_per_day * week_remaining_days:.2f}시간")
st.metric("이번달 남은 근무시간", f"{today_remaining + work_hours_per_day * month_remaining_days:.2f}시간")

# 특정 날짜까지
if target_date and target_date > today:
    target_remaining_days = get_remaining_workdays(today, target_date, holidays_set)
    st.subheader(f"📆 {target_date}까지")
    st.metric("남은 근무시간", f"{today_remaining + work_hours_per_day * target_remaining_days:.2f}시간")
