import streamlit as st
import google.generativeai as genai
import os
from datetime import datetime
import pandas as pd
import json
import uuid
import plotly.express as px
from dotenv import load_dotenv
from PIL import Image
import io
import base64

# Load environment variables
load_dotenv()

# Configure Google Generative AI with API key
try:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    genai.configure(api_key=GOOGLE_API_KEY)
except Exception as e:
    st.error(f"Error configuring Gemini API: {e}")

# Initialize session state variables if they don't exist
if 'patient_records' not in st.session_state:
    st.session_state.patient_records = []
if 'generated_materials' not in st.session_state:
    st.session_state.generated_materials = []
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = {}
if 'patient_assessments' not in st.session_state:
    st.session_state.patient_assessments = {}   


def generate_knowledge_assessment(patient_info):
    """Generates a personalized quiz to assess patient knowledge of their condition."""
    try:
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        prompt = f"""
        Create a knowledge assessment quiz for a patient with the following profile:
        - Condition: {patient_info['condition']}
        - Education Level: {patient_info['education_level']}
        - Learning Style: {patient_info['learning_style']}
        
        Generate 5 multiple-choice questions that assess the patient's understanding of:
        1. Basic condition information
        2. Treatment rationale
        3. Medication understanding
        4. Self-management techniques
        5. Warning signs requiring medical attention
        
        For each question, provide:
        - The question text
        - 4 possible answers (with one correct answer)
        - An explanation of why the correct answer is right
        - The knowledge category being tested
        
        Format the response as a valid JSON object with the following structure:
        {{
            "questions": [
                {{
                    "text": "Question text",
                    "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
                    "correct_answer": "Correct option",
                    "explanation": "Explanation of the correct answer",
                    "category": "Category being tested"
                }},
                ...
            ]
        }}
        """
        
        # Generate the response
        response = model.generate_content(prompt)
        
        # Debug: Print the raw response
        st.write("Raw API Response:", response.text)
        
        # Clean the response by removing triple backticks and the "json" keyword
        cleaned_response = response.text.strip().replace("json", "").replace("", "").strip()
        
        # Parse JSON response
        try:
            assessment = json.loads(cleaned_response)
            return assessment
        except json.JSONDecodeError as e:
            st.error(f"Failed to parse assessment: {e}")
            st.error(f"Cleaned response: {cleaned_response}")
            return {"error": "Failed to parse assessment", "raw_response": cleaned_response}
    
    except Exception as e:
        st.error(f"Error generating assessment: {e}")
        return {"error": "Failed to generate assessment"}
    
    
# Add this function to evaluate user responses
def evaluate_responses(assessment, user_responses):
    """Evaluates user responses to the knowledge assessment."""
    results = {
        "total_questions": len(assessment["questions"]),
        "correct_answers": 0,
        "incorrect_answers": 0,
        "feedback": []
    }
    
    for i, question in enumerate(assessment["questions"]):
        user_answer = user_responses.get(f"question_{i}")
        if user_answer == question["correct_answer"]:
            results["correct_answers"] += 1
            feedback = f"✅ Correct! {question['explanation']}"
        else:
            results["incorrect_answers"] += 1
            feedback = f"❌ Incorrect. The correct answer is: {question['correct_answer']}. {question['explanation']}"
        
        results["feedback"].append({
            "question": question["text"],
            "user_answer": user_answer,
            "correct_answer": question["correct_answer"],
            "feedback": feedback
        })
    
    return results

# Function to generate personalized patient education material
def analyze_injury(image, description):
    try:
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        # Convert the image to base64 for processing
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        # Create a prompt with the image and description
        prompt = f"""
        Analyze this injury or skin condition based on the image and description:
        
        Patient Description: {description}
        
        Please provide the following:
        1. Possible identification of the condition (disclaimer that this is not a medical diagnosis)
        2. Common causes for this type of injury/condition
        3. Recommended home remedies or over-the-counter treatments
        4. When to seek professional medical attention
        5. Precautions to follow
        6. Expected healing timeline
        
        Format the response with clear headings and bullet points where appropriate.
        Include a clear disclaimer at the beginning that this is not medical advice and serious conditions require professional medical attention.
        """
        
        # Generate the content with both text and image input
        response = model.generate_content([prompt, {'mime_type': 'image/jpeg', 'data': img_str}])
        
        return response.text
    
    except Exception as e:
        st.error(f"Error analyzing injury: {e}")
        return "Error analyzing the image and description. Please try again or consult a healthcare professional."



