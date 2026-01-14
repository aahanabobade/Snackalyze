import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from dotenv import load_dotenv
import os
import google.generativeai as genai

# =============================================================================
# CONFIGURATION
# =============================================================================
st.set_page_config(
    page_title="Snackalyze - Health Analytics",
    page_icon="🍟",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

# =============================================================================
# CUSTOM CSS
# =============================================================================
def load_custom_css():
    st.markdown("""
        <style>
        /* Main container styling */
        .main {
            padding: 0rem 1rem;
        }
        
        /* Custom navbar */
        .navbar {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1rem 2rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .navbar-title {
            color: white;
            font-size: 2rem;
            font-weight: bold;
            margin: 0;
            text-align: center;
        }
        
        .navbar-subtitle {
            color: rgba(255,255,255,0.9);
            font-size: 1rem;
            text-align: center;
            margin-top: 0.5rem;
        }
        
        /* Card styling */
        .metric-card {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-left: 4px solid #667eea;
            margin-bottom: 1rem;
        }
        
        .metric-card h3 {
            color: #667eea;
            margin-top: 0;
            font-size: 1.2rem;
        }
        
        .metric-value {
            font-size: 2rem;
            font-weight: bold;
            color: #333;
        }
        
        /* Filter section */
        .filter-badge {
            background-color: #f0f2f6;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            display: inline-block;
            margin: 0.25rem;
            font-size: 0.85rem;
            color: #555;
        }
        
        /* Risk indicators */
        .risk-low {
            background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
            color: white;
        }
        
        .risk-moderate {
            background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
            color: #333;
        }
        
        .risk-high {
            background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
            color: white;
        }
        
        /* Button styling */
        .stButton>button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.5rem 2rem;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        
        /* Sidebar styling */
        .css-1d391kg {
            background-color: #f8f9fa;
        }
        
        /* Section headers */
        .section-header {
            color: #667eea;
            font-size: 1.5rem;
            font-weight: bold;
            margin-top: 2rem;
            margin-bottom: 1rem;
            border-bottom: 2px solid #667eea;
            padding-bottom: 0.5rem;
        }
        
        /* Info boxes */
        .info-box {
            background: linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%);
            padding: 1.5rem;
            border-radius: 10px;
            border-left: 4px solid #667eea;
            margin: 1rem 0;
        }
        
        /* AI insight box */
        .ai-insight {
            background: linear-gradient(135deg, #fbc2eb 0%, #a6c1ee 100%);
            padding: 1.5rem;
            border-radius: 15px;
            box-shadow: 0 6px 18px rgba(0,0,0,0.15);
            margin: 1rem 0;
        }
        
        .ai-insight h4 {
            margin-top: 0;
            color: #333;
        }
        
        /* Tabs styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 1rem 2rem;
            border-radius: 8px 8px 0 0;
        }
        
        </style>
    """, unsafe_allow_html=True)

# =============================================================================
# DATA LOADING AND PROCESSING
# =============================================================================
@st.cache_data
def load_data():
    """Load and preprocess the dataset"""
    df = pd.read_csv("data.csv")
    df["Digestive_Issues_Num"] = df["Digestive_Issues"].map({"Yes": 1, "No": 0})
    return df

def calculate_health_risk(row):
    """Calculate health risk score (0-100) based on multiple factors"""
    score = 0
    
    # BMI contribution
    if row["BMI"] > 30:
        score += 25
    elif row["BMI"] > 25:
        score += 15
    elif row["BMI"] > 22:
        score += 8
    
    # Fast food contribution
    if row["Fast_Food_Meals_Per_Week"] > 10:
        score += 20
    elif row["Fast_Food_Meals_Per_Week"] > 6:
        score += 12
    elif row["Fast_Food_Meals_Per_Week"] > 3:
        score += 6
    
    # Sleep contribution
    if row["Sleep_Hours_Per_Day"] < 5:
        score += 15
    elif row["Sleep_Hours_Per_Day"] < 6:
        score += 10
    elif row["Sleep_Hours_Per_Day"] < 7:
        score += 5
    
    # Physical activity contribution
    if row["Physical_Activity_Hours_Per_Week"] < 1:
        score += 10
    elif row["Physical_Activity_Hours_Per_Week"] < 3:
        score += 6
    elif row["Physical_Activity_Hours_Per_Week"] < 5:
        score += 3
    
    # Energy level contribution
    if row["Energy_Level_Score"] < 3:
        score += 10
    elif row["Energy_Level_Score"] < 5:
        score += 6
    elif row["Energy_Level_Score"] < 7:
        score += 3
    
    return min(score, 100)

def apply_filters(df, filters):
    """Apply all selected filters to the dataframe"""
    filtered_df = df.copy()
    
    if filters['gender'] != "All":
        filtered_df = filtered_df[filtered_df["Gender"] == filters['gender']]
    
    filtered_df = filtered_df[
        (filtered_df["Fast_Food_Meals_Per_Week"] >= filters['fastfood'][0]) &
        (filtered_df["Fast_Food_Meals_Per_Week"] <= filters['fastfood'][1]) &
        (filtered_df["Age"] >= filters['age'][0]) &
        (filtered_df["Age"] <= filters['age'][1]) &
        (filtered_df["BMI"] >= filters['bmi'][0]) &
        (filtered_df["BMI"] <= filters['bmi'][1]) &
        (filtered_df["Digestive_Issues"].isin(filters['digestive'])) &
        (filtered_df["Energy_Level_Score"] >= filters['energy'][0]) &
        (filtered_df["Energy_Level_Score"] <= filters['energy'][1]) &
        (filtered_df["Physical_Activity_Hours_Per_Week"] >= filters['activity'][0]) &
        (filtered_df["Physical_Activity_Hours_Per_Week"] <= filters['activity'][1]) &
        (filtered_df["Sleep_Hours_Per_Day"] >= filters['sleep'][0]) &
        (filtered_df["Sleep_Hours_Per_Day"] <= filters['sleep'][1])
    ]
    
    return filtered_df

# =============================================================================
# UI COMPONENTS
# =============================================================================
def render_navbar():
    """Render the top navbar"""
    st.markdown("""
        <div class="navbar">
            <h1 class="navbar-title">🍟 Snackalyze</h1>
            <p class="navbar-subtitle">Bite. Track. Improve. | Analyze your snacking habits & health metrics</p>
        </div>
    """, unsafe_allow_html=True)

def render_filter_summary(filters):
    """Display active filters as badges"""
    st.markdown(f"""
        <div style="margin-bottom: 1.5rem;">
            <span class="filter-badge">👤 Gender: {filters['gender']}</span>
            <span class="filter-badge">🎂 Age: {filters['age'][0]}–{filters['age'][1]}</span>
            <span class="filter-badge">⚖️ BMI: {filters['bmi'][0]:.1f}–{filters['bmi'][1]:.1f}</span>
            <span class="filter-badge">🍔 Fast Food: {filters['fastfood'][0]}–{filters['fastfood'][1]}/week</span>
            <span class="filter-badge">🔬 Digestive: {', '.join(filters['digestive'])}</span>
        </div>
    """, unsafe_allow_html=True)

def render_health_risk_indicator(avg_risk):
    """Display the overall health risk score"""
    if avg_risk < 40:
        color_class = "risk-low"
        level = "Low Risk 🟢"
        emoji = "✅"
    elif avg_risk < 70:
        color_class = "risk-moderate"
        level = "Moderate Risk 🟡"
        emoji = "⚠️"
    else:
        color_class = "risk-high"
        level = "High Risk 🔴"
        emoji = "🚨"
    
    st.markdown(f"""
        <div class="{color_class}" style="
            padding: 2rem;
            border-radius: 15px;
            text-align: center;
            font-size: 1.3rem;
            box-shadow: 0px 4px 12px rgba(0,0,0,0.2);
            margin: 2rem 0;
        ">
            <div style="font-size: 3rem; margin-bottom: 0.5rem;">{emoji}</div>
            <div style="font-size: 2.5rem; font-weight: bold;">{round(avg_risk, 1)}/100</div>
            <div style="font-size: 1.2rem; margin-top: 0.5rem;"><b>{level}</b></div>
        </div>
    """, unsafe_allow_html=True)

# =============================================================================
# PAGE COMPONENTS
# =============================================================================
def render_dashboard(filtered_df, filters):
    """Render the main dashboard page"""
    st.markdown('<h2 class="section-header">📊 Dashboard Overview</h2>', unsafe_allow_html=True)
    
    render_filter_summary(filters)
    
    if len(filtered_df) == 0:
        st.warning("⚠️ No data available for the selected filters. Try adjusting them.")
        return
    
    # Calculate health risk
    filtered_df["Health_Risk_Score"] = filtered_df.apply(calculate_health_risk, axis=1)
    avg_risk = filtered_df["Health_Risk_Score"].mean()
    
    # Top metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_fastfood = filtered_df["Fast_Food_Meals_Per_Week"].mean()
        st.markdown(f"""
            <div class="metric-card">
                <h3>🍔 Fast Food</h3>
                <div class="metric-value">{avg_fastfood:.1f}</div>
                <p style="color: #666; margin: 0;">meals/week</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        avg_bmi = filtered_df["BMI"].mean()
        st.markdown(f"""
            <div class="metric-card">
                <h3>⚖️ Average BMI</h3>
                <div class="metric-value">{avg_bmi:.1f}</div>
                <p style="color: #666; margin: 0;">body mass index</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        avg_energy = filtered_df["Energy_Level_Score"].mean()
        st.markdown(f"""
            <div class="metric-card">
                <h3>⚡ Energy Level</h3>
                <div class="metric-value">{avg_energy:.1f}/10</div>
                <p style="color: #666; margin: 0;">average score</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        avg_sleep = filtered_df["Sleep_Hours_Per_Day"].mean()
        st.markdown(f"""
            <div class="metric-card">
                <h3>😴 Sleep</h3>
                <div class="metric-value">{avg_sleep:.1f}h</div>
                <p style="color: #666; margin: 0;">per day</p>
            </div>
        """, unsafe_allow_html=True)
    
    # Health Risk Indicator
    st.markdown('<h3 class="section-header">🚨 Health Risk Assessment</h3>', unsafe_allow_html=True)
    render_health_risk_indicator(avg_risk)
    
    # Risk message
    if avg_fastfood > 10 and avg_bmi > 27:
        risk_msg = "⚠️ High fast food intake and elevated BMI detected. Consider lifestyle changes to reduce health risks."
    elif (6 <= avg_fastfood <= 10) or (24 <= avg_bmi <= 27):
        risk_msg = "💡 Moderate health risk detected. Small improvements in diet and activity can make a big difference."
    else:
        risk_msg = "✅ Great balance! Your current habits look healthy. Keep up the good work!"
    
    st.info(risk_msg)
    
    # Charts section
    st.markdown('<h3 class="section-header">📈 Health Trends</h3>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # BMI vs Fast Food
        fastfood_bmi = filtered_df.groupby("Fast_Food_Meals_Per_Week")["BMI"].mean().reset_index()
        fig_bmi = px.line(
            fastfood_bmi, 
            x="Fast_Food_Meals_Per_Week", 
            y="BMI",
            markers=True, 
            line_shape="spline",
            title="📊 BMI vs Fast Food Consumption"
        )
        fig_bmi.update_traces(line_color='#667eea', marker=dict(size=8, color='#764ba2'))
        fig_bmi.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family="Arial", size=12),
            title_font_size=16
        )
        st.plotly_chart(fig_bmi, use_container_width=True)
    
    with col2:
        # Calories vs Fast Food
        fastfood_cal = filtered_df.groupby("Fast_Food_Meals_Per_Week")["Average_Daily_Calories"].mean().reset_index()
        fig_cal = px.line(
            fastfood_cal, 
            x="Fast_Food_Meals_Per_Week", 
            y="Average_Daily_Calories",
            markers=True, 
            line_shape="spline",
            title="🔥 Daily Calories vs Fast Food"
        )
        fig_cal.update_traces(line_color='#f093fb', marker=dict(size=8, color='#f5576c'))
        fig_cal.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family="Arial", size=12),
            title_font_size=16
        )
        st.plotly_chart(fig_cal, use_container_width=True)
    
    # Energy vs Sleep Scatter
    st.markdown("### 😴 Energy & Sleep Correlation")
    fig_energy = px.scatter(
        filtered_df, 
        x="Sleep_Hours_Per_Day", 
        y="Energy_Level_Score",
        color="Fast_Food_Meals_Per_Week",
        size="Physical_Activity_Hours_Per_Week",
        hover_data=["Age", "Gender", "BMI"],
        title="Energy Level vs Sleep Hours (sized by physical activity)",
        color_continuous_scale="Viridis"
    )
    fig_energy.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Arial", size=12),
        title_font_size=16
    )
    st.plotly_chart(fig_energy, use_container_width=True)
    
    # AI Insights
    st.markdown('<h3 class="section-header">🧠 AI-Powered Insights</h3>', unsafe_allow_html=True)
    
    if st.button("🤖 Generate Smart Health Recommendations", use_container_width=True):
        summary = f"""
        Average fast food meals per week: {round(avg_fastfood, 2)}
        Average BMI: {round(avg_bmi, 2)}
        Average energy level: {round(avg_energy, 2)}
        Average sleep hours: {round(filtered_df["Sleep_Hours_Per_Day"].mean(), 2)}
        Average physical activity hours: {round(filtered_df["Physical_Activity_Hours_Per_Week"].mean(), 2)}
        Health risk score: {round(avg_risk, 2)}
        """
        
        prompt = f"""
You are a friendly AI health coach analyzing health data.

From the data below, generate exactly 3 personalized, actionable health tips.
Each tip must be:
- One clear sentence
- Specific and actionable
- Motivating and positive
- Start with an emoji

Data:
{summary}

Format as:
1. [emoji] [tip]
2. [emoji] [tip]
3. [emoji] [tip]
"""
        
        with st.spinner("🧠 Analyzing health patterns..."):
            try:
                response = model.generate_content(prompt)
                
                st.markdown(f"""
                    <div class="ai-insight">
                        <h4>💡 Personalized Recommendations</h4>
                        {response.text.replace('\n', '<br>')}
                    </div>
                """, unsafe_allow_html=True)
                
                st.success("✅ AI recommendations generated successfully!")
            except Exception as e:
                st.error(f"❌ Error generating insights: {str(e)}")

def render_insights(filtered_df, filters):
    """Render the health insights page"""
    st.markdown('<h2 class="section-header">🩺 Health Insights</h2>', unsafe_allow_html=True)
    
    render_filter_summary(filters)
    
    if len(filtered_df) == 0:
        st.warning("⚠️ No data available for the selected filters. Try adjusting them.")
        return
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Digestive Issues Distribution
        st.markdown("### 🔬 Digestive Health Analysis")
        pie_data = filtered_df["Digestive_Issues"].value_counts()
        fig_pie = px.pie(
            names=pie_data.index, 
            values=pie_data.values,
            title="Digestive Issues Distribution",
            color_discrete_sequence=["#667eea", "#764ba2"],
            hole=0.4
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        fig_pie.update_layout(
            font=dict(family="Arial", size=12),
            title_font_size=16
        )
        st.plotly_chart(fig_pie, use_container_width=True)
        
        # Stats
        digestive_pct = (filtered_df["Digestive_Issues"] == "Yes").sum() / len(filtered_df) * 100
        st.markdown(f"""
            <div class="info-box">
                <h4 style="margin-top: 0;">📊 Quick Stats</h4>
                <p><b>{digestive_pct:.1f}%</b> of people experience digestive issues</p>
                <p><b>{len(filtered_df)}</b> total records analyzed</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Doctor Visits
        st.markdown("### 🏥 Healthcare Utilization")
        digestive_visits = filtered_df.groupby("Digestive_Issues")["Doctor_Visits_Per_Year"].mean().reset_index()
        fig_bar = px.bar(
            digestive_visits, 
            x="Digestive_Issues", 
            y="Doctor_Visits_Per_Year",
            color="Doctor_Visits_Per_Year",
            color_continuous_scale="Blues",
            title="Average Doctor Visits by Digestive Issues",
            labels={"Doctor_Visits_Per_Year": "Doctor Visits/Year"}
        )
        fig_bar.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family="Arial", size=12),
            title_font_size=16,
            showlegend=False
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        
        # Overall Health Score
        avg_health = filtered_df["Overall_Health_Score"].mean()
        st.markdown(f"""
            <div class="metric-card" style="text-align: center;">
                <h3>🎯 Overall Health Score</h3>
                <div class="metric-value" style="font-size: 3rem;">{avg_health:.1f}/10</div>
            </div>
        """, unsafe_allow_html=True)
    
    # Correlation Analysis
    st.markdown('<h3 class="section-header">🔍 Correlation Analysis</h3>', unsafe_allow_html=True)
    
    # Fast Food vs Digestive Issues
    ff_digestive = filtered_df.groupby(["Fast_Food_Meals_Per_Week", "Digestive_Issues"]).size().reset_index(name='count')
    fig_ff = px.bar(
        ff_digestive,
        x="Fast_Food_Meals_Per_Week",
        y="count",
        color="Digestive_Issues",
        title="Fast Food Consumption vs Digestive Issues",
        barmode='group',
        color_discrete_sequence=["#667eea", "#f5576c"]
    )
    fig_ff.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Arial", size=12),
        title_font_size=16
    )
    st.plotly_chart(fig_ff, use_container_width=True)

def render_personalized_health(df):
    """Render the personalized health predictor page"""
    st.markdown('<h2 class="section-header">🧍 Personalized Health Predictor</h2>', unsafe_allow_html=True)
    st.write("Enter your personal health metrics to get customized insights based on real data.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📋 Basic Information")
        age = st.slider("Your Age", 18, 65, 25, help="Select your age")
        gender = st.selectbox("Gender", ["Male", "Female"], help="Select your gender")
        bmi = st.number_input("Your BMI", 15.0, 40.0, 22.0, step=0.1, help="Body Mass Index")
    
    with col2:
        st.markdown("### 🍔 Lifestyle Habits")
        fast_food = st.slider("Fast Food Meals per Week", 0, 14, 3, help="How many fast food meals do you eat weekly?")
        sleep = st.slider("Sleep Hours per Day", 3.0, 10.0, 7.0, step=0.5, help="Average hours of sleep per night")
        activity = st.slider("Physical Activity Hours per Week", 0.0, 15.0, 3.0, step=0.5, help="Hours of exercise per week")
        energy = st.slider("Energy Level (1–10)", 1, 10, 6, help="Rate your average energy level")
    
    st.markdown("---")
    
    if st.button("🔮 Predict My Health Profile", use_container_width=True, type="primary"):
        with st.spinner("🔍 Analyzing your lifestyle against thousands of data points..."):
            # Find similar profiles
            df_copy = df.copy()
            df_copy["distance"] = (
                abs(df_copy["Age"] - age) * 0.5 +
                abs(df_copy["BMI"] - bmi) * 2 +
                abs(df_copy["Fast_Food_Meals_Per_Week"] - fast_food) * 1.5 +
                abs(df_copy["Sleep_Hours_Per_Day"] - sleep) * 1.5 +
                abs(df_copy["Physical_Activity_Hours_Per_Week"] - activity) * 1 +
                abs(df_copy["Energy_Level_Score"] - energy) * 1
            )
            
            nearest = df_copy.nsmallest(50, "distance")
            
            # Calculate predictions
            avg_health = nearest["Overall_Health_Score"].mean()
            avg_doctor = nearest["Doctor_Visits_Per_Year"].mean()
            digestive_risk = nearest["Digestive_Issues"].value_counts(normalize=True).get("Yes", 0) * 100
            avg_calories = nearest["Average_Daily_Calories"].mean()
            
            # Calculate personal health risk
            personal_data = pd.DataFrame([{
                "BMI": bmi,
                "Fast_Food_Meals_Per_Week": fast_food,
                "Sleep_Hours_Per_Day": sleep,
                "Physical_Activity_Hours_Per_Week": activity,
                "Energy_Level_Score": energy
            }])
            personal_risk = calculate_health_risk(personal_data.iloc[0])
            
            st.markdown("---")
            st.markdown('<h3 class="section-header">🎯 Your Health Prediction</h3>', unsafe_allow_html=True)
            
            # Metrics in columns
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                health_color = "#2ecc71" if avg_health >= 7 else "#f39c12" if avg_health >= 5 else "#e74c3c"
                st.markdown(f"""
                    <div class="metric-card" style="border-left-color: {health_color};">
                        <h3>🩺 Health Score</h3>
                        <div class="metric-value" style="color: {health_color};">{avg_health:.1f}/10</div>
                    </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                    <div class="metric-card">
                        <h3>🏥 Doctor Visits</h3>
                        <div class="metric-value">{avg_doctor:.1f}</div>
                        <p style="color: #666; margin: 0;">per year</p>
                    </div>
                """, unsafe_allow_html=True)
            
            with col3:
                risk_color = "#2ecc71" if digestive_risk < 30 else "#f39c12" if digestive_risk < 60 else "#e74c3c"
                st.markdown(f"""
                    <div class="metric-card" style="border-left-color: {risk_color};">
                        <h3>🔬 Digestive Risk</h3>
                        <div class="metric-value" style="color: {risk_color};">{digestive_risk:.0f}%</div>
                    </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                    <div class="metric-card">
                        <h3>🔥 Est. Calories</h3>
                        <div class="metric-value">{avg_calories:.0f}</div>
                        <p style="color: #666; margin: 0;">per day</p>
                    </div>
                """, unsafe_allow_html=True)
            
            # Risk indicator
            render_health_risk_indicator(personal_risk)
            
            # AI Personalized Analysis
            st.markdown('<h3 class="section-header">🤖 AI Personal Analysis</h3>', unsafe_allow_html=True)
            
            ai_prompt = f"""
You are a health coach. A {age}-year-old {gender.lower()} has:
- BMI: {bmi}
- Fast food meals/week: {fast_food}
- Sleep hours/day: {sleep}
- Physical activity hours/week: {activity}
- Energy level: {energy}/10

Their predicted health metrics based on similar profiles:
- Health score: {avg_health:.1f}/10
- Digestive issues risk: {digestive_risk:.0f}%
- Health risk score: {personal_risk:.1f}/100

Provide:
1. A brief (2-3 sentences) assessment of their lifestyle
2. 3 specific, actionable recommendations to improve their health
3. One positive reinforcement about what they're doing well

Format professionally and encouragingly.
"""
            
            try:
                response = model.generate_content(ai_prompt)
                st.markdown(f"""
                    <div class="ai-insight">
                        <h4>💡 Your Personalized Health Report</h4>
                        {response.text.replace('\n\n', '<br><br>').replace('\n', '<br>')}
                    </div>
                """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"❌ Error generating AI analysis: {str(e)}")
            
            # Comparison chart
            st.markdown("### 📊 How You Compare")
            comparison_data = pd.DataFrame({
                'Metric': ['Health Score', 'BMI', 'Fast Food', 'Sleep', 'Activity', 'Energy'],
                'Your Value': [avg_health, bmi, fast_food, sleep, activity, energy],
                'Average': [
                    df['Overall_Health_Score'].mean(),
                    df['BMI'].mean(),
                    df['Fast_Food_Meals_Per_Week'].mean(),
                    df['Sleep_Hours_Per_Day'].mean(),
                    df['Physical_Activity_Hours_Per_Week'].mean(),
                    df['Energy_Level_Score'].mean()
                ]
            })
            
            fig_compare = go.Figure()
            fig_compare.add_trace(go.Bar(name='You', x=comparison_data['Metric'], y=comparison_data['Your Value'], marker_color='#667eea'))
            fig_compare.add_trace(go.Bar(name='Average', x=comparison_data['Metric'], y=comparison_data['Average'], marker_color='#c7d2fe'))
            fig_compare.update_layout(
                barmode='group',
                title="Your Metrics vs Population Average",
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(family="Arial", size=12),
                title_font_size=16
            )
            st.plotly_chart(fig_compare, use_container_width=True)

def render_data_page(filtered_df, filters):
    """Render the data preview page"""
    st.markdown('<h2 class="section-header">📊 Dataset Preview</h2>', unsafe_allow_html=True)
    
    render_filter_summary(filters)
    
    if len(filtered_df) == 0:
        st.warning("⚠️ No data available for the selected filters. Try adjusting them.")
        return
    
    # Summary statistics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Records", len(filtered_df))
    with col2:
        st.metric("Unique Ages", filtered_df["Age"].nunique())
    with col3:
        st.metric("Gender Distribution", f"{(filtered_df['Gender']=='Male').sum()}M / {(filtered_df['Gender']=='Female').sum()}F")
    
    st.markdown("---")
    
    # Data table
    st.markdown("### 📋 Filtered Data")
    st.dataframe(
        filtered_df.style.background_gradient(cmap='Blues', subset=['BMI', 'Fast_Food_Meals_Per_Week']),
        use_container_width=True,
        height=400
    )
    
    # Download button
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="⬇️ Download Filtered Data (CSV)",
        data=csv,
        file_name="snackalyze_filtered_data.csv",
        mime="text/csv",
        use_container_width=True
    )
    
    # Quick statistics
    st.markdown("### 📈 Quick Statistics")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Numerical Summary**")
        st.dataframe(filtered_df[['Age', 'BMI', 'Fast_Food_Meals_Per_Week', 'Energy_Level_Score']].describe())
    
    with col2:
        st.markdown("**Categorical Summary**")
        cat_summary = pd.DataFrame({
            'Gender': filtered_df['Gender'].value_counts(),
            'Digestive Issues': filtered_df['Digestive_Issues'].value_counts()
        })
        st.dataframe(cat_summary)

