from pathlib import Path
import pandas as pd,pytest
from src.data_pipeline import load_and_validate,clean_data,MissingColumnError
ROOT=Path(__file__).resolve().parents[1]
def test_columns(): assert len(load_and_validate(ROOT/"data/patient_records.csv"))==500
def test_missing_column():
 df=pd.read_csv(ROOT/"data/patient_records.csv").drop(columns=["Age"]); p=ROOT/"data/_test.csv"; df.to_csv(p,index=False)
 try:
  with pytest.raises(MissingColumnError,match="Age"): load_and_validate(p)
 finally: p.unlink(missing_ok=True)
def test_clean(): assert clean_data(load_and_validate(ROOT/"data/patient_records.csv")).isna().sum().sum()==0
