import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff

from dotenv import load_dotenv
import os
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")


# -------------------
# Load Data
# -------------------
df = pd.read_csv("data.csv")
df["Digestive_Issues_Num"] = df["Digestive_Issues"].map({"Yes": 1, "No": 0})

# -------------------
# Sidebar
# -------------------
st.sidebar.title("Snackalyze 🍟")
st.sidebar.write("🍟 Bite. Track. Improve.")
#st.sidebar.write("Analyze your snacking habits & see how fast food impacts your health!")

# Navigation
page = st.sidebar.radio("Navigate", ["Dashboard", "Insights", "Data"])

# -------------------
# Filters
# -------------------
st.sidebar.header("🔍 Filter Data")

# Gender
gender_filter = st.sidebar.selectbox("Gender", options=["All"] + list(df["Gender"].unique()))

# Fast Food Meals/Week
fastfood_range = st.sidebar.slider(
    "Fast Food Meals/Week",
    int(df["Fast_Food_Meals_Per_Week"].min()),
    int(df["Fast_Food_Meals_Per_Week"].max()),
    (int(df["Fast_Food_Meals_Per_Week"].min()), int(df["Fast_Food_Meals_Per_Week"].max()))
)

# Age
age_range = st.sidebar.slider(
    "Age Range",
    int(df["Age"].min()),
    int(df["Age"].max()),
    (int(df["Age"].min()), int(df["Age"].max()))
)

# BMI
bmi_range = st.sidebar.slider(
    "BMI Range",
    float(df["BMI"].min()),
    float(df["BMI"].max()),
    (float(df["BMI"].min()), float(df["BMI"].max()))
)

# Digestive Issues
digestive_filter = st.sidebar.multiselect(
    "Digestive Issues",
    options=["Yes", "No"],
    default=["Yes", "No"]
)

# Energy Level
energy_range = st.sidebar.slider(
    "Energy Level Score",
    int(df["Energy_Level_Score"].min()),
    int(df["Energy_Level_Score"].max()),
    (int(df["Energy_Level_Score"].min()), int(df["Energy_Level_Score"].max()))
)

# Physical Activity Hours
activity_range = st.sidebar.slider(
    "Physical Activity Hours/Week",
    float(df["Physical_Activity_Hours_Per_Week"].min()),
    float(df["Physical_Activity_Hours_Per_Week"].max()),
    (float(df["Physical_Activity_Hours_Per_Week"].min()), float(df["Physical_Activity_Hours_Per_Week"].max()))
)

# Sleep Hours
sleep_range = st.sidebar.slider(
    "Sleep Hours/Day",
    float(df["Sleep_Hours_Per_Day"].min()),
    float(df["Sleep_Hours_Per_Day"].max()),
    (float(df["Sleep_Hours_Per_Day"].min()), float(df["Sleep_Hours_Per_Day"].max()))
)

# -------------------
# Apply Filters
# -------------------
filtered_df = df.copy()
if gender_filter != "All":
    filtered_df = filtered_df[filtered_df["Gender"] == gender_filter]

filtered_df = filtered_df[
    (filtered_df["Fast_Food_Meals_Per_Week"] >= fastfood_range[0]) &
    (filtered_df["Fast_Food_Meals_Per_Week"] <= fastfood_range[1]) &
    (filtered_df["Age"] >= age_range[0]) & (filtered_df["Age"] <= age_range[1]) &
    (filtered_df["BMI"] >= bmi_range[0]) & (filtered_df["BMI"] <= bmi_range[1]) &
    (filtered_df["Digestive_Issues"].isin(digestive_filter)) &
    (filtered_df["Energy_Level_Score"] >= energy_range[0]) & (filtered_df["Energy_Level_Score"] <= energy_range[1]) &
    (filtered_df["Physical_Activity_Hours_Per_Week"] >= activity_range[0]) & (filtered_df["Physical_Activity_Hours_Per_Week"] <= activity_range[1]) &
    (filtered_df["Sleep_Hours_Per_Day"] >= sleep_range[0]) & (filtered_df["Sleep_Hours_Per_Day"] <= sleep_range[1])
]

