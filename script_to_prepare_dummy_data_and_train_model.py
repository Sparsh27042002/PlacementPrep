# -*- coding: utf-8 -*-
"""Script to Prepare Dummy Data and Train Model

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/14u-1b-2MXdK0xund_SOLyRa7S_wFbn6A
"""

import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

# --- Configuration for Dummy Data Generation ---

NUM_SAMPLES = 1000 # Number of synthetic data points
COMMON_SKILLS = [
    "Python", "Java", "C++", "DSA", "Algorithms", "Web Development", "Frontend", "Backend",
    "Machine Learning", "AI", "Cloud Computing", "AWS", "SQL", "Database Management",
    "Operating Systems", "Computer Networks", "Cybersecurity", "DevOps", "Competitive Programming"
]
COLLEGE_TIERS = ["Tier 1", "Tier 2", "Tier 3"]
MIN_CGPA = 6.0
MAX_CGPA = 10.0
MIN_MCQ_SCORE = 0
MAX_MCQ_SCORE = 20 # 10 domain + 10 coding/DSA
BASE_PACKAGE_RANGE = (4.0, 25.0) # LPA in Lakhs per Annum

# --- Generate Synthetic Data ---
data = {
    'CGPA': np.random.uniform(MIN_CGPA, MAX_CGPA, NUM_SAMPLES).round(1),
    'College_Tier': np.random.choice(COLLEGE_TIERS, NUM_SAMPLES, p=[0.3, 0.4, 0.3]),
    'MCQ_Score': np.random.randint(MIN_MCQ_SCORE, MAX_MCQ_SCORE + 1, NUM_SAMPLES),
}

# Add skill columns as boolean features (0 or 1)
for skill in COMMON_SKILLS:
    data[skill.replace(" ", "_").lower()] = np.random.randint(0, 2, NUM_SAMPLES) # Randomly assign skill presence

df_dummy = pd.DataFrame(data)

# --- Define Package Generation Logic (Simulated) ---
def generate_package(row):
    package = np.random.uniform(BASE_PACKAGE_RANGE[0], BASE_PACKAGE_RANGE[1]) # Base random package

    # Adjust based on CGPA
    package += (row['CGPA'] - MIN_CGPA) * 0.8 # Higher CGPA, higher package

    # Adjust based on College Tier
    if row['College_Tier'] == 'Tier 1':
        package *= 1.5 # Tier 1 gets significant boost
    elif row['College_Tier'] == 'Tier 2':
        package *= 1.2 # Tier 2 gets moderate boost
    else: # Tier 3
        package *= 1.0 # Base for Tier 3

    # Adjust based on MCQ Score
    package += (row['MCQ_Score'] / MAX_MCQ_SCORE) * 3.0 # Higher MCQ score, higher package

    # Adjust based on skills (more skills = higher package)
    skill_count = sum(row[skill.replace(" ", "_").lower()] for skill in COMMON_SKILLS)
    package += skill_count * 0.5 # Each skill adds 0.5 LPA

    # Add some noise
    package += np.random.normal(0, 0.5)

    # Ensure package is within a reasonable range
    package = max(BASE_PACKAGE_RANGE[0], min(package, BASE_PACKAGE_RANGE[1] + 10.0)) # Cap at max base + 10 LPA

    return round(package, 2)

df_dummy['Package_LPA'] = df_dummy.apply(generate_package, axis=1)

# --- Preprocessing for Model Training ---

# Encode College_Tier
le = LabelEncoder()
df_dummy['College_Tier_Encoded'] = le.fit_transform(df_dummy['College_Tier'])
# Map labels to numeric values directly for interpretability: Tier 1 -> 2, Tier 2 -> 1, Tier 3 -> 0
# (You can adjust mapping as needed, e.g., 3,2,1)
tier_mapping = {label: idx for idx, label in enumerate(le.classes_)}
# Reverse mapping to assign higher value to Tier 1
# Assuming le.classes_ are sorted alphabetically if not specified.
# Let's explicitly map: Tier 1=3, Tier 2=2, Tier 3=1
# A better way is to use OneHotEncoder if there's no inherent order assumed by model,
# but for RandomForest/LinearRegression, direct numeric is often fine with careful mapping.
df_dummy['College_Tier_Encoded'] = df_dummy['College_Tier'].map({"Tier 3": 1, "Tier 2": 2, "Tier 1": 3})


