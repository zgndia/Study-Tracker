import math, os

# --- CONFIGURATION ---
LECTURE_BASE = 10
QUESTION_BASE = 3.33
MAX_MINUTES = 600

# --- THE ENGINE (Lambda) ---
# Returns: (lec_min, q_count, q_min, total_min)
calc_study = lambda d: (
    (15, 5, 13, 28) if d == 1 else (
        lambda scale: (
            lambda l, q, qt: (240, 144, 360, 600) if (l + qt) > MAX_MINUTES else (l, q, qt, l + qt)
        )(round(LECTURE_BASE * scale), round(QUESTION_BASE * scale), round(round(QUESTION_BASE * scale) * 2.5))
    )(50 / (1 + math.exp(-0.3 * (d - 12))))
)

aliases = ["q","quit","exit"]

def format_time(total_minutes):
    hours = total_minutes // 60
    minutes = total_minutes % 60
    return f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"

def frontpage():
    print("--- STUDY GOAL FORECASTER ---")
    print("Enter a day number to see the projected workload.")
    print("Type 'q' to close.\n")

def main():
    os.system("clear")
    frontpage()

    while True:
        user_input = input("Target Day > ").lower()
        
        if user_input.isalpha() and any(user_input.lower() == alias for alias in aliases):
            os.system("clear")
            break
            
        try:
            day = int(user_input)
            if day < 1:
                print("Please enter a day greater than 0.")
                continue
                
            lec, q_cnt, q_tm, total = calc_study(day)

            os.system("clear")
            frontpage()
            
            print(f"\n[ RESULTS FOR DAY {day} ]")
            print(f"Status:    (Intensity: {round((total/MAX_MINUTES)*100)}%)")
            print(f"Lectures:  {format_time(lec)}")
            print(f"Questions: {q_cnt} questions ({format_time(q_tm)})")
            print(f"Total:     {format_time(total)}")
            print("-" * 25 + "\n")
            
        except ValueError:
            print("Invalid input. Please enter a number.")

if __name__ == "__main__":
    main()