# -------------------
# Health Risk Score (0–100)
# -------------------
def calculate_health_risk(row):
    score = 0

    # BMI
    if row["BMI"] > 30:
        score += 25
    elif row["BMI"] > 25:
        score += 15
    elif row["BMI"] > 22:
        score += 8

    # Fast food
    if row["Fast_Food_Meals_Per_Week"] > 10:
        score += 20
    elif row["Fast_Food_Meals_Per_Week"] > 6:
        score += 12
    elif row["Fast_Food_Meals_Per_Week"] > 3:
        score += 6

    # Sleep
    if row["Sleep_Hours_Per_Day"] < 5:
        score += 15
    elif row["Sleep_Hours_Per_Day"] < 6:
        score += 10
    elif row["Sleep_Hours_Per_Day"] < 7:
        score += 5

    # Physical activity
    if row["Physical_Activity_Hours_Per_Week"] < 1:
        score += 10
    elif row["Physical_Activity_Hours_Per_Week"] < 3:
        score += 6
    elif row["Physical_Activity_Hours_Per_Week"] < 5:
        score += 3

    # Energy
    if row["Energy_Level_Score"] < 3:
        score += 10
    elif row["Energy_Level_Score"] < 5:
        score += 6
    elif row["Energy_Level_Score"] < 7:
        score += 3

    return min(score, 100)

filtered_df["Health_Risk_Score"] = filtered_df.apply(calculate_health_risk, axis=1)
avg_risk = filtered_df["Health_Risk_Score"].mean()


