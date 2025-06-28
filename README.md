# 🏥 Personalized Patient Education System

A comprehensive AI-powered healthcare application that generates personalized educational materials and provides interactive support for patients using Google's Gemini AI.

## ✨ Features

### 🔧 Core Functionality
- **Smart Patient Profiles** - Create detailed patient records with medical information and learning preferences
- **AI-Generated Content** - Generate personalized educational materials tailored to each patient's unique needs
- **Patient Chatbot** - Interactive AI assistant that understands patient's medical context
- **Material Library** - Organize and manage all generated educational materials
- **Analytics Dashboard** - Track content generation and analyze effectiveness
- **Injury Assessment** - AI-powered image analysis for injury evaluation
- **Knowledge Assessment** - Personalized quizzes to test patient understanding

### 🎨 User Experience
- Modern glassmorphism UI design
- Responsive layout with enhanced visual elements
- Interactive navigation with custom styling
- Real-time chat interface
- Comprehensive analytics and reporting

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- Google AI API key (Gemini)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd personalized-patient-education
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   GOOGLE_API_KEY=your_gemini_api_key_here
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

## 📦 Dependencies

```txt
streamlit
google-generativeai
pandas
plotly
python-dotenv
Pillow
uuid
json
datetime
io
base64
os
```

## 🔧 Configuration

### Environment Variables
- `GOOGLE_API_KEY` - Your Google Gemini AI API key (required)

### Getting a Gemini API Key
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add it to your `.env` file

## 📖 Usage Guide

### 1. Adding Patients
- Navigate to "Add Patient" section
- Fill in comprehensive patient information including:
  - Demographics (name, age, gender)
  - Education level and primary language
  - Medical condition and treatment plan
  - Learning preferences and special needs

### 2. Generating Educational Materials
- Select a patient from the dropdown
- Review patient information
- Click "Generate Personalized Education Material"
- Download or save the generated content

### 3. Patient Chat Interface
- Select a patient to chat with
- Ask questions about their condition, treatment, or medications
- Receive personalized responses based on their medical profile
- Chat history is automatically saved

### 4. Injury Assessment
- Upload an image of an injury or skin condition
- Provide a detailed description
- Receive AI-powered analysis and recommendations
- Download assessment results

### 5. Knowledge Assessment
- Generate personalized quizzes for patients
- Test understanding of their medical condition
- Receive detailed feedback on responses
- Track learning progress

### 6. Analytics Dashboard
- View system usage statistics
- Analyze materials by condition and patient
- Track chat interactions
- Monitor injury assessments over time

## 🏗️ Architecture

### File Structure
```
├── app.py                          # Main Streamlit application
├── .env                           # Environment variables
├── requirements.txt               # Python dependencies
├── patient_education_data.json    # Data storage (auto-generated)
└── README.md                      # This file
```

### Data Storage
The application uses JSON file storage for:
- Patient records
- Generated materials
- Chat history
- Assessment results
- Injury evaluations

### AI Integration
- **Google Gemini 1.5 Pro** for content generation
- **Image analysis** for injury assessment
- **Conversational AI** for patient chat
- **Educational content** personalization

## 🎯 Key Functions

### Content Generation
```python
generate_patient_education(patient_info)
```
Generates personalized educational materials based on patient profile.

### Chat Functionality
```python
chat_with_patient(patient_info, user_question)
```
Provides contextual responses to patient questions.

### Injury Analysis
```python
analyze_injury(image, description)
```
Analyzes injury images and provides recommendations.

### Knowledge Assessment
```python
generate_knowledge_assessment(patient_info)
evaluate_responses(assessment, user_responses)
```
Creates and evaluates personalized knowledge tests.

## 🔒 Privacy & Security

### Data Handling
- All patient data is stored locally
- No data is shared with third parties
- Images are processed temporarily and not stored permanently
- Chat history can be cleared by users

### Disclaimers
- This system is for educational purposes only
- Not a substitute for professional medical advice
- Users should consult healthcare providers for medical decisions
- Injury assessments are informational only

## 📊 Analytics Features

- **Patient Statistics** - Track number of patients and conditions
- **Content Generation** - Monitor material creation over time
- **Chat Metrics** - Analyze patient engagement
- **Assessment Results** - Track learning outcomes
- **Visual Reports** - Interactive charts and graphs

## 🎨 UI/UX Features

- **Glassmorphism Design** - Modern translucent interface elements
- **Responsive Layout** - Works on desktop and mobile devices
- **Interactive Navigation** - Custom styled navigation menu
- **Real-time Updates** - Instant feedback and updates
- **Download Options** - Export materials and assessments

## 🚨 Troubleshooting

### Common Issues

1. **API Key Error**
   - Ensure your Gemini API key is correctly set in `.env`
   - Verify the API key has proper permissions

2. **Image Upload Issues**
   - Supported formats: JPG, JPEG, PNG
   - Check image file size (should be reasonable)

3. **Data Not Saving**
   - Ensure write permissions in the application directory
   - Check if `patient_education_data.json` is being created

4. **Performance Issues**
   - Large chat histories may slow down the app
   - Consider clearing old chat data periodically

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Google Gemini AI** for providing powerful AI capabilities
- **Streamlit** for the excellent web framework
- **Plotly** for interactive visualizations
- Healthcare professionals who inspire better patient education

## 📞 Support

For support, please:
1. Check the troubleshooting section
2. Review the usage guide
3. Open an issue on GitHub
4. Contact the development team

---

**⚠️ Important Notice**: This application is designed for educational and research purposes. Always consult with qualified healthcare professionals for medical advice and treatment decisions.
