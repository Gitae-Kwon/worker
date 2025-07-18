# 근무시간 계산기 (전체 통합코드)

import streamlit as st
from datetime import datetime, timedelta, date, time
from zoneinfo import ZoneInfo  # Python 3.9+
import pandas as pd
import holidays
import altair as alt

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
st.title("\ud83d\udd52 \uadfc\ubb34\uc2dc\uac04 \uacc4\uc0b0\uae30")

# 🌐 국가 선택
country_name = st.selectbox("\ud604\uc7ac \uad6d\uac00 \uc120\ud0dd (\uacf5\ud734\uc77c \ubc0f \uc2dc\uac04\ub300 \ubc18\uc601)", list(country_display.keys()), index=0)
country_code = country_display[country_name]
local_timezone = ZoneInfo(timezone_map.get(country_code, "Asia/Seoul"))

# 포부: 사용자 입력
work_hours_per_day = st.number_input("\ud558\ub8e8 \uae30준 \uadfc\ubb34\uc2dc\uac04 (\uc2dc\uac04)", min_value=1.0, max_value=24.0, value=8.0)
lunch_break_hours = st.number_input("\uc810심\uc2dc\uac04 (\uc2dc\uac04)", min_value=0.0, max_value=3.0, value=1.0)
start_time = st.time_input("\uc624\ub298 \ucd9c\uadfc\uc2dc\uac04 \uc785력", value=time(hour=9, minute=0))
target_date = st.date_input("\ud2b9\uc815 \ub0a0\uc9dc\uae4c\uc9c0 \ub0a8\uc740 \uadfc\ubb34\uc2dc\uac04 \ud655\uc778", value=None)

# 최규 현재 시간
now = datetime.now(local_timezone)
today = now.date()
st.markdown(f"\ud83d\udd52 **{country_name} \ud604\uc7ac \uc2dc\uac04:** `{now.strftime('%Y-%m-%d %H:%M:%S')}`")

start_datetime = datetime.combine(today, start_time).replace(tzinfo=local_timezone)
end_datetime = start_datetime + timedelta(hours=work_hours_per_day + lunch_break_hours)

if now >= end_datetime:
    today_remaining = 0
else:
    raw_remaining = (end_datetime - now).total_seconds() / 3600
    today_remaining = min(round(raw_remaining, 2), work_hours_per_day)

today_ratio = (today_remaining / work_hours_per_day) * 100 if work_hours_per_day > 0 else 0

# 공휴일
try:
    holiday_list = holidays.CountryHoliday(country_code, years=[today.year, today.year + 1])
except:
    holiday_list = {}
holidays_set = set(holiday_list.keys())

# 근\ubb34일 계산 함수
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
    return f"{h}\uc2dc\uac04 {m}\ubd84"

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

week_ratio = (week_remaining_hours / week_total_hours * 100) if week_total_hours > 0 else 0
month_ratio = (month_remaining_hours / month_total_hours * 100) if month_total_hours > 0 else 0

# \ud45c시
st.subheader("\ud83d\udcca \uc624\ub298 \uae30준 \uadfc\ubb34\uc2dc\uac04")
st.metric("\uc624\ub298 \ub0a8\uc740 \uadfc\ubb34\uc2dc\uac04", f"{format_hours_to_hm(today_remaining)} ({today_ratio:.0f}%)")
st.metric("\uc774\ubcf1\uc8fc \ub0a8\uc740 \uadfc\ubb34\uc2dc\uac04", f"{format_hours_to_hm(week_remaining_hours)} ({week_ratio:.0f}%)")
st.metric("\uc774\ubcf1\ub2ec \ub0a8\uc740 \uadfc\ubb34\uc2dc\uac04", f"{format_hours_to_hm(month_remaining_hours)} ({month_ratio:.0f}%)")

if target_date and target_date > today:
    target_remaining_days = get_remaining_workdays(today, target_date, holidays_set)
    total_days = get_total_workdays(today, target_date, holidays_set)
    target_remaining_hours = today_remaining + work_hours_per_day * target_remaining_days
    total_target_hours = work_hours_per_day * total_days
    target_ratio = (target_remaining_hours / total_target_hours * 100) if total_target_hours > 0 else 0

    st.subheader(f"\ud83d\udcc6 {target_date}\uae4c\uc9c0")
    st.metric("\ub0a8\uc740 \uadfc\ubb34\uc2dc\uac04", f"{format_hours_to_hm(target_remaining_hours)} ({target_ratio:.0f}%)")

# \uacf5통 \uadfc\ubb34\ud604\ud669 \uadf8래프
labels = ["\uc624\ub298", "\uc774\ubcf1\uc8fc", "\uc774\ubcf1\ub2ec"]
worked_hours = [
    round(work_hours_per_day - today_remaining, 2),
    round(week_total_hours - week_remaining_hours, 2),
    round(month_total_hours - month_remaining_hours, 2),
]
remaining_hours = [
    round(today_remaining, 2),
    round(week_remaining_hours, 2),
    round(month_remaining_hours, 2),
]

df = pd.DataFrame({
    "\uadf8\ub8f9": labels * 2,
    "\uc2dc\uac04": worked_hours + remaining_hours,
    "\uc0c1\ud669": ["\uc77c\ud55c\uc2dc\uac04"] * 3 + ["\ub0a8\uc740\uc2dc\uac04"] * 3
})

chart = alt.Chart(df).mark_bar().encode(
    x=alt.X("\uadf8\ub8f9:N", title=None),
    y=alt.Y("\uc2dc\uac04:Q", title="\uadfc\ubb34\uc2dc\uac04"),
    color=alt.Color("\uc0c1\ud669:N", scale=alt.Scale(domain=["\uc77c\ud55c\uc2dc\uac04", "\ub0a8\uc740\uc2dc\uac04"], range=["red", "steelblue"])),
    tooltip=["\uadf8\ub8f9", "\uc0c1\ud669", "\uc2dc\uac04"]
).properties(
    title="\ud83d\udcca \uc77c/\uc8fc/\ub2ec \uadfc\ubb34 \ud604\ud669",
    width=600,
    height=300
)

st.altair_chart(chart, use_container_width=True)
