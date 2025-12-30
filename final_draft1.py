import streamlit as st
import data
import pandas as pd
from gtts import gTTS
import base64
import io

# 1. Page Configuration
st.set_page_config(page_title="College Assistant", page_icon="🎓", layout="wide")

# --- VOICE FUNCTION ---
def speak_text(text):
    """Converts text to speech and plays it automatically."""
    try:
        clean_text = text.split(".")[0]
        tts = gTTS(text=clean_text, lang='en')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        b64 = base64.b64encode(fp.read()).decode()
        md = f"""<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>"""
        st.markdown(md, unsafe_allow_html=True)
    except Exception:
        pass

# --- UI RENDERER: COLLEGE INFO ---
def show_college_info():
    """Renders institution details."""
    st.header("🏫 Institution Details")
    st.info(f"**College Name:** {data.college_data['College name']}")
    st.info(f"**Location:** {data.college_data['Location']}")
    st.subheader("Departments")
    for dept in data.college_data['department']:
        st.write(f"- {dept}")

# --- AI LOGIC ENGINE ---
def get_ai_response(user_input):
    """Processes typed commands and returns text plus a UI component."""
    user_input_clean = user_input.lower().replace(" ", "") 
    
    if "collegeinfo" in user_input_clean or "institution" in user_input_clean:
        return "Showing the institution details for KIT.", "college_info"

    if "classtimetable" in user_input_clean or "csetimetable" in user_input_clean:
        rows = []
        for day, classes in data.time_table_of_cse.items():
            for entry in classes:
                if ":" in entry:
                    time_part, subject_part = entry.rsplit(":", 1)
                    rows.append({"DAY": day.strip(), "Time": time_part.strip(), "Subject": subject_part.strip()})
        df_raw = pd.DataFrame(rows)
        day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        time_order = ["9 AM", "10 AM", "11:15 AM", "12:15 PM", "2:15 PM"]
        df_pivoted = df_raw.pivot_table(index="DAY", columns="Time", values="Subject", aggfunc=lambda x: ' / '.join(x))
        df_pivoted = df_pivoted.reindex(index=day_order, columns=time_order).fillna("•")
        return "Here is your timetable in the correct order:", df_pivoted

    if "labschedule" in user_input_clean or "labs" in user_input_clean:
        lab_rows = []
        for day, labs in data.lab_timetable.items():
            for entry in labs:
                if ":" in entry:
                    time_part, lab_part = entry.rsplit(":", 1)
                    lab_rows.append({"DAY": day.strip(), "Time": time_part.strip(), "Subject": lab_part.strip()})
        df_labs = pd.DataFrame(lab_rows)
        day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        df_pivoted = df_labs.pivot_table(index="DAY", columns="Time", values="Subject", aggfunc=lambda x: ' | '.join(x))
        df_pivoted = df_pivoted.reindex(index=day_order).fillna("•")
        return "Showing the Lab Schedule grid.", df_pivoted

    if "studentlist" in user_input_clean:
        if "csea" in user_input_clean or "sectiona" in user_input_clean:
            df = pd.DataFrame(data.cse_a, columns=["Student Name (Section A)"])
            df.index = df.index + 1
            return f"Found {len(data.cse_a)} students in CSE-A.", df
        elif "cseb" in user_input_clean or "sectionb" in user_input_clean:
            df = pd.DataFrame(data.cse_b, columns=["Student Name (Section B)"])
            df.index = df.index + 1
            return f"Found {len(data.cse_b)} students in CSE-B.", df
        elif "csec" in user_input_clean or "sectionc" in user_input_clean:
            df = pd.DataFrame(data.cse_c, columns=["Student Name (Section C)"])
            df.index = df.index + 1
            return f"Found {len(data.cse_c)} students in CSE-C.", df
        else:
            return "Please specify: 'CSE A Student List', 'CSE B Student List', or 'CSE C Student List'.", None

    for student in data.cse_a:
        if student.lower().replace(" ", "") in user_input_clean:
            return f"Yes, **{student}** is a registered student in **CSE-A**.", None
    for student in data.cse_b:
        if student.lower().replace(" ", "") in user_input_clean:
            return f"Yes, **{student}** is a registered student in **CSE-B**.", None
    for student in data.cse_c:
        if student.lower().replace(" ", "") in user_input_clean:
            return f"Yes, **{student}** is a registered student in **CSE-C**.", None

    return "I'm not sure. Type 'College Info', 'CSE A Student List', or search a classmate's name.", None

# --- SIDEBAR CONFIGURATION ---
with st.sidebar:
    st.title("🎓 College Assistant")
    st.write("---")
    
    # HELP COMMANDS (Top)
    st.header("❓ Help & Commands")
    st.markdown("""
    Type these in the chat:
    - **'College Info'**
    - **'CSE Timetable'**
    - **'Lab Schedule'**
    - **'CSE A Student List'** (A, B, or C)
    - **'Search [Name]'** (e.g., search Name)
    """)
    st.write("---")
    
    # ADMIN PANEL (Middle)
    st.header("🛠️ Admin Panel")
    section_choice = st.selectbox("Select Section:", ["CSE-A", "CSE-B", "CSE-C"])
    new_name = st.text_input("Add New Student Name:")
    if st.button("Update data.py"):
        if new_name:
            if section_choice == "CSE-A": data.cse_a.append(new_name)
            elif section_choice == "CSE-B": data.cse_b.append(new_name)
            else: data.cse_c.append(new_name)
            with open("data.py", "w") as f:
                f.write(f"college_data = {repr(data.college_data)}\n\n")
                f.write(f"time_table_of_cse = {repr(data.time_table_of_cse)}\n\n")
                f.write(f"lab_timetable = {repr(data.lab_timetable)}\n\n")
                f.write(f"exam_schedule = {repr(data.exam_schedule)}\n\n")
                f.write(f"classderooms = {repr(data.classderooms)}\n\n")
                f.write(f"cse_a = {repr(data.cse_a)}\n\n")
                f.write(f"cse_b = {repr(data.cse_b)}\n\n")
                f.write(f"cse_c = {repr(data.cse_c)}\n")
            st.success(f"Updated {section_choice}!")
            st.rerun()
    
    # PROJECT CREATORS (Bottom)
    st.write("---")
    st.subheader("👨‍💻 Project Creators")
    st.info("Made by:")
    st.write("- **Darshan HS**")
    st.write("- **Deekshith RK**")
    st.write("- **Gourav N Gowda**")
    st.write("- **K Manoj Kumar**")

# --- MAIN INTERFACE ---
st.title("🎓 College Assistant")
st.write("---")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        ui = message.get("type")
        if isinstance(ui, str) and ui == "college_info": show_college_info()
        elif isinstance(ui, pd.DataFrame): st.table(ui)

if prompt := st.chat_input("Ask about timetable, sections, or students..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    response_text, ui_type = get_ai_response(prompt)
    with st.chat_message("assistant"):
        st.markdown(response_text)
        if isinstance(ui_type, str) and ui_type == "college_info": show_college_info()
        elif isinstance(ui_type, pd.DataFrame): st.table(ui_type)
        speak_text(response_text)
    st.session_state.messages.append({"role": "assistant", "content": response_text, "type": ui_type})