# Define features (X) and target (y)
feature_cols = ['CGPA', 'College_Tier_Encoded', 'MCQ_Score'] + [s.replace(" ", "_").lower() for s in COMMON_SKILLS]
X = df_dummy[feature_cols]
y = df_dummy['Package_LPA']

# --- Train Model ---
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X, y)

# --- Save Model and All Skills ---
joblib.dump(model, 'package_predictor_model.pkl')
joblib.dump(COMMON_SKILLS, 'all_train_skills.pkl') # Save the list of skills the model was trained on

print("Dummy data generated, model trained, and saved successfully:")
print(f"  - Model: package_predictor_model.pkl")
print(f"  - Skills list: all_train_skills.pkl")
print("\nSample of generated data:")
print(df_dummy.head())
print(f"\nModel R^2 score: {model.score(X, y):.2f}") # Evaluate on training data



import streamlit as st
import numpy as np
import pandas as pd
import joblib
import os
import json # Used for parsing JSON from LLM response if needed, but not directly in simulation
# import requests # Uncomment for actual API calls in non-Canvas env

# --- Configuration for Simulated Data and Logic ---

# Define streams
STREAMS = ["Computer Science Engineering (CSE)", "Electronics & Communication Engineering (ECE)",
           "Mechanical Engineering", "Civil Engineering", "Electrical Engineering"]

# Since we're focusing on CSE initially, MCQs are defined for CSE
# 10 Domain Questions
CSE_DOMAIN_MCQS = [
    {"question": "Which of these is a process management concept in Operating Systems?",
     "options": ["Memory Segmentation", "Deadlock", "File System", "Disk Scheduling"], "correct": "Deadlock"},
    {"question": "What is the primary purpose of SQL 'JOIN' clause?",
     "options": ["To combine rows from two or more tables", "To filter records", "To sort data", "To group data"], "correct": "To combine rows from two or more tables"},
    {"question": "Which network topology connects all devices to a central hub?",
     "options": ["Ring", "Bus", "Star", "Mesh"], "correct": "Star"},
    {"question": "What is an abstract class in Java?",
     "options": ["A class that cannot be instantiated", "A class with no methods", "A class that can only have static members", "A class that inherits from another class"], "correct": "A class that cannot be instantiated"},
    {"question": "In cybersecurity, what is phishing?",
     "options": ["A type of malware", "Attempting to acquire sensitive information by masquerading as a trustworthy entity", "A technique to encrypt data", "A network attack that floods a system with traffic"], "correct": "Attempting to acquire sensitive information by masquerading as a trustworthy entity"},
    {"question": "Which HTTP method is typically used to retrieve data from a server?",
     "options": ["POST", "PUT", "GET", "DELETE"], "correct": "GET"},
    {"question": "What is the purpose of 'git clone'?",
     "options": ["To commit changes", "To create a new branch", "To copy a repository from a remote source", "To merge branches"], "correct": "To copy a repository from a remote source"},
    {"question": "Which cloud computing service model provides virtualized computing resources over the internet?",
     "options": ["SaaS", "PaaS", "IaaS", "DaaS"], "correct": "IaaS"},
    {"question": "What is a 'foreign key' in a relational database?",
     "options": ["A key that uniquely identifies a record", "A key that links two tables together", "A key used for encryption", "A key that sorts records"], "correct": "A key that links two tables together"},
    {"question": "What is polymorphism in Object-Oriented Programming?",
     "options": ["Ability of an object to take on many forms", "Concept of data hiding", "Creating multiple instances of a class", "Mechanism of combining data and code"], "correct": "Ability of an object to take on many forms"},
]

