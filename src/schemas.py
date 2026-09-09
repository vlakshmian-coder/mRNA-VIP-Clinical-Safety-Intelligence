from pydantic import BaseModel,Field
from typing import List
class ClinicalSafetyReport(BaseModel):
 Eligible_For_Vaccine: bool
 Recommended_Dose_mg: float
 Reasoning_Steps: List[str]
 FDA_Safety_Warnings_Cited: List[str]
 Disclaimer: str=Field(min_length=1)
