import pandas as pd
import numpy as np
import json

df = pd.read_csv("kidney_dataset.csv")

# --- Derived features ---
df["CKD_Stage"] = pd.cut(
    df["GFR"],
    bins=[0, 15, 30, 45, 60, 90, float("inf")],
    labels=["Stage 5", "Stage 4", "Stage 3b", "Stage 3a", "Stage 2", "Stage 1"],
    right=False
).astype(str)

df["Risk_Score"] = (
    (df["Creatinine"] > 2).astype(int) * 2 +
    (df["BUN"] > 50).astype(int) * 2 +
    (df["GFR"] < 60).astype(int) * 2 +
    df["Diabetes"].astype(int) +
    df["Hypertension"].astype(int) +
    (df["Protein_in_Urine"] > 500).astype(int)
)

df["Risk_Tier"] = pd.cut(
    df["Risk_Score"],
    bins=[-1, 1, 3, 5, 10],
    labels=["Low", "Moderate", "High", "Critical"]
).astype(str)

df["Age_Group"] = pd.cut(
    df["Age"],
    bins=[0, 30, 45, 60, 75, 100],
    labels=["<30", "30-44", "45-59", "60-74", "75+"]
).astype(str)

df["Comorbidity_Count"] = df["Diabetes"] + df["Hypertension"]

# --- Save cleaned CSV ---
df.to_csv("kidney_clean.csv", index=False)
print(f"Saved kidney_clean.csv  ({len(df)} rows, {len(df.columns)} columns)")

# --- Export summary stats for dashboard ---
summary = {
    "total_patients": len(df),
    "ckd_positive": int(df["CKD_Status"].sum()),
    "ckd_negative": int((df["CKD_Status"] == 0).sum()),
    "avg_age": round(df["Age"].mean(), 1),
    "avg_gfr": round(df["GFR"].mean(), 1),
    "avg_creatinine": round(df["Creatinine"].mean(), 2),

    "ckd_by_stage": df.groupby("CKD_Stage")["CKD_Status"].agg(["count", "sum"])
        .rename(columns={"count": "total", "sum": "ckd"}).reset_index()
        .to_dict(orient="records"),

    "risk_tier_counts": df["Risk_Tier"].value_counts().to_dict(),

    "age_group_ckd": df.groupby("Age_Group")["CKD_Status"]
        .agg(total="count", ckd="sum").reset_index().to_dict(orient="records"),

    "medication_ckd": df.groupby("Medication")["CKD_Status"]
        .agg(total="count", ckd="sum").reset_index().to_dict(orient="records"),

    "gfr_bins": np.histogram(df["GFR"], bins=20)[0].tolist(),
    "gfr_edges": np.histogram(df["GFR"], bins=20)[1].round(1).tolist(),

    "creatinine_ckd0": df[df["CKD_Status"] == 0]["Creatinine"].round(2).tolist(),
    "creatinine_ckd1": df[df["CKD_Status"] == 1]["Creatinine"].round(2).tolist(),

    "diabetes_hyp": {
        "neither": int(((df["Diabetes"] == 0) & (df["Hypertension"] == 0)).sum()),
        "diabetes_only": int(((df["Diabetes"] == 1) & (df["Hypertension"] == 0)).sum()),
        "hyp_only": int(((df["Diabetes"] == 0) & (df["Hypertension"] == 1)).sum()),
        "both": int(((df["Diabetes"] == 1) & (df["Hypertension"] == 1)).sum()),
    },

    "scatter_gfr_creatinine": df[["GFR", "Creatinine", "CKD_Status"]].sample(
        min(500, len(df)), random_state=42
    ).to_dict(orient="records"),
}

with open("dashboard_data.json", "w") as f:
    json.dump(summary, f)
print("Saved dashboard_data.json")