# -------------------
# Dashboard Page
# -------------------
if page == "Dashboard":
    st.title("🍟 Snackalyze Dashboard")
    st.write("Interactive visualization of fast food consumption and health metrics.")

    st.markdown(
    f"""
    <div style="
        background-color:#f5f7fa;
        padding:10px 15px;
        border-radius:8px;
        margin-bottom:15px;
        font-size:14px;
        color:#333;
    ">
        <b>Active Filters:</b>
        Gender: {gender_filter} |
        Age: {age_range[0]}–{age_range[1]} |
        BMI: {bmi_range[0]}–{bmi_range[1]} |
        Fast Food: {fastfood_range[0]}–{fastfood_range[1]} |
        Digestive Issues: {digestive_filter}
    </div>
    """,
    unsafe_allow_html=True
)

    if len(filtered_df) == 0:
        st.warning("No data available for the selected filters. Try adjusting them.")
        st.stop()


    if len(filtered_df) > 0:
        # BMI vs Fast Food Meals
        st.subheader("Fast Food Meals vs Average BMI")
        fastfood_bmi = filtered_df.groupby("Fast_Food_Meals_Per_Week")["BMI"].mean().reset_index()
        fig_bmi = px.line(fastfood_bmi, x="Fast_Food_Meals_Per_Week", y="BMI",
                          markers=True, line_shape="spline", template="simple_white",
                          title="BMI vs Fast Food Meals")
        st.plotly_chart(fig_bmi, use_container_width=True)

        # -------------------
        # Health Risk Indicator
        # -------------------
        avg_fastfood = filtered_df["Fast_Food_Meals_Per_Week"].mean()
        avg_bmi = filtered_df["BMI"].mean()

        if avg_fastfood > 10 and avg_bmi > 27:
            risk = "🔴 High Risk"
            risk_msg = "High fast food intake and BMI detected. Consider lifestyle changes."
        elif (6 <= avg_fastfood <= 10) or (24 <= avg_bmi <= 27):
            risk = "🟡 Moderate Risk"
            risk_msg = "Moderate health risk. Small improvements can make a big difference."
        else:
            risk = "🟢 Low Risk"
            risk_msg = "Great balance! Your habits look healthy."

        st.markdown(
            f"""
            <div style="
                background: linear-gradient(135deg, #fdfbfb, #ebedee);
                padding: 20px;
                border-radius: 16px;
                box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
                text-align: center;
                margin-bottom: 20px;
            ">
                <h2>{risk}</h2>
                <p style="font-size:16px;">{risk_msg}</p>
                <p style="color:gray;">
                    Avg Fast Food Meals: {avg_fastfood:.1f} | Avg BMI: {avg_bmi:.1f}
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        # -------------------
        # Health Risk Score UI
        # -------------------
        st.subheader("🚨 Health Risk Score")

        if avg_risk < 40:
            color = "#2ecc71"
            level = "Low Risk 🟢"
        elif avg_risk < 70:
            color = "#f1c40f"
            level = "Moderate Risk 🟡"
        else:
            color = "#e74c3c"
            level = "High Risk 🔴"

        st.markdown(
            f"""
            <div style="
                background-color:{color};
                padding:20px;
                border-radius:15px;
                color:white;
                text-align:center;
                font-size:22px;
                box-shadow:0px 4px 12px rgba(0,0,0,0.2);
                margin-bottom:20px;
            ">
                Health Risk Score: {round(avg_risk,1)} / 100  
                <br><b>{level}</b>
            </div>
            """,
            unsafe_allow_html=True
        )

                



        # Calories vs Fast Food Meals
        st.subheader("Fast Food Meals vs Average Daily Calories")
        fastfood_cal = filtered_df.groupby("Fast_Food_Meals_Per_Week")["Average_Daily_Calories"].mean().reset_index()
        fig_cal = px.line(fastfood_cal, x="Fast_Food_Meals_Per_Week", y="Average_Daily_Calories",
                          markers=True, line_shape="spline", template="simple_white",
                          title="Calories Intake vs Fast Food Meals")
        st.plotly_chart(fig_cal, use_container_width=True)

        # Energy vs Sleep Scatter
        st.subheader("Energy Level vs Sleep Hours")
        fig_energy = px.scatter(filtered_df, x="Sleep_Hours_Per_Day", y="Energy_Level_Score",
                                color="Fast_Food_Meals_Per_Week",
                                size="Physical_Activity_Hours_Per_Week",
                                hover_data=["Age", "Gender"],
                                template="simple_white",
                                title="Energy vs Sleep Hours (Color = Fast Food Meals)")
        st.plotly_chart(fig_energy, use_container_width=True)

        # Metrics
        col1, col2, col3 = st.columns(3)
        highest_bmi = fastfood_bmi.loc[fastfood_bmi['BMI'].idxmax()]
        lowest_bmi = fastfood_bmi.loc[fastfood_bmi['BMI'].idxmin()]
        avg_energy = filtered_df["Energy_Level_Score"].mean()
        col1.metric("Highest BMI", f"{round(highest_bmi['BMI'],2)} at {highest_bmi['Fast_Food_Meals_Per_Week']} meals/week")
        col2.metric("Lowest BMI", f"{round(lowest_bmi['BMI'],2)} at {lowest_bmi['Fast_Food_Meals_Per_Week']} meals/week")
        col3.metric("Average Energy", round(avg_energy,2))

        st.subheader("🧠 Smart Health Insights (AI Powered)")

if st.button("Generate AI Health Insight"):
    summary = f"""
    Average fast food meals per week: {round(avg_fastfood,2)}
    Average BMI: {round(avg_bmi,2)}
    Average energy level: {round(avg_energy,2)}
    Average sleep hours: {round(filtered_df["Sleep_Hours_Per_Day"].mean(),2)}
    Average physical activity hours: {round(filtered_df["Physical_Activity_Hours_Per_Week"].mean(),2)}
    """

    prompt = f"""
You are a friendly AI health coach.

From the data below, generate exactly 2 short, motivating, and practical health tips.
Each tip must be:
- One sentence only
- Actionable
- Written in a positive tone
- Start with an emoji

Data:
{summary}
"""


    with st.spinner("Thinking like a nutritionist 🧠🥗..."):
        response = model.generate_content(prompt)

        st.success("AI Insight Generated!")
        tips = response.text.strip().split("\n")

        st.markdown(
            f"""
            <div style="
                background: linear-gradient(135deg, #fbc2eb, #a6c1ee);
                padding:20px;
                border-radius:15px;
                box-shadow:0px 6px 18px rgba(0,0,0,0.15);
                font-size:16px;
            ">
            <h4>📌 Auto Generated Insights</h4>
            {"".join([f"<p>• {tip}</p>" for tip in tips if tip.strip()])}
            </div>
            """,
            unsafe_allow_html=True
        )




# -------------------
# Insights Page
# -------------------
elif page == "Insights":
    st.title("🩺 Health Insights")
    st.write("Analysis of digestive issues, doctor visits, and overall health scores.")

    st.markdown(
    f"""
    <div style="
        background-color:#f5f7fa;
        padding:10px 15px;
        border-radius:8px;
        margin-bottom:15px;
        font-size:14px;
        color:#333;
    ">
        <b>Active Filters:</b>
        Gender: {gender_filter} |
        Age: {age_range[0]}–{age_range[1]} |
        BMI: {bmi_range[0]}–{bmi_range[1]} |
        Fast Food: {fastfood_range[0]}–{fastfood_range[1]} |
        Digestive Issues: {digestive_filter}
    </div>
    """,
    unsafe_allow_html=True
)

    if len(filtered_df) == 0:
        st.warning("No data available for the selected filters. Try adjusting them.")
        st.stop()


    if len(filtered_df) > 0:
        # Digestive Issues Pie Chart
        st.subheader("Digestive Issues Distribution")
        pie_data = filtered_df["Digestive_Issues"].value_counts()
        fig_pie = px.pie(names=pie_data.index, values=pie_data.values,
                         template="simple_white", title="Digestive Issues Distribution",
                         color_discrete_sequence=["#1f77b4","#ff7f0e"])
        st.plotly_chart(fig_pie, use_container_width=True)

        # Digestive Issues vs Doctor Visits
        st.subheader("Digestive Issues vs Doctor Visits")
        digestive_visits = filtered_df.groupby("Digestive_Issues")["Doctor_Visits_Per_Year"].mean().reset_index()
        fig_bar = px.bar(digestive_visits, x="Digestive_Issues", y="Doctor_Visits_Per_Year",
                         template="simple_white", color="Doctor_Visits_Per_Year",
                         color_continuous_scale=px.colors.sequential.Blues,
                         title="Doctor Visits by Digestive Issues")
        st.plotly_chart(fig_bar, use_container_width=True)

        # Average Health Score
        st.subheader("Overall Health Score (0-10)")
        avg_health = filtered_df["Overall_Health_Score"].mean()
        st.metric("Average Health Score", round(avg_health,2))

# -------------------
# Data Page
# -------------------
else:
    
    st.title("📊 Dataset Preview")
    st.markdown(
    f"""
    <div style="
        background-color:#f5f7fa;
        padding:10px 15px;
        border-radius:8px;
        margin-bottom:15px;
        font-size:14px;
        color:#333;
    ">
        <b>Active Filters:</b>
        Gender: {gender_filter} |
        Age: {age_range[0]}–{age_range[1]} |
        BMI: {bmi_range[0]}–{bmi_range[1]} |
        Fast Food: {fastfood_range[0]}–{fastfood_range[1]} |
        Digestive Issues: {digestive_filter}
    </div>
    """,
    unsafe_allow_html=True
)

    if len(filtered_df) == 0:
        st.warning("No data available for the selected filters. Try adjusting them.")
        st.stop()

    st.dataframe(filtered_df)
    st.write(f"Total records: {len(filtered_df)}")
    st.download_button(
        "Download Filtered Data",
        data=filtered_df.to_csv(index=False),
        file_name="filtered_snackalyze_data.csv",
        mime="text/csv"
    )

    
