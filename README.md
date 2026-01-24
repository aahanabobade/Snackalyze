# Snackalyze - Health Analytics Dashboard

An AI-powered interactive health analytics platform that helps users understand the relationship between fast food consumption and health metrics through data visualization and personalized insights.

## Overview

Snackalyze is a comprehensive health analytics application built with Streamlit that analyzes lifestyle habits, particularly focusing on fast food consumption and its correlation with various health indicators. The platform provides real-time data visualization, AI-powered recommendations, and personalized health predictions based on user input.

## Features

### Core Functionality

- **Interactive Dashboard**: Real-time visualization of health metrics including BMI, energy levels, sleep patterns, and physical activity
- **Health Risk Assessment**: Calculate personalized health risk scores (0-100) based on multiple lifestyle factors
- **AI-Powered Insights**: Generate customized health recommendations using Google's Gemini AI
- **Personalized Health Predictor**: Input your own metrics to receive tailored health predictions based on similar profiles
- **Advanced Data Filtering**: Filter and analyze data by age, gender, BMI, fast food consumption, digestive issues, and more
- **Data Export**: Download filtered datasets for further analysis

### Key Visualizations

- BMI vs Fast Food Consumption trends
- Daily Calorie Intake correlations
- Energy Level vs Sleep Hours scatter plots
- Digestive Health distribution analysis
- Healthcare utilization patterns
- Comparative analysis charts

## Technology Stack

### Backend
- **Python 3.8+**: Core programming language
- **Streamlit**: Web application framework
- **Pandas**: Data manipulation and analysis
- **Google Generative AI (Gemini)**: AI-powered health recommendations

### Frontend
- **Plotly Express**: Interactive data visualizations
- **Plotly Graph Objects**: Custom chart components
- **Custom CSS**: Modern, responsive UI design

### AI Integration
- **Google Gemini 2.5 Flash**: Natural language generation for personalized health insights

## Project Structure

```
snackalyze/
│
├── app.py                      # Main application file
├── data.csv                    # Health metrics dataset
├── .env                        # Environment variables (API keys)
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation
```

## Prerequisites

Before running the application, ensure you have:

- Python 3.8 or higher
- pip package manager
- Google AI API key (for Gemini integration)

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/snackalyze.git
cd snackalyze
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Set Up Environment Variables

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_google_api_key_here
```

To get a Google AI API key:
1. Visit https://makersuite.google.com/app/apikey
2. Create a new API key
3. Copy and paste it into your `.env` file

### Step 5: Prepare Data

Ensure you have a `data.csv` file with the following columns:
- Age
- Gender
- BMI
- Fast_Food_Meals_Per_Week
- Average_Daily_Calories
- Sleep_Hours_Per_Day
- Physical_Activity_Hours_Per_Week
- Energy_Level_Score
- Digestive_Issues
- Doctor_Visits_Per_Year
- Overall_Health_Score

## Usage

### Running the Application

```bash
streamlit run app.py
```

The application will automatically open in your default web browser at `http://localhost:8501`

### Navigating the Application

#### 1. Dashboard
- View overall health metrics and trends
- Analyze BMI, fast food consumption, energy levels, and sleep patterns
- Get AI-powered health recommendations
- Monitor health risk scores

#### 2. Insights
- Explore digestive health statistics
- Analyze healthcare utilization patterns
- View correlation between fast food and health issues
- Examine overall health score distributions

#### 3. Personalized Health
- Input your personal health metrics
- Receive customized health predictions
- Get AI-generated personalized recommendations
- Compare your metrics against population averages

#### 4. Data
- Preview filtered dataset
- View summary statistics
- Download data for external analysis

### Using Filters

Access the sidebar to filter data by:
- **Gender**: Male, Female, or All
- **Age Range**: Adjust slider to select age group
- **BMI Range**: Filter by body mass index
- **Fast Food Consumption**: Meals per week
- **Digestive Issues**: Yes, No, or both
- **Energy Level**: 1-10 scale
- **Physical Activity**: Hours per week
- **Sleep Duration**: Hours per day

