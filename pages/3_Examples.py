import streamlit as st
import pandas as pd

st.set_page_config(page_title="ruCodeReviewer • Examples", page_icon="🔍", layout="wide")

st.title("🔍 Example Explorer")

# -----------------------------------------------------------------------------
# Availability check
# -----------------------------------------------------------------------------

required_keys = [
    "last_benchmark_results",
    "last_predictions",
    "prompts",
    "references",
]

if any(k not in st.session_state for k in required_keys):
    st.info("Run a benchmark first in the Configuration page to populate examples.")
    st.stop()

results = st.session_state["last_benchmark_results"]
all_predictions = st.session_state["last_predictions"]
all_prompts = st.session_state["prompts"]
all_references = st.session_state["references"]

num_samples = len(all_prompts)

st.sidebar.markdown("### Example selector")
example_idx = st.sidebar.slider("Example index", 0, num_samples - 1, 0)

st.subheader(f"Prompt #{example_idx}")

st.code(all_prompts[example_idx], language="text")

st.subheader("Reference output")

st.markdown(all_references[example_idx])

# Predictions may be list of hypotheses
preds_for_example = (
    all_predictions[example_idx] if all_predictions and example_idx < len(all_predictions) else []
)

st.subheader("Model predictions")

if preds_for_example:
    for i, pred in enumerate(preds_for_example, 1):
        st.markdown(f"**Hypothesis {i}:**")
        st.markdown(pred)
else:
    st.write("No predictions captured for this example.")

# ------------------ per-example metric scores ------------------

# Capture needed metrics only
llm_exact_match_scores = {}
multimetric_breakdown = None

for metric_name, metric_tuple in results.items():
    if metric_tuple is None:
        continue

    samples_df, _, _ = metric_tuple  # type: ignore

    if metric_name == "multi_metric":
        multimetric_breakdown = samples_df.iloc[example_idx]
    elif metric_name == "llm_exact_match":
        for col in samples_df.columns:
            if "_pass_" in col:
                _, _, k = col.rpartition("_pass_")
                llm_exact_match_scores[f"@{k}"] = samples_df.iloc[example_idx][col]

st.divider()

# Display LLM Exact Match
if llm_exact_match_scores:
    st.subheader("LLM-based Exact Match")
    cols = st.columns(len(llm_exact_match_scores))
    for (label, val), col in zip(sorted(llm_exact_match_scores.items()), cols):
        try:
            col.metric(f"pass {label}", f"{float(val):.3f}")
        except Exception:
            col.metric(f"pass {label}", str(val))

# Display Multi-Metric breakdown
if multimetric_breakdown is not None:
    st.divider()
    st.subheader("Multi-Metric breakdown")
    cols = st.columns(3)
    for i, (sub_metric, value) in enumerate(multimetric_breakdown.items()):
        col = cols[i % 3]
        try:
            col.metric(sub_metric, f"{float(value):.3f}")
        except Exception:
            col.metric(sub_metric, str(value)) 