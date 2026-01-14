# ai_clinic_timesaver.py
import streamlit as st
import pandas as pd
import numpy as np
from fpdf import FPDF
import plotly.express as px
import os
import openai
import json

# --- Set your OpenAI API key ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# --- Page config ---
st.set_page_config(page_title="AI Clinic Time-Saver", layout="wide")

# --- Custom CSS for unified maroon/black theme ---
st.markdown("""
<style>
/* Page background */
.stApp { background-color: #f7f7f7; }

/* Buttons (Download PDF, Social, Sign-up) */
div.stButton > button {
    background-color: black !important;  /* Black background */
    color: white !important;             /* White text */
    border-radius: 8px;
    height: 3em;
    width: 100%;
    font-size: 16px;
}

/* Sidebar & input labels */
label, input {
    color: #800000;
    font-weight: bold;
}

/* Number inputs text */
input[type="number"] {
    color: white !important;
    background-color: black !important;
    border-radius: 5px;
    padding: 4px;
}

/* Headings & text */
h1, h2, p, span, label {
    color: #800000 !important;
}

/* Hide Streamlit warnings' yellow boxes */
.css-1y4p8pa { background-color: transparent !important; color: #800000 !important; }
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown('<h1>AI Clinic Time-Saver</h1>', unsafe_allow_html=True)
st.markdown('<p>Estimate how much time AI could save your clinic in administrative tasks!<br>'
            'Enter your clinic details below to get personalized insights.</p>', unsafe_allow_html=True)

# --- Input Section ---
st.markdown('<h2>Clinic Details</h2>', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
with col1:
    clinic_size = st.number_input("Number of clinicians", min_value=1, max_value=100, value=5)
with col2:
    patients_per_week = st.number_input("Average patients per week", min_value=10, max_value=1000, value=200)
with col3:
    admin_hours_per_week = st.number_input("Admin hours per clinician per week", min_value=1, max_value=50, value=10)

# --- GPT-generated AI Insights with fallback ---
st.markdown('<h2>AI Insights</h2>', unsafe_allow_html=True)

prompt = f"""
You are a helpful assistant. Given a clinic with {clinic_size} clinicians, each seeing {patients_per_week} patients per week,
and spending {admin_hours_per_week} hours per week on administrative tasks, estimate:
1. Time saved per clinician per week if AI is applied (in hours, decimal allowed)
2. Total admin time saved for the whole clinic per week
3. Suggest a small personalized tip to save time

Return the results in JSON format with keys: time_saved_per_week, total_time_saved, tip
"""

def get_ai_insights():
    if client:
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful healthcare AI assistant."},
                    {"role": "user", "content": prompt}
                ]
            )
            gpt_output = response.choices[0].message.content
            insights = json.loads(gpt_output)
            return insights
        except Exception as e:
            st.markdown(f'<span>OpenAI API unavailable, using fallback values. ({e})</span>', unsafe_allow_html=True)
    # fallback values
    time_saved_per_week = admin_hours_per_week * np.random.uniform(0.25, 0.45)
    total_time_saved = time_saved_per_week * clinic_size
    tip = "Consider delegating repetitive admin tasks to save time."
    return {
        "time_saved_per_week": time_saved_per_week,
        "total_time_saved": total_time_saved,
        "tip": tip
    }

insights = get_ai_insights()
time_saved_per_week = insights["time_saved_per_week"]
total_time_saved = insights["total_time_saved"]
tip = insights["tip"]

st.markdown(f"<b>Estimated admin time saved per clinician per week:</b> {time_saved_per_week:.1f} hours", unsafe_allow_html=True)
st.markdown(f"<b>Total admin time saved for clinic per week:</b> {total_time_saved:.1f} hours", unsafe_allow_html=True)
st.markdown(f"<b>Quick Tip:</b> {tip}", unsafe_allow_html=True)

# --- Charts ---
st.markdown('<h2>Visualized Savings</h2>', unsafe_allow_html=True)
df = pd.DataFrame({
    "Clinician": [f"Clinician {i+1}" for i in range(clinic_size)],
    "Hours Saved": np.random.uniform(time_saved_per_week*0.8, time_saved_per_week*1.2, size=clinic_size)
})

fig = px.bar(
    df,
    x="Clinician",
    y="Hours Saved",
    color_discrete_sequence=['#800000'],
    text='Hours Saved'
)
fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
fig.update_layout(
    plot_bgcolor='black',
    paper_bgcolor='black',
    font_color='#800000',
    xaxis=dict(title="Clinician", color="white"),
    yaxis=dict(title="Hours Saved", color="white")
)
st.plotly_chart(fig, use_container_width=True)

# --- PDF download function ---
def create_pdf(clinic_size, patients_per_week, admin_hours_per_week, time_saved_per_week, total_time_saved, tip, df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.set_text_color(128,0,0)
    pdf.cell(0, 10, "AI Clinic Time-Saver Report", ln=True, align="C")
    pdf.ln(5)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Number of clinicians: {clinic_size}", ln=True)
    pdf.cell(0, 10, f"Average patients per week: {patients_per_week}", ln=True)
    pdf.cell(0, 10, f"Admin hours per clinician per week: {admin_hours_per_week}", ln=True)
    pdf.cell(0, 10, f"Estimated admin time saved per clinician per week: {time_saved_per_week:.1f} hours", ln=True)
    pdf.cell(0, 10, f"Total admin time saved for clinic per week: {total_time_saved:.1f} hours", ln=True)
    pdf.cell(0, 10, f"Quick Tip: {tip}", ln=True)
    pdf.ln(5)
    pdf.cell(0, 10, "Visualized Savings:", ln=True)
    for i, row in df.iterrows():
        pdf.cell(0, 8, f"{row['Clinician']}: {row['Hours Saved']:.1f} hours saved", ln=True)
    pdf_bytes = pdf.output(dest='S').encode('latin1')
    return pdf_bytes

pdf_file = create_pdf(clinic_size, patients_per_week, admin_hours_per_week, time_saved_per_week, total_time_saved, tip, df)
st.download_button(
    label="📄 Download PDF Report",
    data=pdf_file,
    file_name="ai_clinic_timesaver_report.pdf",
    mime="application/pdf"
)

# --- Call to Action ---
st.markdown('<h2>Take the Next Step</h2>', unsafe_allow_html=True)
st.markdown('<p>Sign up for Heidi to get full AI integration for your clinic and start saving time today!</p>', unsafe_allow_html=True)
if st.button("Sign Up for Heidi"):
    st.success("🎉 Thanks! A signup link has been sent to your email (simulated).")

# --- Social Share Simulation ---
st.markdown('<p>Or share this tool with your colleagues:</p>', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Share on LinkedIn"): st.info("✅ LinkedIn share simulated!")
with col2:
    if st.button("Share on Twitter"): st.info("✅ Twitter share simulated!")
with col3:
    if st.button("Copy Referral Link"): st.info("✅ Referral link copied (simulated)!")
