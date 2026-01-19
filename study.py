import sys
import select
import termios
import tty
import os
import re
import math
from pathlib import Path
from datetime import datetime
from colorama import Fore, Back, Style

# --- CONFIGURATION ---
EXAM_DATE = datetime(2026, 6, 20)
LECTURE_BASE = 10
QUESTION_BASE = 3.33
MAX_MINUTES = 600

confirmationState = False

def get_key():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        if select.select([sys.stdin], [], [], 0.1)[0]:
            return sys.stdin.read(1)
        return None
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

def format_time(total_minutes):
    hours = total_minutes // 60
    minutes = total_minutes % 60
    if hours == 0: return f"{minutes}m"
    return f"{hours}h {minutes}m"

def get_study_goals(days_since_start):
    intensity = 1 / (1 + math.exp(-0.3 * (days_since_start - 12))) 
    scale_factor = intensity * 50 

    if days_since_start == 1:
        lec_time = 15
        q_count = 5
        q_time = 13
    else:
        lec_time = round(LECTURE_BASE * scale_factor)
        q_count = round(QUESTION_BASE * scale_factor)
        q_time = round(q_count * 2.5)

    total = lec_time + q_time

    if total > MAX_MINUTES:
        total = MAX_MINUTES
        lec_time, q_time, q_count = 240, 360, 144
        
    return lec_time, q_count, q_time, total

def draw_row(text, width):
    # 1. Strip ANSI for calculation
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    plain_text = ansi_escape.sub('', text)
    
    # 2. Calculate how many spaces we actually need
    visible_width = len(plain_text)
    total_content_area = width - 4
    
    if visible_width > total_content_area:
        # If text is too long, we clip it (rare, but prevents breaking the box)
        text = text[:total_content_area]
        visible_width = total_content_area

    padding = " " * (total_content_area - visible_width)
    
    # 3. Print with a reset after the text to ensure no color bleeds into the padding
    print(f"{Fore.CYAN}║ {Style.RESET_ALL}{text}{padding} {Fore.CYAN}║")

def get_progress_bar(percent, width=20):
    filled_len = int(width * percent // 100)
    bar = "█" * filled_len + "░" * (width - filled_len)
    return f"[{bar}] {percent}%"

# --- DATA PERSISTENCE ---
FILENAME = "streak_date.txt"
FILEPATH = Path("~/Documents/Python/Studying").expanduser()
ABSPATH = str(FILEPATH) + "/" + FILENAME

ASCII_FILENAME = "ascii.txt"
ASCII_PATH = str(FILEPATH) + "/" + ASCII_FILENAME
ASCII = ""

lines = 45 

def load_ascii():
    global ASCII
    if os.path.exists(ASCII_PATH):
        with open(ASCII_PATH, "r") as f:
            ASCII = f.read()

def save_date(date_obj):
    with open(ABSPATH, "w") as f:
        f.write(date_obj.strftime("%Y-%m-%d"))

def load_date():
    if os.path.exists(ABSPATH):
        with open(ABSPATH, "r") as f:
            return datetime.strptime(f.read().strip(), "%Y-%m-%d")
    else:
        save_date(datetime.now())
    return datetime.now()

def format_exam_countdown(days):
    if days < 30:
        return f"{days} days"
    
    months = days // 30
    rem_days = days % 30
    
    if rem_days == 0:
        return f"{months} month{'s' if months > 1 else ''}"
    
    return f"{months} month{'s' if months > 1 else ''}, {rem_days} day{'s' if rem_days > 1 else ''}"

load_ascii()
streak_date = load_date()

while True:
    os.system("clear")
    today = datetime.now()
    
    streak_days = max(1, (today - streak_date).days + 1)
    days_until_exam = int((EXAM_DATE - today).days)
    time_until_exam = format_exam_countdown(days_until_exam)
    
    lec, q_count, q_time, total = get_study_goals(streak_days)
    intensity_val = round((total/MAX_MINUTES)*100)

    print(Fore.BLUE + ASCII + Style.RESET_ALL)
    
    print(Fore.CYAN + "╔" + "═"*(lines-2) + "╗")
    draw_row(f"SYSTEM STATUS: {today.strftime('%b %d, %Y')}", lines)
    print(Fore.CYAN + "╠" + "═"*(lines-2) + "╣")
    
    draw_row(f"Studying Streak: {streak_days} days", lines)
    draw_row(f"{time_until_exam} left for the exam ({days_until_exam})", lines)
    
    print(Fore.CYAN + "╟" + "─"*(lines-2) + "╢")
    
    draw_row(f"TODAY'S GOAL", lines)
    draw_row(f"Intensity: {get_progress_bar(intensity_val, 20)}", lines)
    
    print(Fore.CYAN + "╟" + "─"*(lines-2) + "╢")
    
    draw_row(f"• Lectures:  {format_time(lec)}", lines)
    draw_row(f"• Questions: {q_count} questions ({format_time(q_time)})", lines)
    draw_row(f"• Total:     {format_time(total)}", lines)
    
    print(Fore.CYAN + "╚" + "═"*(lines-2) + "╝" + Style.RESET_ALL)

    print(f"\n{Fore.WHITE}Options: {Fore.GREEN}[r]{Fore.WHITE} Reset streak | {Fore.RED}[q]{Fore.WHITE} Quit" + Style.RESET_ALL)
    
    while True:
        key = get_key()

        if key == "y" and confirmationState:
            confirmationState = False
            streak_date = datetime.now()
            save_date(streak_date)
            break
        elif key == "n" and confirmationState:
            confirmationState = False
            break

        if key == 'q' and not confirmationState:
            os.system("clear")
            print(Style.RESET_ALL + """> Closed, use the "today" command to view todays program again.""")
            quit()
        elif key == 'r' and not confirmationState:
            confirmationState = True
            os.system("clear")
            print(f"{Fore.BLUE}> {Fore.LIGHTRED_EX}Are you sure you want to reset your streak? {Fore.GREEN}[y]{Fore.CYAN}/{Fore.RED}[n]" + Style.RESET_ALL)