# Function to generate personalized patient education material
def generate_patient_education(patient_info):
    try:
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        # Construct prompt with patient information
        prompt = f"""
        Generate personalized patient education material based on the following patient information:
        
        Patient Demographics:
        - Age: {patient_info['age']}
        - Gender: {patient_info['gender']}
        - Education Level: {patient_info['education_level']}
        - Primary Language: {patient_info['language']}
        
        Medical Information:
        - Condition/Diagnosis: {patient_info['condition']}
        - Treatment Plan: {patient_info['treatment']}
        - Medication(s): {patient_info['medications']}
        
        Special Considerations:
        - Learning Style: {patient_info['learning_style']}
        - Special Needs: {patient_info['special_needs']}
        
        Create educational content that:
        1. Explains their condition in simple, understandable terms appropriate for their education level
        2. Describes their treatment plan and why it's important
        3. Explains how to take their medications, potential side effects, and when to contact healthcare providers
        4. Includes lifestyle recommendations specific to their condition
        5. Uses language and examples appropriate for their age, gender, and cultural background
        6. Adapts to their preferred learning style (visual, auditory, reading/writing, kinesthetic)
        7. Accommodates any special needs mentioned
        
        The content should be empathetic, encouraging, and empowering for the patient.
        Format the content with clear headings, bullet points where appropriate, and a summary at the end.
        """
        
        response = model.generate_content(prompt)
        
        # Record the generated material
        material = {
            "id": str(uuid.uuid4()),
            "patient_id": patient_info["id"],
            "patient_name": patient_info["name"],
            "condition": patient_info["condition"],
            "content": response.text,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        st.session_state.generated_materials.append(material)
        save_data()
        
        return response.text
    
    except Exception as e:
        st.error(f"Error generating content: {e}")
        return "Error generating content. Please check your Gemini API key and try again."

# Function to handle patient chat interactions
def chat_with_patient(patient_info, user_question):
    try:
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        # Construct prompt with patient information and question
        prompt = f"""
        You are a medical assistant chatbot helping a patient with their health condition.
        
        Patient Information:
        - Name: {patient_info['name']}
        - Age: {patient_info['age']}
        - Gender: {patient_info['gender']}
        - Education Level: {patient_info['education_level']}
        - Primary Language: {patient_info['language']}
        - Medical Condition: {patient_info['condition']}
        - Treatment Plan: {patient_info['treatment']}
        - Medications: {patient_info['medications']}
        - Learning Style: {patient_info['learning_style']}
        - Special Needs: {patient_info['special_needs']}
        
        The patient is asking: "{user_question}"
        
        Provide a single, clear, and concise answer that is:
        1. Appropriate for their education level and learning style
        2. Specific to their medical condition and treatment plan
        3. Empathetic and reassuring
        4. Accurate but not overly technical
        5. Includes actionable advice when appropriate
        
        If the question is outside of your scope or requires immediate medical attention, advise the patient to contact their healthcare provider.
        """
        
        response = model.generate_content(prompt)
        return response.text
    
    except Exception as e:
        st.error(f"Error generating response: {e}")
        return "I'm sorry, I'm having trouble connecting to my knowledge base. Please try again later or contact your healthcare provider for assistance."

# Functions to save and load data
def save_data():
    data = {
        "patients": st.session_state.patient_records,
        "materials": st.session_state.generated_materials,
        "chat_history": st.session_state.chat_history
    }
    with open("patient_education_data.json", "w") as f:
        json.dump(data, f)

def load_data():
    try:
        with open("patient_education_data.json", "r") as f:
            data = json.load(f)
            st.session_state.patient_records = data.get("patients", [])
            st.session_state.generated_materials = data.get("materials", [])
            st.session_state.chat_history = data.get("chat_history", {})
    except FileNotFoundError:
        st.session_state.patient_records = []
        st.session_state.generated_materials = []
        st.session_state.chat_history = {}

# Load existing data on app start
load_data()

# App UI
st.set_page_config(
    page_title="Personalized Patient Education System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS with background image and improved styling
st.markdown("""
<style>
body{
    /* Base styles and background */
    .main { 
        background: linear-gradient(rgba(255, 255, 255, 0.6), rgba(255, 255, 255, 0.6)), 
                    url('https://www.shutterstock.com/image-vector/medical-background-healthcare-technology-abstract-260nw-1687258565.jpg') center/cover fixed;
        background-repeat: no-repeat;
    }
    
    /* Adding an overlay to improve text readability over the background */
    .main:before {
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(255, 255, 255, 0.4);
        z-index: -1;
    }
    
    .st-emotion-cache-16txtl3 {
        padding: 3rem 1rem;
    }
    
    /* Typography */
    h1, h2, h3 {
        color: #2c3e50;
        font-weight: 600;
    }
    
    /* Enhanced Glassmorphism card styles */
    .glass-card {
        background: rgba(255, 255, 255, 0.25);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.18);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15);
        padding: 20px;
        margin-bottom: 20px;
        transition: all 0.3s ease;
    }
    
    .glass-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px 0 rgba(31, 38, 135, 0.2);
    }
    
    /* Improved Feature cards */
    .feature-card {
        # background: rgba(255, 255, 255, 0.3);
        backdrop-filter: blur(7px);
        -webkit-backdrop-filter: blur(7px);
        border-radius: 15px;
        padding: 18px;
        border-left: 5px solid rgba(52, 152, 219, 0.8);
        margin-bottom: 20px;
        transition: all 0.3s ease;
        height: 100%;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        background: rgba(255, 255, 255, 0.4);
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
    }
    
    .feature-card h3 {
        margin-top: 0;
        font-size: 1.3rem;
    }
    
    .feature-card p {
        margin-bottom: 0;
        line-height: 1.5;
    }
    
    /* Enhanced Hero section */
    .hero-section {
        background: linear-gradient(135deg, rgba(52, 152, 219, 0.8), rgba(155, 89, 182, 0.8));
        background: linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.6)),
        url('https://images.unsplash.com/photo-1576091160550-2173dba999ef?auto=format&fit=crop&q=80') center/cover fixed;
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.18);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.2);
        padding: 50px 40px;
        color: white;
        margin-bottom: 40px;
        text-align: center;
        position: relative;
        overflow: hidden;
        height: 80vh;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    
    .hero-section:before {
        content: "";
        position: absolute;
        top: -20px;
        right: -20px;
        width: 140px;
        height: 140px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 50%;
    }
    
    .hero-section:after {
        content: "";
        position: absolute;
        bottom: -30px;
        left: -30px;
        width: 180px;
        height: 180px;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 50%;
    }
    
    .hero-section h1 {
        font-size: 3rem;
        margin-bottom: 15px;
        color: white;
        text-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
    }
    
    .hero-section p {
        font-size: 1.3rem;
        max-width: 800px;
        margin: 0 auto;
        opacity: 0.9;
    }
    
    /* Enhanced Sidebar navigation */
    .css-1d391kg, .css-hxt7ib {
        background: rgba(245, 247, 250, 0.85) !important;
        backdrop-filter: blur(15px) !important;
        -webkit-backdrop-filter: blur(15px) !important;
        border-right: 1px solid rgba(230, 230, 230, 0.7);
        
    }
    
    .css-1v3fvcr {
        overflow-x: hidden;
    }
    
    /* Custom Navigation Menu */
    .nav-item {
        display: flex;
        align-items: center;
        padding: 10px 15px;
        border-radius: 10px;
        margin-bottom: 8px;
        cursor: pointer;
        transition: all 0.2s ease;
        background: rgba(255, 255, 255, 0.5);
        
    }
    
    .nav-item:hover, .nav-item.active {
        background: rgba(52, 152, 219, 0.2);
    }
    
    .nav-icon {
        margin-right: 10px;
        font-size: 1.2rem;
        color: #3498db;
    }
    
    /* Dashboard stats cards */
    .stats-card {
        background: rgba(255, 255, 255, 0.3);
        background: linear-gradient(rgba(0, 0, 0, 0.8), rgba(0, 0, 0, 0.8)),
                url('https://images.unsplash.com/photo-1505751172876-fa1923c5c528') center/cover fixed;
        backdrop-filter: blur(7px);
        -webkit-backdrop-filter: blur(7px);
        border-radius: 15px;
        padding: 25px;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.18);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.1);
        transition: all 0.3s ease;
        height: 100%;
    }
    
    .stats-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 25px rgba(0, 0, 0, 0.1);
    }
    
    .metric-number {
        font-size: 2.8rem;
        font-weight: bold;
        color: #3498db;
        margin-bottom: 5px;
        text-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    }
    
    .metric-label {
        font-size: 1rem;
        color: #7f8c8d;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Quick Start Guide */
    .guide-card {
        # background: rgba(255, 255, 255, 0.25);
           background: linear-gradient(rgba(0, 0, 0, 0.8), rgba(0, 0, 0, 0.8)),
                url('https://images.unsplash.com/photo-1505751172876-fa1923c5c528') center/cover fixed;
        backdrop-filter: blur(7px);
        -webkit-backdrop-filter: blur(7px);
        border-radius: 15px;
        padding: 25px;
        border: 1px solid rgba(255, 255, 255, 0.18);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.1);
        height: 100%;
    }
    
    .guide-card h3 {
        color: #3498db;
        margin-top: 0;
        font-size: 1.5rem;
        margin-bottom: 15px;
        border-bottom: 2px solid rgba(52, 152, 219, 0.3);
        padding-bottom: 10px;
    }
    
    .guide-card ol, .guide-card ul {
        padding-left: 20px;
    }
    
    .guide-card li {
        margin-bottom: 15px;
        line-height: 1.5;
    }
    
    /* Animation keyframes */
    @keyframes slideInUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    /* Apply animations to elements */
    .hero-section {
        animation: fadeIn 0.8s ease-out forwards;
    }
    
    .feature-card, .stats-card, .guide-card {
        animation: slideInUp 0.6s ease-out forwards;
    }
    
    /* Staggered animations for feature cards */
    .feature-card:nth-child(1) { animation-delay: 0.1s; }
    .feature-card:nth-child(2) { animation-delay: 0.2s; }
    .feature-card:nth-child(3) { animation-delay: 0.3s; }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 20px;
        margin-top: 40px;
        color: #7f8c8d;
        font-size: 0.9rem;
        border-top: 1px solid rgba(0, 0, 0, 0.05);
    }
    
    .chat-message {
        padding: 15px;
        border-radius: 15px;
        margin-bottom: 10px;
        display: flex;
        flex-direction: column;
        max-width: 80%;
    }
    .user-message {
        background-color: #3498db;
        color: white;
        border-bottom-right-radius: 5px;
        align-self: flex-end;
        margin-left: auto;
    }
    .bot-message {
        background-color: #f1f1f1;
        color: #333;
        border-bottom-left-radius: 5px;
        align-self: flex-start;
        margin-right: auto;
    }
    
</style>
""", unsafe_allow_html=True)

# Hidden radio button for navigation (controlled by the custom nav)
page = st.sidebar.radio("Navigation", ["Home", "Add Patient", "Generate Materials", "Patient Chat", "View Materials", "Analytics", "Injury Assessment" , "Knowledge Assessment"], label_visibility="collapsed")

# Custom navbar with icons
def nav_item(title, icon, page_name, current_page):
    active = " active" if page_name == current_page else ""
    return f"""
    <div class="nav-item{active}" onclick="document.querySelector('input[name=\"Navigation\"][value=\"{page_name}\"]').click();">
        <div class="nav-icon">{icon}</div>
        <div>{title}</div>
    </div>
    """

# # Create the navigation HTML
nav_item = f"""
{nav_item("Home", "🏠", "Home", page)}
{nav_item("Add Patient", "👤", "Add Patient", page)}
{nav_item("Generate Materials", "📚", "Generate Materials", page)}
{nav_item("Patient Chat", "💬", "Patient Chat", page)}
{nav_item("View Materials", "📋", "View Materials", page)}
{nav_item("Analytics", "📊", "Analytics", page)}
{nav_item("Injury Assessment", "🤕", "Injury Assessment", page)}
{nav_item("Knowledge Assessment", "🤔", "Knowledge Assessment", page)}
"""

# Display the custom navigation
st.sidebar.markdown(nav_item, unsafe_allow_html=True)

# Sidebar footer (fixed at the bottom)
st.sidebar.markdown("""

""", unsafe_allow_html=True)

# Home page with enhanced design

if page == "Home":
    # Enhanced Hero section
    st.markdown("""
    <div class="hero-section">
        <h1>🏥 Personalized Patient Education System</h1>
        <p>Empowering patients with AI-tailored educational materials and personalized healthcare support</p>
    </div>
    """, unsafe_allow_html=True)
    
    
    
    # System Overview with improved stat cards
    st.markdown("### System Overview")
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        st.markdown(f"""
        <div class="stats-card">
            <div class="metric-number">{len(st.session_state.patient_records)}</div>
            <div class="metric-label">Patient Profiles</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_b:
        st.markdown(f"""
        <div class="stats-card">
            <div class="metric-number">{len(st.session_state.generated_materials)}</div>
            <div class="metric-label">Educational Materials</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_c:
        # Calculate unique conditions
        if st.session_state.patient_records:
            unique_conditions = len(set(p['condition'] for p in st.session_state.patient_records))
        else:
            unique_conditions = 0
            
        st.markdown(f"""
        <div class="stats-card">
            <div class="metric-number">{unique_conditions}</div>
            <div class="metric-label">Unique Conditions</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Enhanced Feature Cards in 3 columns
    st.markdown("### Key Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3 style="color: #3498db;">📋 Smart Patient Profiles</h3>
            <p>Create comprehensive patient profiles with detailed medical information and learning preferences.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <h3 style="color: #3498db;">📊 Analytics Dashboard</h3>
            <p>Track content generation and analyze patient education materials effectiveness over time.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3 style="color: #3498db;">🤖 AI-Generated Content</h3>
            <p>Generate personalized educational materials tailored to each patient's unique needs and preferences.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <h3 style="color: #3498db;">💬 Patient Chatbot</h3>
            <p>Answer patient questions with AI that understands their specific medical context and history.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h3 style="color: #3498db;">📚 Material Library</h3>
            <p>Access and manage all generated educational materials with easy filtering and organization.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <h3 style="color: #3498db;">🔄 Seamless Workflow</h3>
            <p>Streamlined process from patient intake to education delivery with intuitive interface.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Quick Start Guide and Benefits
    st.markdown("### Getting Started")
    col_d, col_e = st.columns(2)
    
    with col_d:
        st.markdown("""
        <div class="guide-card">
            <h3>Quick Start Guide</h3>
            <ol>
                <li><b>Add a Patient Profile</b> - Create a detailed patient record with medical information and learning preferences</li>
                <li><b>Generate Educational Material</b> - Create personalized content tailored to the patient's specific needs</li>
                <li><b>Use the Patient Chatbot</b> - Enable patients to ask questions and receive personalized answers</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
    
    with col_e:
        st.markdown("""
        <div class="guide-card">
            <h3>Why Personalization Matters</h3>
            <p>Studies show that personalized patient education can improve:</p>
            <ul>
                <li><b>70% Increase</b> in treatment adherence</li>
                <li><b>85% Higher</b> patient satisfaction scores</li>
                <li><b>Reduced</b> hospitalizations and complications</li>
                <li><b>Improved</b> patient engagement and self-management</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <div class="footer">
        <p>Personalized Patient Education System • Powered by Gemini AI</p>
    </div>
    """, unsafe_allow_html=True)




# Add Patient page
elif page == "Add Patient":
    st.title("Add New Patient")
    
    with st.form("patient_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name")
            age = st.number_input("Age", min_value=0, max_value=120, value=30)
            gender = st.selectbox("Gender", ["Male", "Female", "Non-binary", "Prefer not to say"])
            education_level = st.selectbox("Education Level", ["Elementary", "High School", "College", "Graduate", "Post-Graduate"])
            language = st.selectbox("Primary Language", ["English", "Spanish", "French", "Mandarin", "Arabic", "Other"])
        
        with col2:
            condition = st.text_input("Medical Condition/Diagnosis")
            treatment = st.text_area("Treatment Plan")
            medications = st.text_area("Medications")
            learning_style = st.selectbox("Preferred Learning Style", ["Visual", "Auditory", "Reading/Writing", "Kinesthetic", "Mixed"])
            special_needs = st.text_area("Special Needs or Considerations", help="Enter any special needs like visual impairment, hearing loss, etc.")
        
        submit_button = st.form_submit_button("Save Patient Information")
        
        if submit_button:
            if name and condition:
                # Create patient record
                patient_id = str(uuid.uuid4())
                patient = {
                    "id": patient_id,
                    "name": name,
                    "age": age,
                    "gender": gender,
                    "education_level": education_level,
                    "language": language,
                    "condition": condition,
                    "treatment": treatment,
                    "medications": medications,
                    "learning_style": learning_style,
                    "special_needs": special_needs,
                    "date_added": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                st.session_state.patient_records.append(patient)
                # Initialize chat history for this patient
                st.session_state.chat_history[patient_id] = []
                save_data()
                
                st.success(f"Patient {name} added successfully!")
                st.balloons()
            else:
                st.error("Name and Medical Condition are required fields.")

# Generate Materials page
elif page == "Generate Materials":
    st.title("Generate Patient Education Materials")
    
    if not st.session_state.patient_records:
        st.warning("No patients found. Please add patients first.")
    else:
        # Patient selection
        patient_names = [f"{p['name']} - {p['condition']}" for p in st.session_state.patient_records]
        selected_patient = st.selectbox("Select Patient", patient_names)
        
        # Get the selected patient's index
        patient_index = patient_names.index(selected_patient)
        patient = st.session_state.patient_records[patient_index]
        
        # Display patient information
        with st.expander("Patient Information", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"Name: {patient['name']}")
                st.markdown(f"Age: {patient['age']}")
                st.markdown(f"Gender: {patient['gender']}")
                st.markdown(f"Education Level: {patient['education_level']}")
                st.markdown(f"Primary Language: {patient['language']}")
            
            with col2:
                st.markdown(f"Medical Condition: {patient['condition']}")
                st.markdown(f"Treatment Plan: {patient['treatment']}")
                st.markdown(f"Medications: {patient['medications']}")
                st.markdown(f"Learning Style: {patient['learning_style']}")
                st.markdown(f"Special Needs: {patient['special_needs']}")
        
        # Generate content
        if st.button("Generate Personalized Education Material"):
            with st.spinner("Generating personalized content..."):
                content = generate_patient_education(patient)
                
                st.success("Material generated successfully!")
                
                # Display the generated content
                st.markdown("### Generated Education Material")
                st.markdown(content)
                
                # Download option
                st.download_button(
                    label="Download as Text File",
                    data=content,
                    file_name=f"{patient['name']}_{patient['condition']}_education.txt",
                    mime="text/plain"
                )

# New Patient Chat page
elif page == "Patient Chat":
    st.title("💬 Patient Chatbot")
    
    if not st.session_state.patient_records:
        st.warning("No patients found. Please add patients first.")
    else:
        # Patient selection
        patient_names = [f"{p['name']} - {p['condition']}" for p in st.session_state.patient_records]
        selected_patient = st.selectbox("Select Patient", patient_names)
        
        # Get the selected patient's index and information
        patient_index = patient_names.index(selected_patient)
        patient = st.session_state.patient_records[patient_index]
        patient_id = patient['id']
        
        # Display patient information
        with st.expander("Patient Information", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"Name: {patient['name']}")
                st.markdown(f"Age: {patient['age']}")
                st.markdown(f"Gender: {patient['gender']}")
                st.markdown(f"Education Level: {patient['education_level']}")
                st.markdown(f"Primary Language: {patient['language']}")
            
            with col2:
                st.markdown(f"Medical Condition: {patient['condition']}")
                st.markdown(f"Treatment Plan: {patient['treatment']}")
                st.markdown(f"Medications: {patient['medications']}")
                st.markdown(f"Learning Style: {patient['learning_style']}")
                st.markdown(f"Special Needs: {patient['special_needs']}")
        
        # Initialize chat history for this patient if it doesn't exist
        if patient_id not in st.session_state.chat_history:
            st.session_state.chat_history[patient_id] = []
        
        # Chat container
        st.markdown(f"### Chat with {patient['name']}'s Personal Health Assistant")
        st.markdown("Ask questions about your condition, treatment, medications, or health concerns.")
        
        # Display chat history
        chat_container = st.container()
        with chat_container:
            st.markdown('<div class="message-container">', unsafe_allow_html=True)
            
            # Display welcome message if chat is empty
            if not st.session_state.chat_history[patient_id]:
                st.markdown(
                    f'<div class="chat-message bot-message">'
                    f'<p>Hello {patient["name"]}! I\'m your personal health assistant. '
                    f'I know about your {patient["condition"]} and can answer questions about your treatment plan '
                    f'or medications. How can I help you today?</p>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            
            # Display chat history
            for message in st.session_state.chat_history[patient_id]:
                if message["role"] == "user":
                    st.markdown(
                        f'<div class="chat-message user-message">'
                        f'<p>{message["content"]}</p>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f'<div class="chat-message bot-message">'
                        f'<p>{message["content"]}</p>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Chat input
        user_question = st.text_input("Type your health question here:", key="user_question")
        
        if st.button("Send") and user_question:
            # Add user message to chat history
            st.session_state.chat_history[patient_id].append({
                "role": "user",
                "content": user_question,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            
            # Generate response
            with st.spinner("Thinking..."):
                bot_response = chat_with_patient(patient, user_question)
            
            # Add bot response to chat history
            st.session_state.chat_history[patient_id].append({
                "role": "assistant",
                "content": bot_response,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            
            # Save chat history
            save_data()
            
            # Rerun to display the new messages
            st.rerun()
        
        # Option to clear chat history
        if st.button("Clear Chat History"):
            st.session_state.chat_history[patient_id] = []
            save_data()
            st.success("Chat history cleared!")
            st.rerun()

# View Materials page
elif page == "View Materials":
    st.title("View Generated Materials")
    
    if not st.session_state.generated_materials:
        st.warning("No educational materials have been generated yet.")
    else:
        # Filter options
        col1, col2 = st.columns(2)
        with col1:
            filter_patient = st.selectbox(
                "Filter by Patient", 
                ["All"] + list(set(material["patient_name"] for material in st.session_state.generated_materials))
            )
        with col2:
            filter_condition = st.selectbox(
                "Filter by Condition", 
                ["All"] + list(set(material["condition"] for material in st.session_state.generated_materials))
            )
        
        # Apply filters
        filtered_materials = st.session_state.generated_materials
        if filter_patient != "All":
            filtered_materials = [m for m in filtered_materials if m["patient_name"] == filter_patient]
        if filter_condition != "All":
            filtered_materials = [m for m in filtered_materials if m["condition"] == filter_condition]
        
        # Display materials
        if not filtered_materials:
            st.info("No materials match the selected filters.")
        else:
            for material in filtered_materials:
                with st.expander(f"{material['patient_name']} - {material['condition']} ({material['timestamp']})"):
                    st.markdown(material["content"])
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.download_button(
                            label="Download as Text",
                            data=material["content"],
                            file_name=f"{material['patient_name']}_{material['condition']}_education.txt",
                            mime="text/plain",
                            key=f"download_{material['id']}"
                        )
                    with col2:
                        if st.button("Delete", key=f"delete_{material['id']}"):
                            st.session_state.generated_materials.remove(material)
                            save_data()
                            st.success("Material deleted")
                            st.rerun()

# Analytics page

elif page == "Injury Assessment":
    st.title("🩹 Injury Assessment")
    
    st.markdown("""
    <div class="info-box">
        <h3>Upload an image of your injury or skin condition</h3>
        <p>Our AI will analyze the image and your description to provide insights and recommendations.</p>
        <p><strong>Disclaimer:</strong> This tool is for informational purposes only and does not replace professional medical advice.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 3])
    
    with col1:
        uploaded_file = st.file_uploader("Upload image of injury/condition", type=["jpg", "jpeg", "png"])
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_column_width=True)
    
    with col2:
        description = st.text_area("Describe your injury or condition", 
                                   height=150, 
                                   placeholder="Please describe your injury or condition. Include details like:\n- When it occurred\n- Any pain or discomfort\n- Changes you've noticed\n- Any treatments you've tried")
        
        patient_name = st.text_input("Your name (optional)")
        patient_age = st.number_input("Your age (optional)", min_value=0, max_value=120, value=30)
        
        analyze_button = st.button("Analyze Injury")
    
    if uploaded_file is not None and description and analyze_button:
        with st.spinner("Analyzing your injury..."):
            analysis_result = analyze_injury(image, description)
            
            # Create a record of the assessment
            assessment = {
                "id": str(uuid.uuid4()),
                "patient_name": patient_name if patient_name else "Anonymous",
                "patient_age": patient_age,
                "description": description,
                "image_filename": uploaded_file.name,
                "assessment": analysis_result,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Add to a new list for injury assessments if it doesn't exist
            if 'injury_assessments' not in st.session_state:
                st.session_state.injury_assessments = []
            
            st.session_state.injury_assessments.append(assessment)
            
            # Update save_data and load_data functions to include injury assessments
            
            st.success("Analysis complete!")
            
            st.markdown("### Assessment Results")
            st.markdown(analysis_result)
            
            # Download option
            st.download_button(
                label="Download Assessment",
                data=analysis_result,
                file_name=f"injury_assessment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
            
elif page == "Analytics":
    st.title("Analytics Dashboard")
    
    if not st.session_state.generated_materials:
        st.warning("No data available for analytics. Generate some materials first.")
    else:
        # Create dataframes for analysis
        materials_df = pd.DataFrame(st.session_state.generated_materials)
        materials_df['date'] = pd.to_datetime(materials_df['timestamp']).dt.date
        
        # Layout
        col1, col2 = st.columns(2)
        
        # Materials by condition
        with col1:
            condition_counts = materials_df['condition'].value_counts().reset_index()
            condition_counts.columns = ['Condition', 'Count']
            
            fig = px.pie(condition_counts, values='Count', names='Condition', title='Materials by Medical Condition')
            st.plotly_chart(fig, use_container_width=True)
        
        # Materials over time
        with col2:
            time_series = materials_df.groupby('date').size().reset_index(name='count')
            fig = px.line(time_series, x='date', y='count', title='Materials Generated Over Time')
            st.plotly_chart(fig, use_container_width=True)
        
        # Materials by patient
        patient_counts = materials_df['patient_name'].value_counts().reset_index()
        patient_counts.columns = ['Patient', 'Count']
        
        fig = px.bar(patient_counts, x='Patient', y='Count', title='Materials by Patient')
        st.plotly_chart(fig, use_container_width=True)
        
        # Chat interactions analysis
        if any(st.session_state.chat_history):
            st.subheader("Chat Interactions Analysis")
            
            # Calculate chat metrics
            total_chats = 0
            total_messages = 0
            patients_with_chats = 0
            
            chat_data = []
            
            for patient_id, messages in st.session_state.chat_history.items():
                if messages:
                    patients_with_chats += 1
                    total_chats += 1
                    total_messages += len(messages)
                    
                    # Find patient name
                    patient_name = next((p['name'] for p in st.session_state.patient_records if p['id'] == patient_id), "Unknown")
                    
                    chat_data.append({
                        "Patient": patient_name,
                        "Messages": len(messages),
                        "Last Interaction": messages[-1]["timestamp"] if messages else "N/A"
                    })
        


        if 'injury_assessments' in st.session_state and st.session_state.injury_assessments:
            st.subheader("Injury Assessment Analysis")
    
            # Create dataframe for injury assessments
            injury_df = pd.DataFrame(st.session_state.injury_assessments)
            injury_df['date'] = pd.to_datetime(injury_df['timestamp']).dt.date
    
            # Display injury assessment metrics
            st.metric("Total Injury Assessments", len(injury_df))
    
            # Display assessments over time
            time_series = injury_df.groupby('date').size().reset_index(name='count')
            fig = px.line(time_series, x='date', y='count', title='Injury Assessments Over Time')
            st.plotly_chart(fig, use_container_width=True)
    
            # Display assessments table
            with st.expander("View All Injury Assessments"):
                st.dataframe(injury_df[['patient_name', 'patient_age', 'description', 'timestamp']])


            # Display chat metrics
            col3, col4, col5 = st.columns(3)
            with col3:
                st.metric("Total Chat Sessions", total_chats)
            with col4:
                st.metric("Total Messages", total_messages)
            with col5:
                st.metric("Patients Using Chat", patients_with_chats)
            
            # Display chat data table
            if chat_data:
                chat_df = pd.DataFrame(chat_data)
                st.dataframe(chat_df)
        
        # Display raw data
        with st.expander("View Raw Data"):
            st.dataframe(materials_df)

elif page == "Knowledge Assessment":
    st.title("📝 Knowledge Assessment")
    
    if not st.session_state.patient_records:
        st.warning("No patients found. Please add patients first.")
    else:
        # Patient selection
        patient_names = [f"{p['name']} - {p['condition']}" for p in st.session_state.patient_records]
        selected_patient = st.selectbox("Select Patient", patient_names)
        
        # Get the selected patient's index
        patient_index = patient_names.index(selected_patient)
        patient = st.session_state.patient_records[patient_index]
        patient_id = patient["id"]
        
        # Display patient information
        with st.expander("Patient Information", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"Name: {patient['name']}")
                st.markdown(f"Age: {patient['age']}")
                st.markdown(f"Gender: {patient['gender']}")
                st.markdown(f"Education Level: {patient['education_level']}")
                st.markdown(f"Primary Language: {patient['language']}")
            
            with col2:
                st.markdown(f"Medical Condition: {patient['condition']}")
                st.markdown(f"Treatment Plan: {patient['treatment']}")
                st.markdown(f"Medications: {patient['medications']}")
                st.markdown(f"Learning Style: {patient['learning_style']}")
                st.markdown(f"Special Needs: {patient['special_needs']}")
        
        # Generate knowledge assessment
        if st.button("Generate Knowledge Assessment"):
            with st.spinner("Generating personalized assessment..."):
                assessment = generate_knowledge_assessment(patient)
                
                if "error" in assessment:
                    st.error("Failed to generate assessment. Please try again.")
                else:
                    st.session_state.patient_assessments[patient_id] = {
                        "assessment": assessment,
                        "user_responses": {},
                        "results": None
                    }
                    save_data()
                    st.success("Assessment generated successfully!")
        
        # Display the assessment if it exists
        if patient_id in st.session_state.patient_assessments:
            assessment_data = st.session_state.patient_assessments[patient_id]
            assessment = assessment_data["assessment"]
            user_responses = assessment_data["user_responses"]
            results = assessment_data["results"]
            
            st.markdown("### Knowledge Assessment")
            
            # Display questions and collect user responses
            for i, question in enumerate(assessment["questions"]):
                st.markdown(f"*Question {i+1}:* {question['text']}")
                options = question["options"]
                user_responses[f"question_{i}"] = st.radio(
                    f"Select your answer for question {i+1}:",
                    options,
                    key=f"question_{i}"
                )
            
            # Evaluate responses
            if st.button("Submit Assessment"):
                results = evaluate_responses(assessment, user_responses)
                st.session_state.patient_assessments[patient_id]["results"] = results
                save_data()
                st.success("Assessment submitted!")
            
            # Display results if available
            if results:
                st.markdown("### Assessment Results")
                st.markdown(f"*Total Questions:* {results['total_questions']}")
                st.markdown(f"*Correct Answers:* {results['correct_answers']}")
                st.markdown(f"*Incorrect Answers:* {results['incorrect_answers']}")
                
                st.markdown("### Feedback")
                for feedback in results["feedback"]:
                    st.markdown(f"*Question:* {feedback['question']}")
                    st.markdown(f"*Your Answer:* {feedback['user_answer']}")
                    st.markdown(f"*Correct Answer:* {feedback['correct_answer']}")
                    st.markdown(f"*Feedback:* {feedback['feedback']}")
                    st.markdown("---")