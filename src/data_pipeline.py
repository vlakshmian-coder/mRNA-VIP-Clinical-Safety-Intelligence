import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder

REQUIRED_COLUMNS = [
    "Patient_ID",
    "Age",
    "Biomarker_Level",
    "Pre_Existing_Conditions",
    "Vaccine_Dose_mcg",
    "Prior_Reaction_History",
    "Reaction_Score",
]

NUMERIC_COLS = ["Age", "Biomarker_Level", "Vaccine_Dose_mcg"]
CATEGORICAL_COL = "Prior_Reaction_History"
TARGET_COL = "Reaction_Score"


class MissingColumnError(ValueError):
    pass


def load_and_validate(path):
    df = pd.read_csv(path)
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise MissingColumnError(
            "Missing required column(s): " + ", ".join(missing)
        )
    return df


def clean_data(df, reference_df=None):
    out = df.copy()
    reference = out if reference_df is None else reference_df

    for c in NUMERIC_COLS:
        out[c] = out[c].fillna(reference[c].median())

    out[CATEGORICAL_COL] = out[CATEGORICAL_COL].fillna(
        reference[CATEGORICAL_COL].mode()[0]
    )

    return out


def prepare_features(train_df, test_df):
    scaler = StandardScaler()
    enc = LabelEncoder()

    a = train_df[NUMERIC_COLS].copy().astype(float)
    b = test_df[NUMERIC_COLS].copy().astype(float)
    a.loc[:, NUMERIC_COLS] = scaler.fit_transform(a)
    b.loc[:, NUMERIC_COLS] = scaler.transform(b)

    enc.fit(train_df[CATEGORICAL_COL])

    a[CATEGORICAL_COL] = enc.transform(train_df[CATEGORICAL_COL])
    b[CATEGORICAL_COL] = enc.transform(test_df[CATEGORICAL_COL])

    a["Pre_Existing_Conditions"] = train_df["Pre_Existing_Conditions"].to_numpy()
    b["Pre_Existing_Conditions"] = test_df["Pre_Existing_Conditions"].to_numpy()

    cols = NUMERIC_COLS + [CATEGORICAL_COL, "Pre_Existing_Conditions"]

    return a[cols], b[cols], scaler, enc