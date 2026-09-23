import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="SMARTMARK",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

.stApp {
    background: #f5f7fb;
}

/* Main title */
.hero {
    background: linear-gradient(135deg, #6c63ff, #8b5cf6);
    padding: 30px;
    border-radius: 20px;
    color: white;
    margin-bottom: 25px;
}

.hero h1 {
    font-size: 38px;
    margin: 0;
    font-weight: 800;
}

.hero p {
    font-size: 16px;
    margin-top: 8px;
    opacity: 0.9;
}

/* Metric cards */
div[data-testid="stMetric"] {
    background: white;
    border-radius: 16px;
    padding: 18px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 4px 12px rgba(0,0,0,0.06);
}

/* Section headings */
.section {
    background: white;
    padding: 18px 22px;
    border-radius: 16px;
    margin-top: 20px;
    margin-bottom: 15px;
    border: 1px solid #e5e7eb;
}

/* Student profile */
.profile-card {
    background: white;
    padding: 25px;
    border-radius: 18px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 4px 15px rgba(0,0,0,0.05);
}

/* Footer */
.footer {
    text-align: center;
    padding: 30px;
    color: #777;
    font-size: 14px;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    border-right: 1px solid #e5e7eb;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# DATA FILE
# =========================================================

DATA_FILE = Path(__file__).parent / "data" / "students.csv"

subjects = [
    "Mathematics",
    "Programming",
    "Database Management",
    "Computer Networks",
    "Web Technology"
]


# =========================================================
# LOAD DATA
# =========================================================

@st.cache_data
def load_data():

    if not DATA_FILE.exists():
        return None

    data = pd.read_csv(DATA_FILE)

    required_columns = [
        "Register Number",
        "Name",
        "Mathematics",
        "Programming",
        "Database Management",
        "Computer Networks",
        "Web Technology"
    ]

    missing = [
        col for col in required_columns
        if col not in data.columns
    ]

    if missing:
        return missing

    data["Register Number"] = (
        data["Register Number"]
        .astype(str)
        .str.strip()
    )

    data["Name"] = (
        data["Name"]
        .astype(str)
        .str.strip()
    )

    for subject in subjects:
        data[subject] = pd.to_numeric(
            data[subject],
            errors="coerce"
        )

    data[subjects] = data[subjects].fillna(0)

    return data


df = load_data()


# =========================================================
# ERROR CHECK
# =========================================================

if df is None:

    st.error("❌ students.csv file not found.")

    st.info(
        "Check: Student Mark Analysis → data → students.csv"
    )

    st.stop()


if isinstance(df, list):

    st.error("❌ Required columns are missing.")

    for item in df:
        st.write("•", item)

    st.stop()


# =========================================================
# CALCULATIONS
# =========================================================

df["Total Marks"] = df[subjects].sum(axis=1)

df["Average"] = df[subjects].mean(axis=1)


def calculate_grade(avg):

    if avg >= 90:
        return "A+"
    elif avg >= 80:
        return "A"
    elif avg >= 70:
        return "B"
    elif avg >= 60:
        return "C"
    elif avg >= 50:
        return "D"
    else:
        return "F"


def calculate_result(row):

    if (row[subjects] >= 40).all():
        return "Pass"

    return "Fail"


df["Grade"] = df["Average"].apply(calculate_grade)

df["Result"] = df.apply(
    calculate_result,
    axis=1
)


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.markdown("## 🎓 SMARTMARK")

st.sidebar.caption(
    "Student Examination Analysis"
)

st.sidebar.markdown("---")

page = st.sidebar.radio(
    "MENU",
    [
        "🏠 Dashboard",
        "👨‍🎓 Student Details",
        "📊 Performance Analysis",
        "📋 Marks Table"
    ]
)

st.sidebar.markdown("---")

st.sidebar.success(
    "System Status: Active"
)


# =========================================================
# DASHBOARD
# =========================================================

if page == "🏠 Dashboard":

    st.markdown("""
    <div class="hero">
        <h1>🎓 SMARTMARK</h1>
        <p>
        Student Examination Marks Analysis &
        Academic Performance Dashboard
        </p>
    </div>
    """, unsafe_allow_html=True)


    # Statistics

    total_students = len(df)

    class_average = df["Average"].mean()

    highest_mark = df[subjects].max().max()

    lowest_mark = df[subjects].min().min()

    passed = (df["Result"] == "Pass").sum()

    pass_percentage = (
        passed / total_students * 100
        if total_students > 0
        else 0
    )


    # Metrics

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        st.metric(
            "👨‍🎓 Students",
            total_students
        )

    with c2:
        st.metric(
            "📈 Class Average",
            f"{class_average:.2f}"
        )

    with c3:
        st.metric(
            "🏆 Highest",
            f"{highest_mark:.0f}"
        )

    with c4:
        st.metric(
            "📉 Lowest",
            f"{lowest_mark:.0f}"
        )

    with c5:
        st.metric(
            "✅ Pass Rate",
            f"{pass_percentage:.1f}%"
        )


    # Charts

    st.markdown(
        '<div class="section"><h3>📊 Academic Overview</h3></div>',
        unsafe_allow_html=True
    )

    c1, c2 = st.columns(2)


    with c1:

        subject_data = pd.DataFrame({
            "Subject": subjects,
            "Average Marks": [
                df[s].mean()
                for s in subjects
            ]
        })

        fig = px.bar(
            subject_data,
            x="Subject",
            y="Average Marks",
            text_auto=".1f"
        )

        fig.update_layout(
            yaxis=dict(range=[0, 100]),
            plot_bgcolor="white",
            paper_bgcolor="white"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    with c2:

        result_data = (
            df["Result"]
            .value_counts()
            .reset_index()
        )

        result_data.columns = [
            "Result",
            "Students"
        ]

        fig = px.pie(
            result_data,
            names="Result",
            values="Students",
            hole=0.5
        )

        fig.update_layout(
            paper_bgcolor="white"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # Top students

    st.markdown(
        '<div class="section"><h3>🏆 Top Performing Students</h3></div>',
        unsafe_allow_html=True
    )

    top_students = (
        df[
            [
                "Register Number",
                "Name",
                "Total Marks",
                "Average",
                "Grade",
                "Result"
            ]
        ]
        .sort_values(
            "Average",
            ascending=False
        )
        .head(5)
        .copy()
    )

    top_students["Average"] = (
        top_students["Average"].round(2)
    )

    st.dataframe(
        top_students,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# STUDENT DETAILS
# =========================================================

elif page == "👨‍🎓 Student Details":

    st.title("👨‍🎓 Student Details")

    st.caption(
        "Search and view individual student performance."
    )

    search = st.text_input(
        "🔎 Search Student",
        placeholder="Enter name or register number...")
    if search.strip():

        value = search.strip().lower()

        filtered = df[
            df["Name"]
            .astype(str)
            .str.lower()
            .str.contains(value, na=False)
            |
            df["Register Number"]
            .astype(str)
            .str.lower()
            .str.contains(value, na=False)
        ]

    else:

        filtered = df


    if filtered.empty:

        st.warning(
            "No student found."
        )

    else:

        options = (
            filtered["Register Number"]
            .astype(str)
            .tolist()
        )

        selected = st.selectbox(
            "Select Student",
            options,
            format_func=lambda x:
                str(
                    filtered.loc[
                        filtered["Register Number"].astype(str)
                        == str(x),
                        "Name"
                    ].iloc[0]
                )
                + "  •  "
                + str(x)
        )


        student = df[
            df["Register Number"].astype(str)
            == str(selected)
        ].iloc[0]


        st.markdown("---")


        # Profile

        st.markdown(
            '<div class="profile-card">',
            unsafe_allow_html=True
        )

        c1, c2, c3 = st.columns(3)

        with c1:
            st.markdown("### 👤 Student")
            st.write(str(student["Name"]))

        with c2:
            st.markdown("### 🆔 Register Number")
            st.write(str(student["Register Number"]))

        with c3:
            st.markdown("### 📌 Result")

            if student["Result"] == "Pass":
                st.success("PASS")
            else:
                st.error("FAIL")

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )


        st.markdown("---")


        # Metrics

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.metric(
                "Total Marks",
                f"{student['Total Marks']:.0f}/500"
            )

        with c2:
            st.metric(
                "Average",
                f"{student['Average']:.2f}"
            )

        with c3:
            st.metric(
                "Grade",
                str(student["Grade"])
            )

        with c4:
            st.metric(
                "Result",
                str(student["Result"])
            )


        st.markdown("---")


        # Marks

        st.subheader("📚 Subject-wise Marks")

        marks = pd.DataFrame({
            "Subject": subjects,
            "Marks": [
                float(student[s])
                for s in subjects
            ]
        })

        st.dataframe(
            marks,
            use_container_width=True,
            hide_index=True
        )


        # Chart

        st.subheader("📈 Performance Overview")

        fig = px.bar(
            marks,
            x="Subject",
            y="Marks",
            text_auto=".0f"
        )

        fig.update_layout(
            yaxis=dict(range=[0, 100]),
            plot_bgcolor="white",
            paper_bgcolor="white"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


# =========================================================
# PERFORMANCE ANALYSIS
# =========================================================

elif page == "📊 Performance Analysis":

    st.title("📊 Performance Analysis")

    st.caption(
        "Analyze overall academic performance."
    )


    st.subheader("📚 Subject-wise Average")

    subject_data = pd.DataFrame({
        "Subject": subjects,
        "Average Marks": [
            df[s].mean()
            for s in subjects
        ]
    })


    fig = px.bar(
        subject_data,
        x="Subject",
        y="Average Marks",
        text_auto=".1f"
    )

    fig.update_layout(
        yaxis=dict(range=[0, 100]),
        plot_bgcolor="white",
        paper_bgcolor="white"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


    st.subheader("👨‍🎓 Student Average Performance")

    student_avg = (
        df[
            ["Name", "Average"]
        ]
        .sort_values(
            "Average",
            ascending=False
        )
        .copy()
    )

    fig = px.bar(
        student_avg,
        x="Name",
        y="Average",
        text_auto=".1f"
    )

    fig.update_layout(
        yaxis=dict(range=[0, 100]),
        plot_bgcolor="white",
        paper_bgcolor="white"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# =========================================================
# MARKS TABLE
# =========================================================

elif page == "📋 Marks Table":

    st.title("📋 Student Marks Table")

    st.caption(
        "Complete examination marks and results."
    )


    columns = [
        "Register Number",
        "Name",
        "Mathematics",
        "Programming",
        "Database Management",
        "Computer Networks",
        "Web Technology",
        "Total Marks",
        "Average",
        "Grade",
        "Result"
    ]


    table = df[columns].copy()

    table["Average"] = (
        table["Average"].round(2)
    )


    st.dataframe(
        table,
        use_container_width=True,
        hide_index=True
    )


    st.markdown("---")


    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "👨‍🎓 Total",
            len(df)
        )

    with c2:
        st.metric(
            "✅ Passed",
            int(
                (df["Result"] == "Pass").sum()
            )
        )

    with c3:
        st.metric(
            "❌ Failed",
            int(
                (df["Result"] == "Fail").sum()
            )
        )


# =========================================================
# FOOTER
# =========================================================

st.markdown("""
<div class="footer">
    🎓 <b>SMARTMARK</b><br>
    Student Examination Marks Analysis System<br>
    Academic Performance Dashboard
</div>
""", unsafe_allow_html=True)
