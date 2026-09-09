import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
VOCAB=["A","C","G","U"]; EMBED_DIM=8; embedding_table={b:np.random.default_rng(42).normal(size=EMBED_DIM) for b in VOCAB}
def encode_sequence(s):
 if not 5<=len(s)<=50: raise ValueError("Sequence length must be between 5 and 50.")
 bad=sorted(set(s)-set(VOCAB))
 if bad: raise ValueError(f"Invalid nucleotide(s): {bad}. Allowed: A, C, G, U.")
 return np.stack([embedding_table[b] for b in s])
def softmax(x):
 x=x-np.max(x,axis=-1,keepdims=True); e=np.exp(x); return e/e.sum(axis=-1,keepdims=True)
def self_attention(X,d_k=EMBED_DIM):
 rng=np.random.default_rng(42); _,d=X.shape; Q=X@(rng.normal(size=(d,d_k))*.1); K=X@(rng.normal(size=(d,d_k))*.1); V=X@(rng.normal(size=(d,d_k))*.1); W=softmax(Q@K.T/np.sqrt(d_k)); return W,W@V
def plot_attention(w,s,p):
 fig,ax=plt.subplots(figsize=(8,6)); im=ax.imshow(w); q=range(len(s)); ax.set_xticks(list(q)); ax.set_yticks(list(q)); ax.set_xticklabels(list(s)); ax.set_yticklabels(list(s)); ax.set_xlabel("Attending TO position"); ax.set_ylabel("Attending FROM position"); ax.set_title("mRNA Sequence Self-Attention Weights"); fig.colorbar(im,label="Attention weight"); fig.tight_layout(); fig.savefig(p,dpi=150); plt.close(fig)
if __name__=="__main__":
 r=Path(__file__).resolve().parents[1]; s="ACGUACGUACGGCUA"; w,_=self_attention(encode_sequence(s)); assert np.allclose(w.sum(axis=1),1); plot_attention(w,s,r/"outputs/figures/attention_heatmap.png")