# 10 Coding and DSA Basic Questions
CODING_DSA_MCQS = [
    {"question": "What is the worst-case time complexity of Quick Sort?",
     "options": ["O(n log n)", "O(n^2)", "O(log n)", "O(n)"], "correct": "O(n^2)"},
    {"question": "Which data structure uses LIFO (Last-In, First-Out) principle?",
     "options": ["Queue", "Linked List", "Stack", "Array"], "correct": "Stack"},
    {"question": "What is the output of `print(2 + 3 * 4)` in Python?",
     "options": ["20", "14", "24", "10"], "correct": "14"},
    {"question": "Which of these is a valid way to create a list in Python?",
     "options": ["list = (1, 2, 3)", "list = [1, 2, 3]", "list = {1, 2, 3}", "list = <1, 2, 3>"], "correct": "list = [1, 2, 3]"},
    {"question": "What is the base case in a recursive function?",
     "options": ["The condition that stops the recursion", "The condition that causes an infinite loop", "The main function call", "The first call to the function"], "correct": "The condition that stops the recursion"},
    {"question": "Which algorithm is used to find the shortest path in a weighted graph?",
     "options": ["DFS", "BFS", "Dijkstra's Algorithm", "Kruskal's Algorithm"], "correct": "Dijkstra's Algorithm"},
    {"question": "What is hashing primarily used for?",
     "options": ["Sorting data", "Encrypting data", "Fast data retrieval", "Compressing data"], "correct": "Fast data retrieval"},
    {"question": "If an array has 'n' elements, what is the maximum number of comparisons in a bubble sort in the worst case?",
     "options": ["n", "n log n", "n^2", "n^2 / 2"], "correct": "n^2"},
    {"question": "What is the purpose of 'else' in an 'if-else' statement?",
     "options": ["To execute code if the condition is true", "To execute code if the condition is false", "To loop through code", "To declare a variable"], "correct": "To execute code if the condition is false"},
    {"question": "Which of these is NOT a common tree traversal method?",
     "options": ["Inorder", "Preorder", "Postorder", "Depth-first"], "correct": "Depth-first"}, # DFS is an approach, not a traversal method name like In/Pre/Postorder
]

ALL_MCQS = CSE_DOMAIN_MCQS + CODING_DSA_MCQS

# Maps for user-friendly display to model input
COLLEGE_TIER_MAPPING = {"Tier 1": 3, "Tier 2": 2, "Tier 3": 1} # Higher value for better tier

# --- Load Model and Skills ---
MODEL_PATH = 'package_predictor_model.pkl'
SKILLS_LIST_PATH = 'all_train_skills.pkl'

@st.cache_resource # Cache the model and skills list loading
def load_resources():
    model = None
    all_train_skills = []
    try:
        model = joblib.load(MODEL_PATH)
        all_train_skills = joblib.load(SKILLS_LIST_PATH)
        return model, all_train_skills
    except FileNotFoundError:
        st.error(f"Error: Required files not found. Please run 'prepare_model_data.py' first.")
        st.stop()
    except Exception as e:
        st.error(f"An error occurred while loading resources: {e}")
        st.stop()

model, all_train_skills = load_resources()

# --- Helper Functions ---

def calculate_mcq_score(mcqs_set, user_answers):
    """Calculates the score for a specific set of MCQs."""
    score = 0
    for i, mcq in enumerate(mcqs_set):
        key = f"q_{i}_{'domain' if mcqs_set == CSE_DOMAIN_MCQS else 'coding_dsa'}"
        if user_answers.get(key) == mcq["correct"]:
            score += 1
    return score