# =============================================================================
# SIDEBAR
# =============================================================================
def render_sidebar(df):
    """Render the sidebar with filters"""
    with st.sidebar:
        st.markdown("## 🎛️ Control Panel")
        st.markdown("---")
        
        # Navigation
        st.markdown("### 🧭 Navigation")
        page = st.radio(
            "Select Page",
            ["Dashboard", "Insights", "Personalized Health", "Data"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # Filters
        st.markdown("### 🔍 Data Filters")
        
        gender_filter = st.selectbox("👤 Gender", options=["All"] + list(df["Gender"].unique()))
        
        age_range = st.slider(
            "🎂 Age Range",
            int(df["Age"].min()),
            int(df["Age"].max()),
            (int(df["Age"].min()), int(df["Age"].max()))
        )
        
        bmi_range = st.slider(
            "⚖️ BMI Range",
            float(df["BMI"].min()),
            float(df["BMI"].max()),
            (float(df["BMI"].min()), float(df["BMI"].max())),
            step=0.1
        )
        
        fastfood_range = st.slider(
            "🍔 Fast Food (meals/week)",
            int(df["Fast_Food_Meals_Per_Week"].min()),
            int(df["Fast_Food_Meals_Per_Week"].max()),
            (int(df["Fast_Food_Meals_Per_Week"].min()), int(df["Fast_Food_Meals_Per_Week"].max()))
        )
        
        digestive_filter = st.multiselect(
            "🔬 Digestive Issues",
            options=["Yes", "No"],
            default=["Yes", "No"]
        )
        
        energy_range = st.slider(
            "⚡ Energy Level",
            int(df["Energy_Level_Score"].min()),
            int(df["Energy_Level_Score"].max()),
            (int(df["Energy_Level_Score"].min()), int(df["Energy_Level_Score"].max()))
        )
        
        activity_range = st.slider(
            "🏃 Physical Activity (hrs/week)",
            float(df["Physical_Activity_Hours_Per_Week"].min()),
            float(df["Physical_Activity_Hours_Per_Week"].max()),
            (float(df["Physical_Activity_Hours_Per_Week"].min()), float(df["Physical_Activity_Hours_Per_Week"].max())),
            step=0.5
        )
        
        sleep_range = st.slider(
            "😴 Sleep (hrs/day)",
            float(df["Sleep_Hours_Per_Day"].min()),
            float(df["Sleep_Hours_Per_Day"].max()),
            (float(df["Sleep_Hours_Per_Day"].min()), float(df["Sleep_Hours_Per_Day"].max())),
            step=0.5
        )
        
        st.markdown("---")
        
        # Reset button
        if st.button("🔄 Reset All Filters", use_container_width=True):
            st.rerun()
        
        st.markdown("---")
        st.markdown("### ℹ️ About")
        st.info("**Snackalyze** helps you understand the relationship between fast food consumption and health metrics.")
        
        filters = {
            'gender': gender_filter,
            'age': age_range,
            'bmi': bmi_range,
            'fastfood': fastfood_range,
            'digestive': digestive_filter,
            'energy': energy_range,
            'activity': activity_range,
            'sleep': sleep_range
        }
        
        return page, filters

# =============================================================================
# MAIN APPLICATION
# =============================================================================
def main():
    """Main application entry point"""
    load_custom_css()
    render_navbar()
    
    # Load data
    df = load_data()
    
    # Sidebar
    page, filters = render_sidebar(df)
    
    # Apply filters
    filtered_df = apply_filters(df, filters)
    
    # Render selected page
    if page == "Dashboard":
        render_dashboard(filtered_df, filters)
    elif page == "Insights":
        render_insights(filtered_df, filters)
    elif page == "Personalized Health":
        render_personalized_health(df)
    else:  # Data
        render_data_page(filtered_df, filters)
    
    # Footer
    st.markdown("---")
    st.markdown("""
        <div style="text-align: center; color: #666; padding: 2rem 0;">
            <p>Made with ❤️ using Streamlit | © 2024 Snackalyze</p>
            <p style="font-size: 0.85rem;">Data is for demonstration purposes only</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()