## Health Risk Calculation

The application calculates a comprehensive health risk score (0-100) based on:

### Contributing Factors

- **BMI (up to 25 points)**
  - BMI > 30: +25 points
  - BMI 25-30: +15 points
  - BMI 22-25: +8 points

- **Fast Food Consumption (up to 20 points)**
  - >10 meals/week: +20 points
  - 6-10 meals/week: +12 points
  - 3-6 meals/week: +6 points

- **Sleep Duration (up to 15 points)**
  - <5 hours: +15 points
  - 5-6 hours: +10 points
  - 6-7 hours: +5 points

- **Physical Activity (up to 10 points)**
  - <1 hour/week: +10 points
  - 1-3 hours/week: +6 points
  - 3-5 hours/week: +3 points

- **Energy Level (up to 10 points)**
  - <3/10: +10 points
  - 3-5/10: +6 points
  - 5-7/10: +3 points

### Risk Categories

- **Low Risk (0-39)**: Healthy lifestyle, minimal health concerns
- **Moderate Risk (40-69)**: Some lifestyle improvements recommended
- **High Risk (70-100)**: Significant health concerns, lifestyle changes needed

## AI Features

### Smart Health Recommendations

The application uses Google's Gemini AI to generate:
- Personalized health tips based on your metrics
- Actionable lifestyle improvement suggestions
- Positive reinforcement for healthy habits
- Data-driven insights from population trends

### Personalized Health Analysis

AI analyzes your profile to provide:
- Lifestyle assessment (2-3 sentences)
- 3 specific, actionable recommendations
- Positive reinforcement
- Comparison with similar health profiles

## Data Privacy

- All data processing happens locally or through secure API calls
- No personal health data is stored permanently
- Google AI API calls are encrypted and secure
- Downloaded data is for your personal use only

## Customization

### Modifying Visualizations

Edit the chart configurations in `app.py`:

```python
fig = px.line(
    data, 
    x="column_x", 
    y="column_y",
    title="Your Custom Title"
)
fig.update_layout(
    plot_bgcolor='white',
    font=dict(family="Arial", size=12)
)
```

### Adjusting Health Risk Formula

Modify the `calculate_health_risk()` function to change risk scoring:

```python
def calculate_health_risk(row):
    score = 0
    # Add your custom logic here
    return min(score, 100)
```

### Customizing AI Prompts

Edit the prompt templates for different AI responses:

```python
prompt = f"""
Your custom prompt here with {variables}
"""
```

## Troubleshooting

### Common Issues

**Issue**: Application won't start
```bash
# Solution: Check Python version
python --version  # Should be 3.8+

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**Issue**: AI recommendations not generating
```bash
# Solution: Verify API key in .env file
# Ensure .env file exists and contains valid GOOGLE_API_KEY
```

**Issue**: Data not loading
```bash
# Solution: Verify data.csv exists and has correct format
# Check column names match expected format
```

**Issue**: Charts not displaying
```bash
# Solution: Clear Streamlit cache
streamlit cache clear
```

## Dependencies

```
streamlit>=1.28.0
pandas>=2.0.0
plotly>=5.17.0
python-dotenv>=1.0.0
google-generativeai>=0.3.0
```

## Future Enhancements

- Integration with wearable device data (Fitbit, Apple Watch)
- Meal tracking and nutrition database
- Social features for community challenges
- Advanced ML models for predictive analytics
- Multi-language support
- Mobile app version
- Integration with healthcare provider systems

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with Streamlit for rapid web app development
- Powered by Google Gemini AI for intelligent health insights
- Data visualization using Plotly
- Inspired by the need for accessible health analytics tools

## Disclaimer

This application is for educational and informational purposes only. It is not intended to be a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of your physician or other qualified health provider with any questions you may have regarding a medical condition.

---

**Made with ❤️ for better health awareness**
