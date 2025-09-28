import streamlit as st
from PIL import Image
from streamlit_lottie import st_lottie
import requests
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta

# --- Credential Storage (for demonstration) ---
VALID_CREDENTIALS = {
    "guest": "guest",
    "kmetro_admin": "admin123",
    "station_controller": "stationpass",
    "ops_officer": "opspass",
    "maint_eng": "maintpass",
    "admin_staff": "staffpass"
}

# --- Initialize session state ---
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
    st.session_state['username'] = None
    st.session_state['role'] = None
if 'language' not in st.session_state:
    st.session_state['language'] = 'English'

# --- Language Translations ---
LANGUAGES = {
    "English": {
        "title": "Welcome to AkshRail",
        "subtitle": "Intelligent Document Management for Kochi Metro Rail",
        "critical_alert": "CRITICAL ALERT: Unexpected maintenance on Line 2 scheduled for tonight. Delays expected.",
        "welcome_message": "AkshRail is an **AI-powered solution** designed to revolutionize document management for Kochi Metro Rail Limited. Say goodbye to manual filing and hello to automated summaries, intelligent search, and actionable insights.",
        "mission": "Our mission: To transform document overload into a streamlined, efficient information hub.",
        "role_summary_title": "Your Role-Based Summary",
        "manager_summary": "High-level overview of monthly document submissions and pending approvals. Analytics tab shows key performance indicators for department efficiency.",
        "engineer_summary": "Recent maintenance reports and technical drawings have been uploaded. Check the 'Search' page for 'Safety Protocol Update DOC-1150'.",
        "guest_summary": "You are logged in as a Guest. You have read-only access to public documents. Please contact an administrator for elevated privileges.",
        "core_capabilities": "🚀 Core Capabilities",
        "ocr_title": "OCR & Text Extraction",
        "ocr_desc": "Extracts text from scanned PDFs, images, and various document formats with high accuracy.",
        "nlp_title": "NLP for Insights",
        "nlp_desc": "Summarizes content, identifies key entities, and detects duplicates using advanced Natural Language Processing.",
        "search_title": "Smart Search & Linkage",
        "search_desc": "Provides blazing-fast search capabilities and automatically links related documents for comprehensive understanding."
    },
    "Malayalam": {
        "title": "അക്ഷറെയിലിലേക്ക് സ്വാഗതം",
        "subtitle": "കൊച്ചി മെട്രോ റെയിലിനായുള്ള ഇന്റലിജന്റ് ഡോക്യുമെന്റ് മാനേജ്മെന്റ്",
        "critical_alert": "ഗുരുതരമായ മുന്നറിയിപ്പ്: ലൈൻ 2-ൽ ഇന്ന് രാത്രി അപ്രതീക്ഷിത അറ്റകുറ്റപ്പണി. தாமதங்கள் எதிர்பார்க்கப்படுகிறது.",
        "welcome_message": "കൊച്ചി മെട്രോ റെയിൽ ലിമിറ്റഡിന്റെ ഡോക്യുമെന്റ് മാനേജ്‌മെന്റിൽ വിപ്ലവം സൃഷ്ടിക്കാൻ രൂപകൽപ്പന ചെയ്ത ഒരു **AI- പവർഡ് സൊല്യൂഷനാണ്** അക്ഷറെയിൽ. മാനുവൽ ഫയലിംഗിനോട് വിട പറയുകയും ഓട്ടോമേറ്റഡ് സംഗ്രഹങ്ങൾ, ഇന്റലിജന്റ് സെർച്ച്, പ്രവർത്തനക്ഷമമായ സ്ഥിതിവിവരക്കണക്കുകൾ എന്നിവയ്ക്ക് ഹലോ പറയുകയും ചെയ്യുക.",
        "mission": "ഞങ്ങളുടെ ദൗത്യം: ഡോക്യുമെന്റ് ഓവർലോഡ് ഒരു സുസംഘടിതവും കാര്യക്ഷമവുമായ വിവര കേന്ദ്രമാക്കി മാറ്റുക.",
        "role_summary_title": "നിങ്ങളുടെ റോൾ അടിസ്ഥാനമാക്കിയുള്ള സംഗ്രഹം",
        "manager_summary": "പ്രതിമാസ പ്രമാണ സമർപ്പണങ്ങളുടെയും തീർച്ചപ്പെടുത്താത്ത അംഗീകാരങ്ങളുടെയും ഉയർന്ന തലത്തിലുള്ള അവലോകനം. അനലിറ്റിക്‌സ് ടാബ് വകുപ്പിന്റെ കാര്യക്ഷമതയുടെ പ്രധാന സൂചകങ്ങൾ കാണിക്കുന്നു.",
        "engineer_summary": "സമീപകാല മെയിന്റനൻസ് റിപ്പോർട്ടുകളും സാങ്കേതിക ഡ്രോയിംഗുകളും അപ്‌ലോഡ് ചെയ്തു. 'സേഫ്റ്റി പ്രോട്ടോക്കോൾ അപ്‌ഡേറ്റ് DOC-1150' എന്നതിനായി 'തിരയൽ' പേജ് പരിശോധിക്കുക.",
        "guest_summary": "നിങ്ങൾ ഒരു അതിഥിയായി ലോഗിൻ ചെയ്തിരിക്കുന്നു. നിങ്ങൾക്ക് പൊതു പ്രമാണങ്ങളിലേക്ക് റീഡ്-ഒൺലി ആക്‌സസ് ഉണ്ട്. ഉയർന്ന പദവികൾക്കായി ദയവായി ഒരു അഡ്മിനിസ്ട്രേറ്ററുമായി ബന്ധപ്പെടുക.",
        "core_capabilities": "🚀 പ്രധാന കഴിവുകൾ",
        "ocr_title": "OCR & ടെക്സ്റ്റ് എക്സ്ട്രാക്ഷൻ",
        "ocr_desc": "സ്കാൻ ചെയ്ത PDF-കൾ, ചിത്രങ്ങൾ, വിവിധ പ്രമാണ ഫോർമാറ്റുകൾ എന്നിവയിൽ നിന്ന് ഉയർന്ന കൃത്യതയോടെ ടെസ്റ്റ് എക്‌സ്‌ട്രാക്റ്റുചെയ്യുന്നു.",
        "nlp_title": "ഇൻസൈറ്റുകൾക്കായി എൻ‌എൽ‌പി",
        "nlp_desc": "വിപുലമായ നാച്ചുറൽ ലാംഗ്വേജ് പ്രോസസ്സിംഗ് ഉപയോഗിച്ച് ഉള്ളടക്കം സംഗ്രഹിക്കുകയും പ്രധാന എന്റിറ്റികളെ തിരിച്ചറിയുകയും തനിപ്പകർപ്പുകൾ കണ്ടെത്തുകയും ചെയ്യുന്നു.",
        "search_title": "സ്മാർട്ട് സെർച്ച് & ലിങ്കേജ്",
        "search_desc": "അതിവേഗത്തിലുള്ള തിരയൽ കഴിവുകൾ നൽകുകയും സമഗ്രമായ ധാരണയ്ക്കായി ബന്ധപ്പെട്ട പ്രമാണങ്ങളെ യാന്ത്രികമായി ലിങ്കുചെയ്യുകയും ചെയ്യുന്നു."
    }
}

