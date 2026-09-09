from pathlib import Path
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
def create_dashboard():
 fig,axes=plt.subplots(1,3,figsize=(16,5))
 for ax,title in zip(axes,["ML ROC Curve","Attention Heatmap","Retrieval Latency"]): ax.set_title(title); ax.text(.5,.5,"Run the corresponding module first",ha="center",va="center"); ax.set_xticks([]); ax.set_yticks([])
 fig.tight_layout(); fig.savefig(ROOT/"outputs/figures/dashboard.png",dpi=150); plt.close(fig)
if __name__=="__main__": create_dashboard()