# --- LLM Integration (Simulated for Canvas Environment) ---
@st.cache_data(show_spinner=False)
def get_llm_roadmap(stream, mcq_score, strengths_input_str, expected_package_lpa, target_package_lpa, time_left_months):
    """Generates a roadmap using the Gemini API."""
    prompt = f"""
    Generate a personalized career roadmap for a student in {stream}.
    The student's combined basic technical understanding (based on MCQs) is {mcq_score}/{len(ALL_MCQS)}.
    Their self-identified strengths/skills include: {strengths_input_str if strengths_input_str else 'None explicitly mentioned'}.
    Their estimated current package is {expected_package_lpa} LPA.
    Their target package is approximately {target_package_lpa} Lakhs per Annum (LPA) within the next {time_left_months} months.

    The roadmap should be structured into these sections:
    1.  **Core Technical Skill Development:** Specific to their stream and aimed at improving their current basic understanding. Focus heavily on DSA and programming fundamentals given the MCQ score.
    2.  **Advanced / Niche Skill Acquisition:** Based on their target package, suggesting specialized skills relevant to high-paying roles in {stream}.
    3.  **Project Work & Portfolio Building:** Types of projects to undertake to showcase skills.
    4.  **Soft Skills & Communication:** Importance and how to develop for professional growth.
    5.  **Interview Preparation Strategy:** What to focus on for cracking interviews (Technical and HR).
    6.  **Networking & Job Search:** Tips for finding and securing opportunities.

    Provide actionable, specific advice for each section, considering the time constraint. Ensure the advice is practical and progressive. Format the output as Markdown.
    """

    llm_api_key = "" # Leave as empty string for Canvas. Gemini will inject API key at runtime.
    llm_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={llm_api_key}"

    chat_history = [{"role": "user", "parts": [{"text": prompt}]}]
    payload = {"contents": chat_history}

    headers = {'Content-Type': 'application/json'}

    try:
        with st.spinner("Generating personalized roadmap... This might take a moment."):
            # --- Simulated LLM Response for Canvas Environment ---
            st.info("Simulating LLM response for roadmap generation. In a real deployment, this would call Gemini API.")
            simulated_roadmap = f"""
            **Comprehensive Roadmap for a {stream} Student to Achieve {target_package_lpa} LPA in {time_left_months} Months:**

            Your current MCQ score of **{mcq_score}/{len(ALL_MCQS)}** indicates a foundation that needs strengthening, particularly in core DSA and programming fundamentals. Your self-identified strengths like **"{strengths_input_str}"** are a good starting point. This roadmap will guide you from your current estimated package of **{expected_package_lpa} LPA** to your target of **{target_package_lpa} LPA**.

            1.  **Core Technical Skill Development (Months 1-{min(time_left_months, 4)}):**
                * **Data Structures & Algorithms (DSA):** This is paramount. Dedicate 2-3 hours daily.
                    * **Concepts:** Master Arrays, Linked Lists, Stacks, Queues, Trees (BSTs, Heaps), Graphs (BFS, DFS), Hash Maps.
                    * **Algorithms:** Sorting (Merge, Quick), Searching (Binary Search), Recursion, Dynamic Programming (basic problems), Greedy algorithms.
                    * **Practice:** Solve at least 100-150 problems on platforms like LeetCode (Easy & Medium), HackerRank, or GeeksforGeeks. Prioritize frequently asked interview questions.
                * **Programming Language Proficiency:** Deepen your expertise in **Python/Java/C++** (whichever you prefer for coding interviews). Understand its standard library, nuances, and Object-Oriented Programming (OOP) concepts thoroughly.
                * **Core CS Fundamentals:** Revise key concepts from Operating Systems (Process Management, Memory Management), Database Management Systems (SQL queries, normalization, ACID properties), and Computer Networks (OSI/TCP-IP model, common protocols). Aim for conceptual clarity.

            2.  **Advanced / Niche Skill Acquisition (Months {min(time_left_months, 5)}-{min(time_left_months, 10)}):**
                * To reach {target_package_lpa} LPA, specialization is key. Based on typical high-paying CSE roles, consider:
                    * **Full-Stack Web Development:** (If you enjoy building applications) Choose a modern stack (e.g., MERN: MongoDB, Express.js, React, Node.js; or Django/Flask with React/Vue). Build at least 2 complex web apps.
                    * **Machine Learning/AI:** (If you have a strong math/stats background) Learn Python libraries (NumPy, Pandas, Scikit-learn, TensorFlow/PyTorch). Focus on supervised/unsupervised learning, deep learning basics. Complete 1-2 ML projects end-to-end.
                    * **Cloud Computing:** (Highly in-demand) Get a foundational certification like AWS Cloud Practitioner or Azure Fundamentals. Understand cloud services (compute, storage, networking, databases).
                    * **DevOps/SRE:** (If interested in infrastructure) Learn Docker, Kubernetes, CI/CD tools (Jenkins/GitLab CI), and scripting (Bash/Python).
                * **Deep Dive:** Select **one** primary area and become proficient. Don't try to learn everything at once.

            3.  **Project Work & Portfolio Building (Concurrent with skill acquisition):**
                * **Minimum 3 Strong Projects:** Build projects that showcase your core and advanced skills.
                * **Variety:** Aim for projects that solve real-world problems or demonstrate complex functionalities (e.g., a full-stack e-commerce site, an ML-powered recommendation system, a cloud-deployed microservice).
                * **GitHub Portfolio:** Maintain a well-organized GitHub profile. Each project should have a clear README, screenshots/demos, and instructions for setup.
                * **Personal Website/Blog:** (Optional, but recommended) Create a simple website to host your projects and write about your learning journey.

            4.  **Soft Skills & Communication (Ongoing):**
                * **Problem Solving:** Actively practice critical thinking for coding and design problems.
                * **Communication:** Work on articulating technical concepts clearly. Practice explaining project architectures.
                * **Teamwork:** Participate in group projects, hackathons. Be a good collaborator.
                * **Active Listening:** Essential for understanding requirements and feedback.

            5.  **Interview Preparation Strategy (Months {time_left_months - 3}-{time_left_months}):**
                * **Company-Specific Prep:** Research companies you're targeting (values, culture, common interview questions).
                * **Technical Rounds:**
                    * **DSA:** Practice solving problems under timed conditions.
                    * **Core CS:** Be ready for questions on OS, DBMS, Networks, OOPs, etc.
                    * **System Design:** For higher packages, understand basic system design principles (scalability, reliability, databases, APIs).
                * **Behavioral/HR Rounds:** Prepare common HR questions like "Tell me about yourself," "Why this company?", "Strengths/Weaknesses," "Conflict resolution." Have STAR (Situation, Task, Action, Result) stories ready.
                    * **Mock Interviews:** Conduct mock interviews with peers, seniors, or professional services. Get constructive feedback.

            6.  **Networking & Job Search (Months {time_left_months - 2}-{time_left_months}):**
                * **LinkedIn:** Optimize your profile with keywords, showcase projects, and connect with recruiters and professionals in your target companies/industries.
                * **Job Boards:** Actively apply on platforms like LinkedIn Jobs, Indeed, Naukri, Glassdoor, and company career pages.
                * **Referrals:** Reach out to your alumni network, professors, or industry contacts for referrals. Referrals significantly boost chances.
                * **Career Fairs:** Attend campus or virtual career fairs.
                * **Tailor Applications:** Customize your resume and cover letter for each job application.

            **Market Trends (General Guidance):**
            Currently, the market values strong problem-solvers with practical project experience and specialization in areas like AI/ML, Cloud, and advanced Web/Mobile development. Adaptability and continuous learning are key.

            Remember, consistency is key. Even small, daily efforts accumulate into significant progress over time. Good luck with your placements!
            """
            return simulated_roadmap
            # --- End Simulated LLM Response ---

    except Exception as e:
        st.error(f"Failed to generate roadmap: {e}")
        return "Could not generate roadmap. Please try again."


