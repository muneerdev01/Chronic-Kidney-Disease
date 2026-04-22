import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Kidney Disease Dashboard",
    page_icon="🫘",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #1e3a5f, #2d6a9f);
        border-radius: 12px; padding: 20px; text-align: center;
        color: white; box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .metric-value { font-size: 2.2rem; font-weight: 700; margin: 0; }
    .metric-label { font-size: 0.85rem; opacity: 0.85; margin-top: 4px; }
    .section-title {
        font-size: 1.1rem; font-weight: 600; color: #1e3a5f;
        border-left: 4px solid #2d6a9f; padding-left: 10px; margin-bottom: 12px;
    }
    [data-testid="stSidebar"] { background-color: #0f2540; }
    [data-testid="stSidebar"] * { color: #cfe2f3 !important; }
</style>
""", unsafe_allow_html=True)

# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("kidney_clean.csv")
    return df

df = load_data()

# ── Sidebar filters ───────────────────────────────────────────────────────────
st.sidebar.image("https://img.icons8.com/fluency/96/kidney.png", width=60)
st.sidebar.title("🫘 CKD Dashboard")
st.sidebar.markdown("---")

age_range = st.sidebar.slider(
    "Age Range", int(df["Age"].min()), int(df["Age"].max()),
    (int(df["Age"].min()), int(df["Age"].max()))
)
ckd_filter = st.sidebar.selectbox("CKD Status", ["All", "CKD Positive", "CKD Negative"])
risk_filter = st.sidebar.multiselect(
    "Risk Tier", options=["Low", "Moderate", "High", "Critical"],
    default=["Low", "Moderate", "High", "Critical"]
)
med_options = sorted(df["Medication"].dropna().unique().tolist())
med_filter = st.sidebar.multiselect(
    "Medication", options=med_options,
    default=med_options
)

# ── Apply filters ─────────────────────────────────────────────────────────────
fdf = df[
    (df["Age"] >= age_range[0]) & (df["Age"] <= age_range[1]) &
    (df["Risk_Tier"].isin(risk_filter)) &
    (df["Medication"].fillna("None").isin(med_filter))
]
if ckd_filter == "CKD Positive":
    fdf = fdf[fdf["CKD_Status"] == 1]
elif ckd_filter == "CKD Negative":
    fdf = fdf[fdf["CKD_Status"] == 0]

st.sidebar.markdown("---")
st.sidebar.metric("Filtered Patients", f"{len(fdf):,}")

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("## 🫘 Chronic Kidney Disease — Clinical Analytics Dashboard")
st.markdown("Comprehensive analysis of patient biomarkers, risk stratification, and CKD progression.")
st.markdown("---")

# ── KPI Row ───────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)
ckd_rate = fdf["CKD_Status"].mean() * 100
avg_gfr  = fdf["GFR"].mean()
avg_creat = fdf["Creatinine"].mean()
avg_age  = fdf["Age"].mean()
high_risk = (fdf["Risk_Tier"].isin(["High", "Critical"])).sum()

for col, val, label, color in zip(
    [k1, k2, k3, k4, k5],
    [f"{len(fdf):,}", f"{ckd_rate:.1f}%", f"{avg_gfr:.1f}", f"{avg_creat:.2f}", f"{high_risk:,}"],
    ["Total Patients", "CKD Prevalence", "Avg GFR (mL/min)", "Avg Creatinine (mg/dL)", "High/Critical Risk"],
    ["#1e3a5f", "#c0392b", "#1a7a4a", "#7d3c98", "#d35400"]
):
    col.markdown(f"""
    <div class="metric-card" style="background:linear-gradient(135deg,{color},{color}cc)">
        <p class="metric-value">{val}</p>
        <p class="metric-label">{label}</p>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Row 1: CKD Distribution + Risk Tier ──────────────────────────────────────
c1, c2, c3 = st.columns([1, 1.5, 1.5])

with c1:
    st.markdown('<p class="section-title">CKD Status Distribution</p>', unsafe_allow_html=True)
    ckd_counts = fdf["CKD_Status"].map({0: "No CKD", 1: "CKD"}).value_counts().reset_index()
    ckd_counts.columns = ["Status", "Count"]
    fig = px.pie(ckd_counts, names="Status", values="Count",
                 color="Status", color_discrete_map={"No CKD": "#2d6a9f", "CKD": "#c0392b"},
                 hole=0.55)
    fig.update_traces(textinfo="percent+label", textfont_size=13)
    fig.update_layout(margin=dict(t=10, b=10), showlegend=False, height=280)
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.markdown('<p class="section-title">Risk Tier Breakdown</p>', unsafe_allow_html=True)
    rt = fdf["Risk_Tier"].value_counts().reindex(["Low","Moderate","High","Critical"]).fillna(0).reset_index()
    rt.columns = ["Tier", "Count"]
    colors = {"Low": "#27ae60", "Moderate": "#f39c12", "High": "#e67e22", "Critical": "#c0392b"}
    fig = px.bar(rt, x="Tier", y="Count", color="Tier",
                 color_discrete_map=colors, text="Count")
    fig.update_traces(textposition="outside", textfont_size=12)
    fig.update_layout(showlegend=False, margin=dict(t=10, b=10), height=280,
                      xaxis_title="", yaxis_title="Patients")
    st.plotly_chart(fig, use_container_width=True)

with c3:
    st.markdown('<p class="section-title">CKD Stage Distribution</p>', unsafe_allow_html=True)
    stage_order = ["Stage 1","Stage 2","Stage 3a","Stage 3b","Stage 4","Stage 5"]
    stage_df = fdf["CKD_Stage"].value_counts().reindex(stage_order).fillna(0).reset_index()
    stage_df.columns = ["Stage", "Count"]
    fig = px.bar(stage_df, x="Stage", y="Count", color="Stage",
                 color_discrete_sequence=px.colors.sequential.Blues_r, text="Count")
    fig.update_traces(textposition="outside", textfont_size=11)
    fig.update_layout(showlegend=False, margin=dict(t=10, b=10), height=280,
                      xaxis_title="", yaxis_title="Patients")
    st.plotly_chart(fig, use_container_width=True)

# ── Row 2: GFR Histogram + Creatinine Box ────────────────────────────────────
c4, c5 = st.columns(2)

with c4:
    st.markdown('<p class="section-title">GFR Distribution by CKD Status</p>', unsafe_allow_html=True)
    fig = px.histogram(fdf, x="GFR", color=fdf["CKD_Status"].map({0:"No CKD",1:"CKD"}),
                       nbins=40, barmode="overlay", opacity=0.75,
                       color_discrete_map={"No CKD":"#2d6a9f","CKD":"#c0392b"},
                       labels={"color":"Status"})
    fig.update_layout(margin=dict(t=10,b=10), height=300,
                      xaxis_title="GFR (mL/min/1.73m²)", yaxis_title="Count",
                      legend_title="")
    st.plotly_chart(fig, use_container_width=True)

with c5:
    st.markdown('<p class="section-title">Creatinine Levels by CKD Status</p>', unsafe_allow_html=True)
    box_df = fdf.copy()
    box_df["Status"] = box_df["CKD_Status"].map({0:"No CKD",1:"CKD"})
    fig = px.box(box_df, x="Status", y="Creatinine", color="Status",
                 color_discrete_map={"No CKD":"#2d6a9f","CKD":"#c0392b"},
                 points="outliers")
    fig.update_layout(showlegend=False, margin=dict(t=10,b=10), height=300,
                      xaxis_title="", yaxis_title="Creatinine (mg/dL)")
    st.plotly_chart(fig, use_container_width=True)

# ── Row 3: Scatter + Age Group ────────────────────────────────────────────────
c6, c7 = st.columns(2)

with c6:
    st.markdown('<p class="section-title">GFR vs Creatinine (Sample 600)</p>', unsafe_allow_html=True)
    sample = fdf.sample(min(600, len(fdf)), random_state=42)
    sample["Status"] = sample["CKD_Status"].map({0:"No CKD",1:"CKD"})
    fig = px.scatter(sample, x="GFR", y="Creatinine", color="Status",
                     color_discrete_map={"No CKD":"#2d6a9f","CKD":"#c0392b"},
                     opacity=0.65, size_max=6,
                     hover_data=["Age","BUN","Medication"])
    fig.update_layout(margin=dict(t=10,b=10), height=320,
                      xaxis_title="GFR (mL/min)", yaxis_title="Creatinine (mg/dL)",
                      legend_title="")
    st.plotly_chart(fig, use_container_width=True)

with c7:
    st.markdown('<p class="section-title">CKD Rate by Age Group</p>', unsafe_allow_html=True)
    age_grp = fdf.groupby("Age_Group")["CKD_Status"].agg(["mean","count"]).reset_index()
    age_grp.columns = ["Age_Group","CKD_Rate","Count"]
    age_grp["CKD_Rate"] *= 100
    age_order = ["<30","30-44","45-59","60-74","75+"]
    age_grp["Age_Group"] = pd.Categorical(age_grp["Age_Group"], categories=age_order, ordered=True)
    age_grp = age_grp.sort_values("Age_Group")
    fig = px.bar(age_grp, x="Age_Group", y="CKD_Rate", text=age_grp["CKD_Rate"].round(1).astype(str)+"%",
                 color="CKD_Rate", color_continuous_scale="Reds")
    fig.update_traces(textposition="outside")
    fig.update_layout(showlegend=False, margin=dict(t=10,b=10), height=320,
                      xaxis_title="Age Group", yaxis_title="CKD Rate (%)",
                      coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

# ── Row 4: Comorbidities + Medication ────────────────────────────────────────
c8, c9 = st.columns(2)

with c8:
    st.markdown('<p class="section-title">Comorbidity Impact on CKD</p>', unsafe_allow_html=True)
    fdf["Comorbidity"] = fdf.apply(
        lambda r: "Both" if r["Diabetes"]==1 and r["Hypertension"]==1
        else ("Diabetes Only" if r["Diabetes"]==1
        else ("Hypertension Only" if r["Hypertension"]==1 else "Neither")), axis=1
    )
    cmb = fdf.groupby("Comorbidity")["CKD_Status"].agg(["mean","count"]).reset_index()
    cmb.columns = ["Comorbidity","CKD_Rate","Count"]
    cmb["CKD_Rate"] *= 100
    fig = px.bar(cmb, x="Comorbidity", y="CKD_Rate", color="Comorbidity",
                 text=cmb["CKD_Rate"].round(1).astype(str)+"%",
                 color_discrete_sequence=["#27ae60","#f39c12","#e67e22","#c0392b"])
    fig.update_traces(textposition="outside")
    fig.update_layout(showlegend=False, margin=dict(t=10,b=10), height=300,
                      xaxis_title="", yaxis_title="CKD Rate (%)")
    st.plotly_chart(fig, use_container_width=True)

with c9:
    st.markdown('<p class="section-title">Medication Distribution by CKD Status</p>', unsafe_allow_html=True)
    med_df = fdf.groupby(["Medication","CKD_Status"]).size().reset_index(name="Count")
    med_df["Status"] = med_df["CKD_Status"].map({0:"No CKD",1:"CKD"})
    fig = px.bar(med_df, x="Medication", y="Count", color="Status", barmode="group",
                 color_discrete_map={"No CKD":"#2d6a9f","CKD":"#c0392b"}, text="Count")
    fig.update_traces(textposition="outside", textfont_size=10)
    fig.update_layout(margin=dict(t=10,b=10), height=300,
                      xaxis_title="", yaxis_title="Patients", legend_title="")
    st.plotly_chart(fig, use_container_width=True)

# ── Row 5: Correlation Heatmap + BUN vs GFR ──────────────────────────────────
c10, c11 = st.columns(2)

with c10:
    st.markdown('<p class="section-title">Biomarker Correlation Heatmap</p>', unsafe_allow_html=True)
    num_cols = ["Creatinine","BUN","GFR","Urine_Output","Protein_in_Urine",
                "Water_Intake","Age","CKD_Status"]
    corr = fdf[num_cols].corr().round(2)
    fig = px.imshow(corr, text_auto=True, color_continuous_scale="RdBu_r",
                    zmin=-1, zmax=1, aspect="auto")
    fig.update_layout(margin=dict(t=10,b=10), height=340)
    st.plotly_chart(fig, use_container_width=True)

with c11:
    st.markdown('<p class="section-title">BUN vs GFR by CKD Status</p>', unsafe_allow_html=True)
    sample2 = fdf.sample(min(600, len(fdf)), random_state=7)
    sample2["Status"] = sample2["CKD_Status"].map({0:"No CKD",1:"CKD"})
    fig = px.scatter(sample2, x="BUN", y="GFR", color="Status",
                     color_discrete_map={"No CKD":"#2d6a9f","CKD":"#c0392b"},
                     opacity=0.65,
                     hover_data=["Age","Creatinine"])
    fig.update_layout(margin=dict(t=10,b=10), height=340,
                      xaxis_title="BUN (mg/dL)", yaxis_title="GFR (mL/min)",
                      legend_title="")
    st.plotly_chart(fig, use_container_width=True)

# ── Row 6: Protein in Urine + Water Intake ───────────────────────────────────
c12, c13 = st.columns(2)

with c12:
    st.markdown('<p class="section-title">Protein in Urine Distribution</p>', unsafe_allow_html=True)
    prot_df = fdf.copy()
    prot_df["Status"] = prot_df["CKD_Status"].map({0:"No CKD",1:"CKD"})
    fig = px.histogram(prot_df, x="Protein_in_Urine", color="Status", nbins=40,
                       barmode="overlay", opacity=0.75,
                       color_discrete_map={"No CKD":"#2d6a9f","CKD":"#c0392b"})
    fig.update_layout(margin=dict(t=10,b=10), height=280,
                      xaxis_title="Protein in Urine (mg/dL)", yaxis_title="Count",
                      legend_title="")
    st.plotly_chart(fig, use_container_width=True)

with c13:
    st.markdown('<p class="section-title">Water Intake vs Urine Output</p>', unsafe_allow_html=True)
    sample3 = fdf.sample(min(500, len(fdf)), random_state=99)
    sample3["Status"] = sample3["CKD_Status"].map({0:"No CKD",1:"CKD"})
    fig = px.scatter(sample3, x="Water_Intake", y="Urine_Output", color="Status",
                     color_discrete_map={"No CKD":"#2d6a9f","CKD":"#c0392b"},
                     opacity=0.6)
    fig.update_layout(margin=dict(t=10,b=10), height=280,
                      xaxis_title="Water Intake (L)", yaxis_title="Urine Output (mL)",
                      legend_title="")
    st.plotly_chart(fig, use_container_width=True)

# ── Data Table ────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown('<p class="section-title">📋 Patient Data Explorer</p>', unsafe_allow_html=True)
display_cols = ["Age","Age_Group","Creatinine","BUN","GFR","Urine_Output",
                "Protein_in_Urine","Diabetes","Hypertension","Medication",
                "CKD_Stage","Risk_Tier","CKD_Status"]
st.dataframe(
    fdf[display_cols].reset_index(drop=True),
    use_container_width=True, height=300
)

col_dl1, col_dl2 = st.columns([1, 5])
with col_dl1:
    st.download_button(
        "⬇️ Download Filtered CSV",
        data=fdf.to_csv(index=False),
        file_name="kidney_filtered.csv",
        mime="text/csv"
    )

st.markdown("---")
st.caption("🫘 Kidney Disease Clinical Dashboard  |  Data: kidney_clean.csv  |  Built with Streamlit & Plotly")
