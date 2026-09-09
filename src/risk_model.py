from pathlib import Path
import json,joblib,numpy as np,pandas as pd,matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report,confusion_matrix,f1_score,roc_auc_score,roc_curve
from data_pipeline import load_and_validate,clean_data,prepare_features,TARGET_COL
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/"outputs"; FIG=OUT/"figures"; FIG.mkdir(parents=True,exist_ok=True)
def run():
 raw=load_and_validate(ROOT/"data/patient_records.csv"); print("Missing values before cleaning:\n",raw.isna().sum()); clean=clean_data(raw); clean.to_csv(ROOT/"data/patient_records_clean.csv",index=False); tr,te=train_test_split(clean,test_size=.2,random_state=42,stratify=clean[TARGET_COL]); Xtr,Xte,sc,enc=prepare_features(tr,te); ytr,yte=tr[TARGET_COL],te[TARGET_COL]; models={"logistic_regression":LogisticRegression(max_iter=1000,random_state=42),"random_forest":RandomForestClassifier(n_estimators=200,random_state=42)}; res={}
 for n,m in models.items():
  m.fit(Xtr,ytr); pred=m.predict(Xte); prob=m.predict_proba(Xte)[:,1]; cm=confusion_matrix(yte,pred); res[n]={"model":m,"f1":float(f1_score(yte,pred)),"roc_auc":float(roc_auc_score(yte,prob)),"report":classification_report(yte,pred,output_dict=True),"cm":cm,"prob":prob}; (OUT/f"{n}_classification_report.json").write_text(json.dumps(res[n]["report"],indent=2)); np.save(OUT/f"{n}_confusion_matrix.npy",cm); fig,ax=plt.subplots(figsize=(5,4)); ax.imshow(cm); ax.set_title(n.replace("_"," ").title()+" — Confusion Matrix"); ax.set_xlabel("Predicted"); ax.set_ylabel("Actual"); [ax.text(j,i,str(v),ha="center",va="center") for (i,j),v in np.ndenumerate(cm)]; fig.tight_layout(); fig.savefig(FIG/f"{n}_confusion_matrix.png",dpi=150); plt.close(fig)
 best=max(res,key=lambda x:res[x]["f1"]); joblib.dump({"model":res[best]["model"],"scaler":sc,"encoder":enc,"feature_columns":Xtr.columns.tolist(),"model_name":best},OUT/"risk_model.joblib"); (OUT/"model_comparison.json").write_text(json.dumps({k:{"f1":v["f1"],"roc_auc":v["roc_auc"]} for k,v in res.items()},indent=2)); fig,ax=plt.subplots(figsize=(6,5)); [ax.plot(*roc_curve(yte,v["prob"])[:2],label=f"{n} (AUC={v['roc_auc']:.3f})") for n,v in res.items()]; ax.plot([0,1],[0,1],"--",label="Chance"); ax.set_title("ML ROC Curve"); ax.set_xlabel("False Positive Rate"); ax.set_ylabel("True Positive Rate"); ax.legend(); fig.tight_layout(); fig.savefig(FIG/"ml_roc_curve.png",dpi=150); plt.close(fig); print("Selected model by test-set F1:",best)
if __name__=="__main__": run()