# ---------- Function to load Lottie animation ----------
def load_lottie_url(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# ---------- Login Page Function ----------
def login_page():
    """Renders the login page with professional styling."""
    st.set_page_config(page_title="AkshRail Login", layout="centered")

    # --- STYLE FOR LOGIN PAGE ---
    st.markdown("""
    <style>
    body {
        background-color: #F0F2F6;
    }
    .stApp {
        background-color: #F0F2F6;
    }
    .st-form {
        background-color: white;
        padding: 2em;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    h1, h2 {
        color: #1E2A38;
    }
    .stButton>button {
        background-color: #007BFF;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 10px 20px;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #0056b3;
    }
    </style>
    """, unsafe_allow_html=True)

    st.title("AkshRail Authentication")
    st.subheader("For Authorized Railways and Metro Government Officials")
    st.markdown("---")

    with st.form("login_form"):
        role = st.selectbox(
            "Select Your Post/Role",
            ["Senior Manager", "Station Controller", "Operations Officer", "Maintenance Engineer", "Administrative Staff", "Guest"],
            index=5
        )
        username = st.text_input("Username", placeholder="e.g., kmetro_admin")
        password = st.text_input("Password", type="password", placeholder="••••••••")
        login_button = st.form_submit_button("Login")

        if login_button:
            if username in VALID_CREDENTIALS and password == VALID_CREDENTIALS[username]:
                st.session_state['authenticated'] = True
                st.session_state['username'] = username
                st.session_state['role'] = role
                st.success("Login successful! Redirecting...")
                st.rerun()
            else:
                st.error("Invalid username or password.")
    
    st.info("For demonstration, use Username: `guest` and Password: `guest`")

    st.markdown("---")
    st.caption("Prepared by Team TechNavs. This is a detailed idea demonstration where features and technologies are frequently explained. The final prototype may vary.")

    with st.expander("✨ What You'll Find Inside"):
        st.success("""
        - **A Fully Interactive UI:** Navigate through different menus to see all features in action.
        - **Detailed Explanations:** Every page includes a 'Functions and Technologies' dropdown explaining how it works.
        - **In-depth FAQs:** Each section has a dedicated FAQ to answer common questions about its features.
        - **Advanced Analytics:** Explore the analytics dashboard to see how data-driven insights are generated.
        """)

    with st.expander("🛠️ Functions and Technologies on Login Page"):
        st.write("""
        - **`st.set_page_config`**: Sets the layout to 'centered' for a focused login experience.
        - **`st.markdown` with `<style>` tags**: Injects custom CSS to create a professional look and feel for the login form, including background colors, shadows, and button styling.
        - **`st.form`**: Groups the input fields and login button, ensuring the page only re-runs upon final submission, not on every widget interaction.
        - **`st.session_state`**: The core of the authentication mechanism. It's used to store and verify the user's login status (`authenticated`), username, and selected role across page reruns and navigation.
        - **Credential Validation**: A simple Python dictionary (`VALID_CREDENTIALS`) is used for demonstration to check usernames and passwords. In a production environment, this would be replaced with a secure backend call to a user database.
        """)

# ---------- Main Application Function ----------
def main_app():
    # ---------- Load Logo ----------
    try:
        logo = Image.open("Screenshot (4).png")
    except FileNotFoundError:
        st.warning("Logo file not found. Using a placeholder or removing logo for now.")
        logo = None # Set to None if file not found

    # Page Config
    st.set_page_config(page_title="AkshRail", layout="wide", initial_sidebar_state="expanded")

    # Custom CSS for better aesthetics
    st.markdown("""
    <style>
        .reportview-container .main .block-container {
            padding-top: 2rem;
            padding-right: 2rem;
            padding-left: 2rem;
            padding-bottom: 2rem;
        }
        .css-1d391kg { /* sidebar */
            background-color: #f0f2f6;
        }
        .css-1oe5zmf { /* main app background */
            background-color: #ffffff;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #333366; /* Dark blue for headers */
        }
        .stButton>button {
            background-color: #4CAF50; /* Green button */
            color: white;
            border-radius: 5px;
            border: none;
            padding: 10px 20px;
            font-size: 16px;
        }
        .stButton>button:hover {
            background-color: #45a049;
        }
        .stAlert {
            border-left: 6px solid #2196F3; /* Blue alert border */
            background-color: #66bde8;
        }
        .stExpander {
            border: 1px solid #ddd;
            border-radius: 5px;
            margin-bottom: 10px;
        }
        /* Metric styling */
        div[data-testid="stMetricValue"] {
            font-size: 36px;
            color: #007bff; /* Blue for metric values */
        }
        div[data-testid="stMetricLabel"] {
            font-size: 18px;
            color: #555;
        }
        div[data-testid="stSidebar"] {
            background-image: linear-gradient(to bottom, #333366, #5C5C8A); /* Gradient sidebar */
            color: white;
        }
        div[data-testid="stSidebar"] .stRadio > label {
            color: white;
        }
        div[data-testid="stSidebar"] .stTitle {
            color: white;
        }
    </style>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 5])
    with col1:
        if logo:
            st.image(logo, width=180)
        else:
            st.markdown("<h1 style='color: #333366;'>🚆</h1>", unsafe_allow_html=True) # Placeholder icon
    with col2:
        st.title(" AkshRail")
        st.subheader("Where Information Meets Action")
        st.markdown("---") # Visual separator

    # ---------- Sidebar ----------
    st.sidebar.title("📂 Document Navigation")
    st.sidebar.markdown("---")
    st.sidebar.success(f"Welcome, {st.session_state.get('username', 'User')}!")
    st.sidebar.info(f"Role: {st.session_state.get('role', 'Guest')}")
    menu = st.sidebar.radio("Go to:", ["Home", "Dashboard", "Upload", "Search", "Analytics", "About"])
    st.sidebar.markdown("---")
    
    # --- Logout Button ---
    if st.sidebar.button("Logout"):
        st.session_state['authenticated'] = False
        st.session_state['username'] = None
        st.session_state['role'] = None
        st.rerun()
    
    st.sidebar.info("Developed for Kochi Metro Rail Limited")

    # ---------- Lottie Animations (Centralized) ----------
    home_lottie = load_lottie_url("https://assets1.lottiefiles.com/packages/lf20_9wjm14ni.json") # Welcome
    summary_lottie = load_lottie_url("https://assets7.lottiefiles.com/packages/lf20_u4yrau.json")  # AI Animation
    alert_lottie = load_lottie_url("https://assets9.lottiefiles.com/packages/lf20_tutvdkg0.json")  # Alert/Notification
    upload_lottie = load_lottie_url("https://assets2.lottiefiles.com/packages/lf20_jbr3byh0.json") # Upload
    search_lottie = load_lottie_url("https://assets9.lottiefiles.com/packages/lf20_49rdyysj.json") # Search
    analytics_lottie = load_lottie_url("https://assets1.lottiefiles.com/packages/lf20_mhlvj87g.json") # Analytics
    about_lottie = load_lottie_url("https://assets4.lottiefiles.com/packages/lf20_tpgx4e3e.json") # About/Info


    # ---------- HOME PAGE ----------
    if menu == "Home":
        # --- Language Toggle ---
        lang_choice = st.radio("Language/ഭാഷ", ["English", "Malayalam"], horizontal=True, index=0 if st.session_state['language'] == 'English' else 1)
        if lang_choice != st.session_state.get('language'):
            st.session_state['language'] = lang_choice
            st.rerun()
        
        TEXT = LANGUAGES[st.session_state['language']]

        st.header(TEXT["title"])
        st.markdown(f"### {TEXT['subtitle']}")

        col_lottie, col_text = st.columns([1, 2])
        with col_lottie:
            if home_lottie:
                st_lottie(home_lottie, height=250, key="home_welcome")
        with col_text:
            st.write(TEXT["welcome_message"])
            st.info(TEXT["mission"])

        st.markdown("---")
        st.subheader(TEXT["core_capabilities"])
        col_cap1, col_cap2, col_cap3 = st.columns(3)
        with col_cap1:
            st.markdown(f"#### {TEXT['ocr_title']}")
            st.markdown(TEXT["ocr_desc"])
        with col_cap2:
            st.markdown(f"#### {TEXT['nlp_title']}")
            st.markdown(TEXT["nlp_desc"])
        with col_cap3:
            st.markdown(f"#### {TEXT['search_title']}")
            st.markdown(TEXT["search_desc"])
            
        with st.expander("🛠️ Methodology (Stepwise)"):
            st.write("""
            1. **Document Upload:** Staff uploads documents (PDF/TXT/Scans) via a secure web interface.
            2. **Text Extraction (OCR):** Scanned documents undergo OCR to extract text content, which is then cleaned and pre-processed.
            3. **Processing & Summarization (NLP):** Extracted text is fed into NLP pipelines for summarization, keyword extraction, and identifying potential duplicates.
            4. **Smart Storage & Search (ElasticSearch & DB):** Documents and their metadata (summaries, keywords, entities) are indexed in ElasticSearch and stored in the database for efficient retrieval and linking.
            5. **Alerts & Dashboards:** Role-based dashboards provide staff with an overview, and a notification system delivers critical updates and alerts.
            """)

    
        with st.expander("🌟 How it Differs from Current Metro System"):
            st.write("""
             - Current system relies heavily on **manual reading and filing**, leading to inefficiencies.
            - AkshRail automatically **summarizes, searches, and intelligently links documents**, saving countless hours.
             - Provides **role-specific dashboards** for tailored information access.
             - Offers robust **multi-language support** (English & Malayalam) for broader usability.
             - Implements smart **alerts & notifications** for critical updates and deadlines.
                """)

        with st.expander("✅ Key Benefits"):
            st.write("""
                - **Saves significant time**: Quick access to summaries and search results.
                - **Improves teamwork & collaboration**: Centralized, easily searchable access for all authorized staff.
                - **Ensures compliance**: Highlights critical updates and policy changes.
                - **Reduces duplicated effort**: Automatic duplicate detection and summaries prevent redundant work.
                - **Preserves institutional knowledge**: Creates a living archive of company documents and insights.
                - **Enhances decision-making**: Provides data-driven insights from document analytics.
                """)

        with st.expander("🛠️ Functions and Technologies on Home Page"):
            st.write("""
            - **`st.radio`**: Used to create the horizontal language selection toggle (English/Malayalam), providing an intuitive way for users to switch languages.
            - **`st.session_state`**: Persists the user's language preference (`language`) across the application, ensuring a consistent user experience.
            - **Python Dictionary (`LANGUAGES`)**: Acts as a simple but effective translation store, holding all UI strings for both English and Malayalam.
            - **`streamlit_lottie`**: Renders engaging Lottie animations to improve the visual appeal of the page.
            """)

    # ---------- DASHBOARD ----------
    elif menu == "Dashboard":
        st.subheader("📊 AkshRail Dashboard")
        st.info("Your main control center: Get an overview of document activity, pending tasks, and system health.")
        
        # --- Critical Alerts Banner ---
        st.error("🚨 CRITICAL ALERT: Unexpected maintenance on Line 2 scheduled for tonight. Delays expected.")
        st.markdown("---")

        # --- Role-based Summaries ---
        st.subheader("Your Role-Based Summary")
        role = st.session_state.get('role', 'Guest')
        if role == "Senior Manager":
            st.warning("High-level overview of monthly document submissions and pending approvals. Analytics tab shows key performance indicators for department efficiency.")
        elif role == "Maintenance Engineer":
            st.warning("Recent maintenance reports and technical drawings have been uploaded. Check the 'Search' page for 'Safety Protocol Update DOC-1150'.")
        else: # Guest and other roles
            st.warning("You are logged in as a Guest. You have read-only access to public documents. Please contact an administrator for elevated privileges.")
        st.markdown("---")

        # --- Compliance Deadline Countdowns ---
        st.subheader("Upcoming Compliance Deadlines")
        today = datetime.now()
        deadlines = {
            "Safety Audit Report": today + timedelta(days=15),
            "Quarterly Financial Statement": today + timedelta(days=45),
            "Vendor Contract Renewal (ABC Corp)": today + timedelta(days=7),
        }
        
        for task, deadline in deadlines.items():
            days_left = (deadline - today).days
            if days_left < 10:
                st.error(f"**{task}:** Due in {days_left} days ({deadline.strftime('%Y-%m-%d')})")
            elif days_left < 30:
                st.warning(f"**{task}:** Due in {days_left} days ({deadline.strftime('%Y-%m-%d')})")
            else:
                st.info(f"**{task}:** Due in {days_left} days ({deadline.strftime('%Y-%m-%d')})")
        
        st.markdown("---")

        # --- Duplicate File Alerts ---
        st.subheader("Duplicate File Alerts")
        st.warning("""
        **Potential Duplicates Found:**
        - `DOC-1023` (Maintenance Schedule Q3) appears similar to `DOC-0891`
        - `DOC-2087` (Vendor Invoice #4567) may be a duplicate of `DOC-2080`
        Please review these files in the **Search** section.
        """)
        st.markdown("---")

        col_metrics, col_lottie_dash = st.columns([2, 1])
        with col_metrics:
            # Improved Metrics with custom colors
            st.markdown(
                """
                <style>
                .metric-box {
                    background-color: #f8f9fa;
                    border-radius: 10px;
                    padding: 15px;
                    margin-bottom: 15px;
                    box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
                }
                .metric-label {
                    font-size: 16px;
                    color: #555;
                }
                .metric-value {
                    font-size: 32px;
                    font-weight: bold;
                    color: #007bff; /* Primary blue */
                }
                </style>
                """, unsafe_allow_html=True
            )

            st.markdown('<div class="metric-box"><div class="metric-label">Total Documents Indexed</div><div class="metric-value">1,245</div></div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-box"><div class="metric-label">Documents Awaiting Review</div><div class="metric-value">37</div></div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-box"><div class="metric-label">New Uploads This Month</div><div class="metric-value">223</div></div>', unsafe_allow_html=True)

        with col_lottie_dash:
            if alert_lottie:
                st_lottie(alert_lottie, height=200, key="dashboard_alert_lottie")
            st.markdown("---")
            st.markdown("#### Quick Actions")
            if st.button("Review Pending Documents"):
                st.session_state.menu = "Search" # Example of changing menu based on action
                st.rerun()
            if st.button("Upload New Document"):
                st.session_state.menu = "Upload"
                st.rerun()


        st.markdown("---")
        st.subheader("Recent Document Activity")
        # Sample Data for a table/chart
        activity_data = {
            "Document ID": ["DOC-1023", "DOC-2087", "DOC-1150", "DOC-0998", "DOC-3011"],
            "Title": ["Maintenance Schedule Q3", "Vendor Invoice #4567", "Safety Protocol Update", "Board Meeting Minutes", "New Project Proposal"],
            "Type": ["Report", "Invoice", "Policy", "Minutes", "Proposal"],
            "Last Modified": ["2023-10-26", "2023-10-25", "2023-10-24", "2023-10-23", "2023-10-22"],
            "Status": ["Approved", "Pending Payment", "Under Review", "Finalized", "Draft"]
        }
        df_activity = pd.DataFrame(activity_data)
        st.dataframe(df_activity)

        st.markdown("---")
        
        # --- Department Activity Heatmap ---
        st.subheader("Department Activity Heatmap (Last 7 Days)")
        # Sample Data
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        departments = ["Operations", "Maintenance", "Finance", "HR", "Legal"]
        heatmap_data = np.random.randint(0, 50, size=(len(departments), len(days)))
        df_heatmap = pd.DataFrame(heatmap_data, index=departments, columns=days)
        
        fig_heatmap = px.imshow(df_heatmap,
                                labels=dict(x="Day of Week", y="Department", color="Uploads"),
                                x=days,
                                y=departments,
                                title="Document Uploads by Department",
                                color_continuous_scale=px.colors.sequential.Viridis)
        st.plotly_chart(fig_heatmap, use_container_width=True)
        
        st.markdown("---")
        
        # --- FAQ Section ---
        st.subheader("Frequently Asked Questions (FAQ)")
        with st.expander("What is the 'Your Role-Based Summary' section?"):
            st.write("""
            This section provides a personalized summary of recent activities and important documents relevant to your specific role. This ensures you see the most critical information first, tailored to your responsibilities.
            """)
        with st.expander("Why do I see a critical alert at the top of my dashboard?"):
            st.write("""
            The critical alert banner is used to communicate urgent, high-priority information that affects all users, such as unexpected maintenance, system-wide updates, or safety announcements.
            """)
        with st.expander("How are the compliance deadlines calculated?"):
            st.write("""
            The deadlines are automatically pulled from the document metadata stored in our database. The system calculates the days remaining based on the current date and color-codes them for urgency (Red for <10 days, Yellow for <30 days, Blue for others).
            """)
        with st.expander("What does a 'Duplicate File Alert' mean?"):
            st.write("""
            Our AI-powered NLP system analyzes the content of newly uploaded documents and compares them to existing ones using techniques like document embeddings or hashing. If a high degree of similarity is found, it flags them as potential duplicates to prevent redundant data. You should review these files to confirm if they are true duplicates.
            """)
        with st.expander("How should I interpret the Department Activity Heatmap?"):
            st.write("""
            The heatmap shows the volume of document uploads per department over the last seven days. Darker colors indicate higher activity, while lighter colors indicate lower activity. This helps managers identify departmental workload, track productivity, and spot trends in document submission patterns.
            """)
        with st.expander("Can I customize the dashboard view?"):
            st.write("""
            Currently, the dashboard provides a standardized overview for all users based on their role. We are actively working on developing customizable widgets and personalized views for a future release to allow you to tailor the dashboard to your specific needs.
            """)


        with st.expander("🛠️ Functions and Technologies on Dashboard"):
            st.write("""
            - **`st.error`**: Displays the high-visibility critical alerts banner to immediately draw user attention.
            - **Conditional Rendering (`if/elif/else`)**: Checks `st.session_state['role']` to dynamically display personalized, role-based summaries.
            - **`st.expander`**: Used to create the collapsible FAQ section, allowing for a clean and organized layout where users can find answers without cluttering the main dashboard.
            - **`datetime` & `timedelta`**: Python's standard libraries are used to calculate and display the compliance deadline countdowns, with color-coding (`st.error`, `st.warning`, `st.info`) to indicate urgency.
            - **Duplicate Alerts**: The duplicate file alert section is powered by a backend NLP process (e.g., using document embeddings or hashing) that identifies potential duplicates. The results are then displayed in a formatted `st.warning` message.
            - **Heatmap (`plotly.express.imshow`)**: Creates a detailed and interactive heatmap to visualize department activity. This chart uses aggregated data (simulated with `numpy` and `pandas`) that would be fetched from the document database in a real system.
            - **Metrics & KPIs:** Displays key performance indicators from the database (PostgreSQL/MongoDB) like total documents, pending reviews, calculated by aggregation queries.
            - **Lottie Animations:** Uses `streamlit_lottie` to display dynamic alerts and notifications.
            - **Data Table (`st.dataframe`):** Fetches recent document activity from ElasticSearch/Database and displays it in an interactive table.
            - **Interactive Buttons:** Allows direct navigation to other sections (e.g., "Upload") to streamline workflows.
            """)

    # ---------- UPLOAD ----------
    elif menu == "Upload":
        st.subheader("📤 Upload New Documents to AkshRail")
        st.info("Effortlessly upload engineering drawings, invoices, reports, and various other document types. Our system will automatically process them.")

        col_upload_form, col_upload_lottie = st.columns([2, 1])
        with col_upload_form:
            with st.form("document_upload_form"):
                uploaded_file = st.file_uploader("Choose a document to upload", type=["pdf", "docx", "jpg", "png", "txt", "xlsx"], help="Supported formats: PDF, DOCX, JPG, PNG, TXT, XLSX")
                document_title = st.text_input("Document Title (Optional)", placeholder="e.g., Q4 Financial Report, Metro Line 3 Design")
                
                confidentiality = st.radio(
                    "Select Confidentiality Level",
                    ("Public", "Internal", "Sensitive"),
                    index=1,
                    horizontal=True
                )

                submit_button = st.form_submit_button("Upload Document & Process")

                if submit_button:
                    if uploaded_file is not None:
                        st.success(f"✅ Document '{uploaded_file.name}' uploaded successfully!")
                        st.write("Processing document...")
                        
                        predicted_type = "Invoice" 
                        with st.spinner("Extracting text, classifying document, and generating summary..."):
                            import time
                            time.sleep(3)
                        st.success("Document processed and indexed!")
                        
                        st.markdown(f"**Title:** {document_title if document_title else uploaded_file.name}")
                        st.info(f"**Auto-detected Document Type:** {predicted_type}")
                        st.warning(f"**Confidentiality Level Set To:** {confidentiality}")

                        st.markdown("---")
                        st.subheader("OCR Preview (Extracted Text)")
                        st.text_area(
                            "Review the extracted text from the document below. Edits can be made if necessary.",
                            "Kochi Metro Rail Limited\nInvoice #KMRL-2025-4567\nDate: 2025-09-27\n\nBill To:\nOperations Department\nKochi Metro Rail Ltd.\n\nDescription\tQuantity\tUnit Price\tTotal\n------------------------------------------------------------\nPart #XYZ-001\t5\t₹15,000\t₹75,000\nService Fee\t1\t₹5,000\t₹5,000\n------------------------------------------------------------\nTotal Due: ₹80,000\n\nNotes: 30-day payment terms.",
                            height=250
                        )

                    else:
                        st.error("Please select a file to upload.")

        with col_upload_lottie:
            if upload_lottie:
                st_lottie(upload_lottie, height=300, key="upload_animation")
            st.markdown("---")
            st.markdown("#### How it Works:")
            st.write("""
            1. **Upload:** Your file is securely transmitted.
            2. **OCR & Classification:** Text is extracted, and the document type is auto-detected.
            3. **NLP Analysis:** Content is summarized, and keywords are identified.
            4. **Indexing:** The document and its metadata are stored for rapid retrieval.
            """)
        
        st.markdown("---")

        # --- FAQ Section for Upload ---
        st.subheader("Frequently Asked Questions (FAQ)")
        with st.expander("How does the OCR Preview work?"):
            st.write("""
            When you upload an image or a scanned PDF, our system uses Optical Character Recognition (OCR) technology to extract the text from the document. The text you see in the preview box is the direct result of this process. It's provided so you can verify its accuracy and make corrections before the document is saved.
            """)
        with st.expander("Is the auto-classification of documents always accurate?"):
            st.write("""
            Our AI model is trained to classify documents based on their content with high accuracy. However, for complex or unusual documents, it might misclassify. We recommend reviewing the auto-detected type. In future versions, you will be able to override the suggestion if needed.
            """)
        with st.expander("What do the different confidentiality levels mean?"):
            st.write("""
            - **Public:** The document can be viewed by anyone, including guest users.
            - **Internal:** The document is accessible only to logged-in staff members of Kochi Metro.
            - **Sensitive:** Access is restricted to specific high-level roles or departments. This ensures that confidential information is protected.
            """)
        with st.expander("Can I upload multiple files at once?"):
            st.write("""
            This version of the application supports single file uploads to ensure each document is processed with its specific metadata. A bulk upload feature is on our development roadmap and will be available in a future update.
            """)


        with st.expander("🛠️ Functions and Technologies on Upload Page"):
            st.write("""
            - **OCR Preview (`st.text_area`):** After backend OCR processing (e.g., using Tesseract), the extracted text is displayed in a text area for user review and correction, ensuring data accuracy.
            - **Auto-classification (Backend NLP):** The system uses a pre-trained NLP classification model (e.g., from **Hugging Face** or a custom **scikit-learn** model) to analyze the document's content and automatically suggest a type (e.g., 'Invoice', 'Report').
            - **Confidentiality Labels (`st.radio`):** Allows users to apply important security metadata to the document at the time of upload, which can be used later for access control.
            - **File Uploader (`st.file_uploader`):** Handles secure file uploads from the user interface.
            - **Forms (`st.form`):** Organizes user input fields and streamlines submission.
            - **Backend Integration (Simulated):** The `submit_button` triggers an API call to a **Flask/Django** backend, which orchestrates the OCR, NLP classification, and summarization tasks.
            - **Database & ElasticSearch (Backend):** The processed data, including the confidentiality label and auto-detected type, is stored in **PostgreSQL/MongoDB** and indexed in **ElasticSearch**.
            - **Streamlit Spinners (`st.spinner`):** Provides visual feedback during backend processing.
            """)


    # ---------- SEARCH ----------
    elif menu == "Search":
        st.subheader("🔍 Smart Search & Retrieve Documents")
        st.info("Find any document instantly with advanced search capabilities. Use keywords, document IDs, or even natural language queries.")

        col_search_input, col_search_lottie = st.columns([2, 1])
        with col_search_input:
            query = st.text_input("Enter keywords, document ID, or a natural language query:", placeholder="e.g., 'Maintenance report Q3', 'invoice from ABC Corp', 'Safety guidelines'")
            
            col_search_btn, col_voice_btn, col_search_filter = st.columns([2, 1, 3])
            with col_search_btn:
                search_button = st.button("Perform Smart Search")
            with col_voice_btn:
                st.button("🎤", help="Voice Search (EN/ML)")
            with col_search_filter:
                document_type_filter = st.multiselect("Filter by Document Type", ["Report", "Invoice", "Drawing", "Policy", "Minutes", "Legal", "Other"], default=[])

        with col_search_lottie:
            if search_lottie:
                st_lottie(search_lottie, height=200, key="search_animation")

        st.markdown("---")

        if search_button and query:
            st.success(f"Searching for: **'{query}'** (Filters: {', '.join(document_type_filter) if document_type_filter else 'None'})")
            with st.spinner("Retrieving results from ElasticSearch..."):
                import time
                time.sleep(2) # Simulate search time

            # Sample search results
            results_data = {
                "Document ID": ["DOC-1023", "DOC-2087", "DOC-1150", "DOC-0998"],
                "Title": ["Metro Line 1 Maintenance Report Q3 2023", "Invoice ABC Corp #4567 for Q2", "Updated Safety Protocol for Station Operations", "October Board Meeting Minutes"],
                "Type": ["Report", "Invoice", "Policy", "Minutes"],
                "Relevance Score": [0.95, 0.88, 0.82, 0.75],
                "Preview": ["Summary: Overview of routine maintenance tasks...", "Summary: Details of materials supplied by...", "Summary: New guidelines for emergency...", "Summary: Key decisions on budget allocation..."]
            }
            df_results = pd.DataFrame(results_data)

            # Apply simple filter for demonstration
            if document_type_filter:
                df_results = df_results[df_results["Type"].isin(document_type_filter)]

            if not df_results.empty:
                st.subheader("Search Results")
                for index, row in df_results.iterrows():
                    st.markdown(f"#### {row['Title']} (ID: {row['Document ID']})")
                    st.markdown(f"**Type:** {row['Type']} | **Relevance:** {row['Relevance Score']:.0%}")
                    with st.expander("Read Preview"):
                        st.write(row['Preview'])
                    
                    col_view, col_pin = st.columns(2)
                    with col_view:
                        st.button("View Document", key=f"view_{row['Document ID']}")
                    with col_pin:
                        st.button("📌 Pin for Later", key=f"pin_{row['Document ID']}")

                    st.markdown("---")

                # Contextual Recommendations
                st.subheader("You Might Also Be Interested In...")
                st.info("""
                - **DOC-1024:** Metro Line 2 Maintenance Report Q3 2023
                - **DOC-1151:** Annual Safety Drill Report
                - **DOC-0999:** September Board Meeting Minutes
                """)

            else:
                st.warning("No documents found matching your query and filters.")
        elif search_button:
            st.warning("Please enter a search query.")
        
        st.markdown("---")
        
        # --- FAQ Section for Search ---
        st.subheader("Frequently Asked Questions (FAQ)")
        with st.expander("How does Voice Search work?"):
            st.write("""
            Clicking the microphone icon (🎤) will activate your device's microphone. Your speech is then converted into text using an AI-powered Speech-to-Text service that supports both English and Malayalam. This text is then used as your search query.
            """)
        with st.expander("What are Contextual Recommendations?"):
            st.write("""
            After you perform a search, our system analyzes the content of the top results and suggests other documents that are semantically similar. This helps you discover related information that you might not have found with your initial keywords.
            """)
        with st.expander("Where do my Pinned Documents go?"):
            st.write("""
            When you pin a document, it's added to a personal 'bookmarks' list associated with your user account. This feature is designed for quick access to important or frequently used files. You will be able to access your full list of pinned documents from the sidebar in a future update.
            """)
        with st.expander("Can I use advanced search operators?"):
            st.write("""
            Yes, you can use operators like `AND`, `OR`, `NOT`, and quotes for exact phrases (e.g., `"safety protocol"`) to refine your search results. This allows for more precise and powerful querying of the document database.
            """)


        with st.expander("🛠️ Functions and Technologies on Search Page"):
            st.write("""
            - **Voice Search (Frontend & Backend)**: A microphone button (`st.button`) would trigger a frontend JavaScript component to capture audio. This audio is then sent to a backend API, which uses a **Speech-to-Text service (e.g., Google Cloud Speech-to-Text, Whisper AI)** to transcribe the speech into a query string for both English and Malayalam.
            - **Contextual Recommendations (Backend NLP)**: After a search, the system provides recommendations based on document similarity (content-based filtering using NLP embeddings). This helps users discover relevant documents they weren't explicitly looking for.
            - **Pin/Bookmark Functionality**: A user's pinned documents would be stored either in `st.session_state` for the current session or, for persistence, in a user profile within the main **PostgreSQL/MongoDB** database.
            - **Text Input & Buttons (`st.text_input`, `st.button`):** User interface for entering search queries and initiating searches.
            - **Multi-select Filter (`st.multiselect`):** Allows users to refine searches by document type.
            - **ElasticSearch (Backend):** This is the core technology. When a query is submitted, it's sent to the **ElasticSearch** index.
                - **Full-Text Search:** ElasticSearch performs fast and relevant full-text searches on document content and summaries.
                - **Faceted Search:** Filters by document type are handled efficiently by ElasticSearch's aggregation capabilities.
                - **Semantic Search (NLP):** If the query involves natural language, NLP models (e.g., **Hugging Face sentence transformers**) can convert the query into an embedding, which ElasticSearch then uses for vector similarity search to find semantically similar documents.
            - **Relevance Ranking:** ElasticSearch provides relevance scores to order results.
            - **Backend API (Flask/Django):** Handles the communication between Streamlit and ElasticSearch, processes queries, and formats results.
            """)

    # ---------- ANALYTICS ----------
    elif menu == "Analytics":
        st.subheader("📈 Analytics & Insights")
        st.info("Unlock meaningful insights from your document data. Visualize trends, identify bottlenecks, and monitor system usage.")

        if analytics_lottie:
            st_lottie(analytics_lottie, height=200, key="analytics_animation")
        st.markdown("---")

        # --- Compliance Score Dashboard ---
        st.subheader("Compliance & Efficiency Scores")
        col_score, col_latency, col_bottleneck = st.columns(3)
        with col_score:
            st.metric(label="Compliance Score", value="95.7%", delta="+1.2% vs. last month")
        with col_latency:
            st.metric(label="Avg. Decision Latency", value="48 Hours", delta="-5 hours vs. last month")
        with col_bottleneck:
            st.metric(label="Top Bottleneck Dept", value="Finance")
        
        st.markdown("---")


        col_chart1, col_chart2 = st.columns(2)

        with col_chart1:
            st.markdown("#### Decision Latency Report (Time to First Action)")
            latency_data = {
                "Document Type": ["Invoice", "Report", "Policy", "Legal"],
                "Avg. Latency (Hours)": [24, 55, 72, 40]
            }
            df_latency = pd.DataFrame(latency_data)
            fig_latency = px.bar(df_latency, x="Document Type", y="Avg. Latency (Hours)",
                                 title="Average Time from Upload to Action",
                                 color="Document Type",
                                 labels={"Avg. Latency (Hours)": "Average Hours"})
            st.plotly_chart(fig_latency, use_container_width=True)

        with col_chart2:
            st.markdown("#### Bottleneck Analysis (Department Review Times)")
            bottleneck_data = {
                "Department": ["Finance", "Legal", "Operations", "Maintenance", "HR"],
                "Avg. Review Time (Hours)": [68, 45, 30, 24, 18]
            }
            df_bottleneck = pd.DataFrame(bottleneck_data)
            fig_bottleneck = px.bar(df_bottleneck, x="Department", y="Avg. Review Time (Hours)",
                                    title="Average Document Review Time by Department",
                                    color="Department",
                                    color_discrete_sequence=px.colors.qualitative.Plotly)
            st.plotly_chart(fig_bottleneck, use_container_width=True)


        st.markdown("---")
        
        # --- Contributors Board ---
        st.markdown("#### Contributors Board (Top Departments by Uploads)")
        contributors_data = {
            "Department": ["Maintenance", "Operations", "Finance", "HR", "Legal"],
            "Uploads (Last 30 Days)": [120, 95, 60, 45, 20]
        }
        df_contributors = pd.DataFrame(contributors_data)
        fig_contributors = px.bar(df_contributors, x="Department", y="Uploads (Last 30 Days)",
                                title="Department Uploads in the Last 30 Days",
                                color="Department",
                                color_discrete_sequence=px.colors.qualitative.Safe)
        st.plotly_chart(fig_contributors, use_container_width=True)


        st.markdown("---")
        st.markdown("#### Top 5 Most Searched Keywords")
        # Sample data for keywords
        keywords_data = {
            "Keyword": ["Metro Line Expansion", "Safety Audit", "Vendor Contract", "Financial Report Q3", "Daily Operations"],
            "Search Count": [150, 120, 90, 80, 75]
        }
        df_keywords = pd.DataFrame(keywords_data)
        fig_keywords = px.bar(df_keywords.sort_values("Search Count", ascending=True),
                              x="Search Count", y="Keyword", orientation='h',
                              title="Most Frequent Search Terms",
                              color_discrete_sequence=["#2ca02c"]) # Green bars
        st.plotly_chart(fig_keywords, use_container_width=True)

        st.markdown("---")
        
        # --- FAQ Section for Analytics ---
        st.subheader("Frequently Asked Questions (FAQ)")
        with st.expander("What is the Contributors Board?"):
            st.write("""
            The Contributors Board is a chart that ranks departments based on the number of documents they have uploaded in the last 30 days. It helps to visualize which departments are most active in contributing to the system and promotes organizational engagement.
            """)
        with st.expander("What is 'Decision Latency'?"):
            st.write("""
            Decision Latency measures the average time it takes for a document to receive its first staff action (like being reviewed or approved) after it has been uploaded. A lower latency indicates a more efficient workflow.
            """)
        with st.expander("How do you identify a 'Bottleneck' department?"):
            st.write("""
            The Bottleneck Analysis chart shows the average time each department takes to review documents assigned to them. The department with the longest average review time is identified as a potential bottleneck, helping managers focus on process improvements.
            """)
        with st.expander("What does the 'Compliance Score' represent?"):
            st.write("""
            This score represents the percentage of regulatory or time-sensitive documents that were acted upon *before* their specified deadlines. A higher score indicates better adherence to compliance schedules.
            """)
        with st.expander("Can I export these charts and reports?"):
            st.write("""
            Currently, you can view these analytics within the application. A feature to export charts as images and data as CSV files is planned for a future release to support offline reporting and presentations.
            """)

        with st.expander("🛠️ Functions and Technologies on Analytics Page"):
            st.write("""
            - **Contributors Board**: Visualizes data aggregated from the document metadata (e.g., department of uploader) to create a leaderboard, fostering engagement and highlighting active departments.
            - **Decision Latency & Bottleneck Analysis**: These reports are generated by running aggregation queries on the document metadata stored in **PostgreSQL/MongoDB**. The system calculates the time difference between document upload timestamps and the timestamps of the first staff action (e.g., status change from 'Pending' to 'In Review').
            - **Compliance Score Dashboard (`st.metric`)**: This metric is calculated by a backend job that regularly checks regulatory documents against their deadlines. It computes the percentage of documents acted upon in time and displays it with a comparison delta.
            - **Data Aggregation (Backend & Database/ElasticSearch):** Analytics charts are powered by aggregated data from **PostgreSQL/MongoDB** (for structured metadata) and **ElasticSearch** (for operational metrics like search counts).
            - **Plotly Express (`plotly.express`):** Used for creating interactive and visually rich charts:
                - **Line Charts:** For showing trends over time (e.g., monthly uploads).
                - **Bar Charts:** For comparing categories (e.g., document status, top keywords, latency, and bottleneck analysis).
                - **Pie Charts (on Dashboard):** For showing distribution.
            - **Data Processing (Pandas):** Data fetched from the backend is processed and formatted using **Pandas DataFrames** before being visualized.
            - **Backend Analytics Engine (Flask/Django):** A dedicated backend service calculates and provides the aggregated data required for these visualizations.
            """)

    # ---------- ABOUT ----------
    elif menu == "About":
        st.subheader("ℹ️ About AkshRail: Powering Kochi Metro's Future")
        st.write("AkshRail is a brainchild developed to tackle the challenges of document overload and information fragmentation at Kochi Metro Rail Limited.")
        
        st.markdown("---")

        with st.expander("🏢 Overall Project Structure", expanded=True):
            st.write("""
            The AkshRail project is built on a modern, multi-tiered architecture designed for scalability and maintainability:
            - **Frontend (UI Layer):** Developed with **Streamlit**, this is the user-facing interface. It provides an interactive and intuitive web application for document uploads, search, and analytics visualization.
            - **Backend (API & Logic Layer):** A robust **Flask/Django** server acts as the central nervous system. It handles user authentication, manages API endpoints, and orchestrates the entire document processing workflow.
            - **AI Services (Intelligence Layer):** This layer contains the core AI/ML models for OCR (Tesseract), NLP (SpaCy, Hugging Face for summarization, classification, and embeddings), and Speech-to-Text. These services are called by the backend to process documents.
            - **Data Stores (Persistence Layer):**
                - **PostgreSQL/MongoDB:** For storing structured metadata (like document ID, title, user info, timestamps) and processed NLP data.
                - **ElasticSearch:** A powerful search engine for indexing all document content and enabling fast, full-text, and semantic searches.
                - **Cloud Storage (AWS S3/GCS):** For securely storing the original uploaded document files.
            """)

        with st.expander("🔄 Detailed Data Flow"):
            st.write("""
            This section illustrates how data moves through the AkshRail system.

            **1. User Interaction (Frontend):**
               - **Upload:** A user uploads a document file (e.g., PDF, JPG) through the Streamlit web interface.
               - **Search/Analytics:** A user submits a search query or accesses the analytics dashboard.

            **2. Backend API (Logic Layer):**
               - The **Flask/Django** server receives the request from the frontend.
               - For uploads, it first saves the original file to **Secure Cloud Storage** (like AWS S3).
               - It then places a processing job into a **Task Queue** (like Celery with Redis) to avoid blocking the user's session.

            **3. Asynchronous Processing (AI Services):**
               - **OCR Engine:** A worker process picks up the job. If the file is an image or scanned PDF, it's sent to the OCR engine to extract raw text.
               - **NLP Pipeline:** The extracted text is then passed to the NLP pipeline for:
                 - **Summarization & Classification:** Creating a concise summary and automatically determining the document type (e.g., 'Invoice').
                 - **Indexing:** The processed text and metadata are sent to two destinations.

            **4. Data Storage (Persistence Layer):**
               - **Database (PostgreSQL/MongoDB):** The document's metadata (title, user, date, confidentiality) and the AI-generated summary are stored.
               - **ElasticSearch:** The full extracted text and key metadata are indexed, making the entire document content searchable.

            **5. Data Retrieval:**
               - **For Search:** When a user searches, the query hits the backend API, which in turn queries the powerful **ElasticSearch** engine to get relevant results instantly.
               - **For Analytics:** When a user opens the Analytics page, the backend API queries the **Database** for aggregated data (e.g., upload counts by department) to build the charts.

            **6. Displaying Results:**
               - The backend API sends the formatted results (search results or analytics data) back to the **Streamlit UI**, where it is displayed to the user.
            """)
        
        with st.expander("⚙️ Backend Architecture"):
            st.write("""
            The backend is designed as a set of microservices or modular components to ensure separation of concerns and independent scaling.
            - **API Server (Flask/Django):** Exposes RESTful APIs for the Streamlit frontend to consume. It handles requests for uploads, searches, analytics, and user management. It does not perform heavy processing itself.
            - **Task Queue (Celery with Redis/RabbitMQ):** When a new document is uploaded, the API server places a processing job into a queue. This prevents the API from getting blocked by long-running tasks.
            - **Worker Nodes:** These are separate processes that listen to the task queue.
                - **OCR Worker:** Picks up jobs for scanned documents and runs them through the Tesseract OCR engine.
                - **NLP Worker:** Takes the extracted text and runs it through various NLP models for cleaning, summarization, entity recognition, classification, and duplicate checking.
            - **Scheduler (Celery Beat):** Manages periodic tasks, such as generating daily/weekly analytics reports or re-indexing documents.
            - **Database & Search Cluster:** The workers interact directly with PostgreSQL/MongoDB to store metadata and ElasticSearch to index the content, making it available for search.
            """)
        
        st.markdown("---")

        col_about_text, col_about_lottie = st.columns([2, 1])
        with col_about_text:
            st.markdown("#### Our Vision")
            st.write("To establish a seamless, intelligent, and accessible document management ecosystem that enhances operational efficiency, fosters collaboration, and safeguards critical organizational knowledge for Kochi Metro.")
            st.markdown("#### The Team")
            st.write("This solution is developed by a dedicated team with expertise in AI, web development, and data management, committed to delivering a robust and user-friendly system.")
            st.markdown("#### Get in Touch")
            st.write("For support, feedback, or further inquiries, please contact our development team.")
        
        with col_about_lottie:
            if about_lottie:
                st_lottie(about_lottie, height=300, key="about_animation")

        st.markdown("---")
        
        st.markdown("#### 🚀 Built with Passion Using")
        st.info("""
        - **Python:** The backbone of our AI and backend logic.
        - **Streamlit:** For creating beautiful and interactive web applications with ease.
        - **Flask/Django:** Robust backend frameworks for API development and task management.
        - **AI (NLP & OCR):** The intelligence that powers summarization, search, and data extraction.
        - **ElasticSearch:** For lightning-fast, intelligent search and document indexing.
        - **PostgreSQL/MongoDB:** Reliable databases for structured and unstructured data storage.
        - **Cloud Storage:** For scalable and secure document storage (e.g., AWS S3, Google Cloud Storage).
        """)


        st.markdown("---")
        st.write("© 2025 AkshRail. All rights reserved.")


# --- Main Logic: Show login page or main app ---
if not st.session_state.get("authenticated"):
    login_page()
else:
    main_app()