# --- Streamlit UI ---
st.set_page_config(page_title="Career Navigator: Insights & Roadmap", layout="centered")

# --- Custom CSS for Background Image and Styling ---
background_image_url = "https://images.unsplash.com/photo-1549247775-6e4693a1c1d0?q=80&w=2940&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D" # Example: A subtle, abstract tech/gradient image
background_css = f"""
<style>
.stApp {{
    background-image: url("{background_image_url}");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    background-attachment: fixed;
}}
.stApp::before {{
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(255, 255, 255, 0.75);
    z-index: -1;
}}
.main .block-container {{
    background-color: rgba(255, 255, 255, 0.95);
    border-radius: 12px;
    padding: 2.5rem;
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
    margin-top: 2rem;
    margin-bottom: 2rem;
}}
h1, h2, h3, h4, h5, h6 {{
    color: #1a202c;
}}
p, li, div[data-testid="stText"], label {{
    color: #4a5568;
}}
</style>
"""
st.markdown(background_css, unsafe_allow_html=True)


st.title("🚀 Career Navigator: Insights & Roadmap")
st.markdown("""
Welcome! Get personalized career insights and a roadmap to achieve your target package.
""")

# --- User Inputs ---
st.subheader("1. Your Academic & Background Details")

# Stream Selection (currently fixed to CSE)
selected_stream = st.selectbox(
    "Select your engineering stream:",
    options=["Computer Science Engineering (CSE)"], # Only CSE available for now
    index=0 # Default to CSE
)
st.session_state.selected_stream = selected_stream # Store in session state

