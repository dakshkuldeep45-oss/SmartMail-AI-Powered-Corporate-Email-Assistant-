import streamlit as st
from google import genai
import config
import sys

# Configure basic web layout parameters
st.set_page_config(page_title=config.APP_TITLE, layout="centered")

def process_email_workflow(raw_email_text, response_tone):
    """Dispatches corporate text inputs to the Gemini inference engine for parsing."""
    try:
        client = genai.Client(api_key=config.GEMINI_API_KEY)
        
        analysis_prompt = f"""
        You are an elite corporate communications executive. Analyze the incoming email text and execute two specific processing tasks.
        
        INCOMING EMAIL TEXT:
        {raw_email_text}
        
        DESIRED REPLY TONE:
        {response_tone}
        
        Format your execution response matching these strict headings precisely:
        [PRIORITY]
        Insert only one word here representing urgency level: Urgent, Medium, or Low.
        [CATEGORY]
        Insert only a single categorizing label here matching the domain: Tech Support, Billing, Customer Feedback, or Spam.
        [REPLY]
        Write a complete, ready-to-send corporate email reply addressing all points from the incoming mail in a "{response_tone}" tone. Include appropriate placeholder markers like [Your Name].
        """
        
        response = client.models.generate_content(
            model=config.MODEL_ENGINE,
            contents=analysis_prompt
        )
        return response.text
    except Exception as e:
        return f"Operational Error linking to AI cloud processors: {str(e)}"

# Define Streamlit Web User Interface View Elements
st.title("📧 SmartMail Autopilot")
st.subheader("AI-Powered Corporate Email Assistant & Ticket Classifier")

st.divider()

email_input = st.text_area("Paste incoming email text contents here:", height=180, 
                           placeholder="Dear Support team, I have been trying to access my dashboard since morning but it shows 502 error...")

tone_choice = st.selectbox(
    "Select desired auto-reply messaging style:",
    ["Professional & Courteous", "Apologetic & Explanatory", "Urgent & Escalated", "Casual & Informative"]
)

st.divider()

if st.button("Execute Autopilot Workflow", type="primary"):
    if not config.GEMINI_API_KEY or config.GEMINI_API_KEY == "YOUR_SECURE_API_KEY_HERE":
        st.error("Configuration Error: Active Gemini API Key binding missing inside config.py.")
    elif not email_input.strip():
        st.warning("Please insert email text content to process.")
    else:
        with st.spinner("Classifying ticket domains and generating reply matrix..."):
            raw_result = process_email_workflow(email_input, tone_choice)
            
            try:
                parts = raw_result.split("[")
                priority_val = "Medium"
                category_val = "General"
                reply_text = ""
                
                for part in parts:
                    if part.startswith("PRIORITY]"):
                        priority_val = part.replace("PRIORITY]", "").strip()
                    elif part.startswith("CATEGORY]"):
                        category_val = part.replace("CATEGORY]", "").strip()
                    elif part.startswith("REPLY]"):
                        reply_text = part.replace("REPLY]", "").strip()
                
                st.success("Workflow Analysis Complete!")
                
                # Visual Dashboard Metrics
                col1, col2 = st.columns(2)
                with col1:
                    st.metric(label="Assigned Ticket Category", value=category_val)
                with col2:
                    st.metric(label="Operational Priority Urgency", value=priority_val)
                
                st.divider()
                st.write("### 📝 Drafted Auto-Response")
                st.markdown(reply_text)
                
                # Download utility component
                st.download_button(
                    label="📥 Export Draft Response",
                    data=reply_text,
                    file_name="Email_Draft.txt",
                    mime="text/plain"
                )
                
            except Exception:
                st.markdown(raw_result)