# CGPA Input
cgpa = st.number_input(
    "Enter your current CGPA (e.g., 8.5):",
    min_value=0.0, max_value=10.0, value=st.session_state.get('cgpa', 8.0), step=0.1,
    help="Your academic performance helps estimate package."
)
st.session_state.cgpa = cgpa

# College Tier Input
college_tier = st.selectbox(
    "Select your College Tier:",
    options=["Tier 1", "Tier 2", "Tier 3"],
    index=st.session_state.get('college_tier_idx', 0), # Default to Tier 1
    help="This is a generalized classification for package estimation."
)
st.session_state.college_tier = college_tier
st.session_state.college_tier_idx = ["Tier 1", "Tier 2", "Tier 3"].index(college_tier) # Store index for consistency


st.subheader(f"2. Quick Technical Assessment for {selected_stream}")
st.markdown("Answer these questions to help us gauge your basic technical understanding.")

# Initialize session state for MCQ answers
if 'mcq_answers_domain' not in st.session_state:
    st.session_state.mcq_answers_domain = {}
if 'mcq_answers_coding_dsa' not in st.session_state:
    st.session_state.mcq_answers_coding_dsa = {}

# Display Domain MCQs
st.subheader("Domain Specific MCQs (CSE)")
for i, mcq in enumerate(CSE_DOMAIN_MCQS):
    st.session_state.mcq_answers_domain[f"q_{i}_domain"] = st.radio(
        f"{i+1}. {mcq['question']}",
        options=mcq["options"],
        key=f"domain_q_{i}",
        index=st.session_state.mcq_answers_domain.get(f"q_{i}_domain_idx", None)
    )
    # Store index to persist selection on rerun
    if st.session_state.mcq_answers_domain[f"q_{i}_domain"] in mcq["options"]:
        st.session_state.mcq_answers_domain[f"q_{i}_domain_idx"] = mcq["options"].index(st.session_state.mcq_answers_domain[f"q_{i}_domain"])
    else:
         st.session_state.mcq_answers_domain[f"q_{i}_domain_idx"] = None


# Display Coding and DSA MCQs
st.subheader("Coding & DSA Basic MCQs")
for i, mcq in enumerate(CODING_DSA_MCQS):
    st.session_state.mcq_answers_coding_dsa[f"q_{i}_coding_dsa"] = st.radio(
        f"{i+1}. {mcq['question']}",
        options=mcq["options"],
        key=f"coding_dsa_q_{i}",
         index=st.session_state.mcq_answers_coding_dsa.get(f"q_{i}_coding_dsa_idx", None)
    )
    # Store index to persist selection on rerun
    if st.session_state.mcq_answers_coding_dsa[f"q_{i}_coding_dsa"] in mcq["options"]:
        st.session_state.mcq_answers_coding_dsa[f"q_{i}_coding_dsa_idx"] = mcq["options"].index(st.session_state.mcq_answers_coding_dsa[f"q_{i}_coding_dsa"])
    else:
        st.session_state.mcq_answers_coding_dsa[f"q_{i}_coding_dsa_idx"] = None

# Calculate total MCQ score
mcq_score_domain = calculate_mcq_score(CSE_DOMAIN_MCQS, st.session_state.mcq_answers_domain)
mcq_score_coding_dsa = calculate_mcq_score(CODING_DSA_MCQS, st.session_state.mcq_answers_coding_dsa)
total_mcq_score = mcq_score_domain + mcq_score_coding_dsa

st.subheader("3. Your Skills & Ambitions")

# Skills Input
strengths_input_str = st.text_area(
    "List your current strengths, skills, or technologies you know (comma-separated):",
    value=st.session_state.get('strengths_input_str', ""),
    help="e.g., Python, Java, Data Structures, Web Development, Machine Learning"
)
st.session_state.strengths_input_str = strengths_input_str

# Target Package Input
target_package_lpa = st.number_input(
    "What is your target package (Lakhs per Annum - LPA)?",
    min_value=3.0, max_value=100.0, value=st.session_state.get('target_package_lpa', 10.0), step=0.5,
    help="Enter your desired salary package."
)
st.session_state.target_package_lpa = target_package_lpa

# Time Left Input
time_left_months = st.number_input(
    "How many months until your placements/job search begins?",
    min_value=1, max_value=48, value=st.session_state.get('time_left_months', 12), step=1,
    help="This helps tailor the roadmap timeline."
)
st.session_state.time_left_months = time_left_months

# --- Prediction and Roadmap Generation ---

if st.button("Get Career Insights & Roadmap"):
    # --- Prepare data for model prediction ---
    input_data = {skill: 0 for skill in all_train_skills}

    # Add user-input skills (simple presence check based on input string)
    if strengths_input_str:
        user_skills = [skill.strip() for skill in strengths_input_str.split(',')]
        for skill in user_skills:
            if skill in input_data:
                input_data[skill] = 1
            # Note: Skills not in all_train_skills are ignored for prediction

    # Add CGPA
    input_data['CGPA'] = cgpa

    # Add College Tier (using mapped value)
    input_data['College_Tier'] = COLLEGE_TIER_MAPPING.get(college_tier, 1) # Default to Tier 3 if mapping fails

    # Add MCQ Scores
    input_data['Domain_MCQ_Score'] = mcq_score_domain
    input_data['Coding_DSA_MCQ_Score'] = mcq_score_coding_dsa

    # Convert to DataFrame for model
    input_df = pd.DataFrame([input_data])

    # Ensure all training columns are present, fill missing with 0
    for skill in all_train_skills:
        if skill not in input_df.columns:
            input_df[skill] = 0

    # Reorder columns to match training data order if necessary (important for some model types)
    # Assuming all_train_skills is the correct order of feature names for the model
    feature_order = [skill for skill in all_train_skills if skill != 'Package_LPA'] # Exclude target if present
    # Add other features if not already in skills list (like CGPA, College_Tier, MCQ scores)
    other_features = ['CGPA', 'College_Tier', 'Domain_MCQ_Score', 'Coding_DSA_MCQ_Score']
    for feature in other_features:
        if feature not in feature_order:
            feature_order.append(feature)

    # Filter input_df to only include features in feature_order and in that order
    input_df = input_df[feature_order]


    # --- Make Prediction ---
    try:
        expected_package_lpa = model.predict(input_df)[0]
        expected_package_lpa = round(expected_package_lpa, 2) # Round for display

        st.subheader("🎯 Your Expected Package & Roadmap")
        st.success(f"Based on your inputs, your estimated package is: **{expected_package_lpa} LPA**")
        st.info(f"Your total technical MCQ score is: **{total_mcq_score}/{len(ALL_MCQS)}**")

        # --- Generate and Display Roadmap ---
        roadmap_content = get_llm_roadmap(
            selected_stream,
            total_mcq_score,
            strengths_input_str,
            expected_package_lpa,
            target_package_lpa,
            time_left_months
        )
        st.markdown("---")
        st.markdown(roadmap_content)

    except Exception as e:
        st.error(f"An error occurred during prediction: {e}")

st.markdown("---")
st.markdown("Disclaimer: This tool provides estimates and suggestions based on a trained model and LLM. Actual outcomes may vary.")



from pyngrok import ngrok
public_url = ngrok.connect(addr="8501", bind_tls=True)
print(f"Streamlit App URL: {public_url}")
