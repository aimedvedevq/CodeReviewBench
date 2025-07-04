import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="ruCodeReviewer • Results", page_icon="📈", layout="wide")

st.title("📈 Benchmark Observation")

# -----------------------------------------------------------------------------
# Safety check
# -----------------------------------------------------------------------------

if "last_benchmark_results" not in st.session_state:
    st.warning("No benchmark results found. Run a benchmark first from the main page.")
    st.stop()

# -----------------------------------------------------------------------------
# Pull data & metadata
# -----------------------------------------------------------------------------

results = st.session_state["last_benchmark_results"]
meta_df = pd.DataFrame(
    {
        "comment_language": st.session_state.get("comment_language", []),
        "language": st.session_state.get("programming_language", []),
        "topic": st.session_state.get("topic", []),
    }
)

# -----------------------------------------------------------------------------
# Filtering controls
# -----------------------------------------------------------------------------

st.sidebar.header("Filters")

def multiselect_with_all(label, options):
    all_key = "(All)"
    options_with_all = [all_key] + sorted([o for o in options if pd.notna(o)])
    default = options_with_all[0]
    selection = st.sidebar.multiselect(label, options_with_all, default=[default])
    return options if all_key in selection or not selection else selection

comment_langs = multiselect_with_all("Comment language", meta_df["comment_language"].unique())
prog_langs = multiselect_with_all("Programming language", meta_df["language"].unique())
topics = multiselect_with_all("Topic", meta_df["topic"].unique())

mask = (
    meta_df["comment_language"].isin(comment_langs)
    & meta_df["language"].isin(prog_langs)
    & meta_df["topic"].isin(topics)
)

# If nothing selected due to filters, notify user
if mask.sum() == 0:
    st.warning("No samples match the selected filters.")
    st.stop()

# -----------------------------------------------------------------------------
# Build summary (metric row, passes as columns) & full sample DataFrame
# -----------------------------------------------------------------------------

summary_dict: dict[str, dict[str, str]] = {}
sample_frames: list[pd.DataFrame] = []
all_passes: set[int] = set()

# Hold dedicated data for multi_metric breakdown
multi_metric_breakdown: tuple[pd.DataFrame, pd.Series, pd.Series] | None = None

for metric_name, metric_tuple in results.items():
    if metric_tuple is None:
        continue

    samples_df, mean_series, std_series = metric_tuple  # type: ignore

    # If this is the composite multi_metric, keep for separate display and
    # skip adding to the generic summary table.
    if metric_name == "multi_metric":
        filtered_samples = samples_df[mask]
        multi_metric_breakdown = (
            filtered_samples,
            filtered_samples.mean(axis=0),
            filtered_samples.std(axis=0) / (len(filtered_samples) ** 0.5),
        )
    else:
        # ---------------- summary ----------------
        for col in mean_series.index:
            # extract pass id from *_pass_{k}
            if "_pass_" in col:
                _, _, pass_k = col.rpartition("_pass_")
                p_int = int(pass_k)
            else:
                # fallback: no pass encoded
                p_int = 1
            all_passes.add(p_int)

            mean_val = mean_series[col]
            std_val = std_series[col] if col in std_series else float("nan")

            summary_dict.setdefault(metric_name, {})[f"@{p_int}"] = f"{mean_val:.4f} ± {std_val:.4f}"

    # ---------------- full samples for plots ----------------
    # Rename each column to pattern "Metric@pass" for easy grouping
    renamed_cols = {}
    for col in samples_df.columns:
        if "_pass_" in col:
            metric_base, _, pass_k = col.rpartition("_pass_")
            renamed_cols[col] = f"{metric_base}@{pass_k}"
            all_passes.add(int(pass_k))
        else:
            # For metrics without explicit pass (e.g., multi_metric readability),
            # treat them as pass@1 and tag accordingly for consistency.
            renamed_cols[col] = f"{metric_name}_{col}@1"
            all_passes.add(1)
    samples_df = samples_df.rename(columns=renamed_cols)

    # Apply mask for filtering
    filtered_samples = samples_df[mask]

    # Recompute summary on filtered data
    if metric_name != "multi_metric":
        if len(filtered_samples) == 0:
            continue
        for col in filtered_samples.columns:
            if "@" in col:
                base, _, pass_k = col.partition("@")
                pass_k = pass_k or "1"
                all_passes.add(int(pass_k))
                mean_val = filtered_samples[col].mean()
                std_val = filtered_samples[col].std() / (len(filtered_samples) ** 0.5)
                summary_dict.setdefault(metric_name, {})[f"@{pass_k}"] = f"{mean_val:.4f} ± {std_val:.4f}"

    sample_frames.append(filtered_samples)

# Summary table in wide format
summary_df = pd.DataFrame.from_dict(summary_dict, orient="index")
summary_df.index.name = "Metric"
summary_df = summary_df.sort_index()

# Ensure columns sorted by pass number (1,5,10,…)
sorted_pass_cols = [f"@{p}" for p in sorted(all_passes)]
summary_df = summary_df.reindex(columns=sorted_pass_cols)

st.subheader("Metric means ± std (rows = metrics, columns = passes)")
st.dataframe(summary_df, use_container_width=True)

# -----------------------------------------------------------------------------
# Multi-Metric detailed table (if available)
# -----------------------------------------------------------------------------

if multi_metric_breakdown is not None:
    _, mm_mean, mm_std = multi_metric_breakdown  # type: ignore

    mm_table = pd.DataFrame({
        "Sub-metric": mm_mean.index,
        "Mean ± Std": [f"{mm_mean[c]:.4f} ± {mm_std.get(c, float('nan')):.4f}" for c in mm_mean.index],
    })

    st.divider()
    st.subheader("🧩 Multi-Metric breakdown (pass @1)")
    st.dataframe(mm_table, use_container_width=True)

# -----------------------------------------------------------------------------
# Scatter & box plots using full per-sample results
# -----------------------------------------------------------------------------

combined_samples = pd.concat(sample_frames, axis=1) if sample_frames else pd.DataFrame()

if combined_samples.empty:
    st.stop()

st.divider()

st.header("📊 Explore relationships between metrics")

# Select pass first to keep the list manageable
selected_pass = st.selectbox("Pass (k)", options=sorted(all_passes), format_func=lambda x: f"@{x}")

pass_suffix = f"@{selected_pass}"
cols_for_pass = [c for c in combined_samples.columns if c.endswith(pass_suffix)]

if len(cols_for_pass) < 2:
    st.info("Need at least two metrics for scatter plot at this pass.")
else:
    col_x = st.selectbox("X-axis", options=cols_for_pass, key="scatter_x")
    remaining = [c for c in cols_for_pass if c != col_x]
    col_y = st.selectbox("Y-axis", options=remaining, key="scatter_y")

    scatter_chart = (
        alt.Chart(combined_samples.reset_index(drop=True)).mark_circle(size=60).encode(
            x=alt.X(col_x, title=col_x),
            y=alt.Y(col_y, title=col_y),
            tooltip=[col_x, col_y],
        )
        .properties(height=400)
        .interactive()
    )

    st.altair_chart(scatter_chart, use_container_width=True)

st.divider()

st.header("📦 Boxplots")

selected_box_pass = st.selectbox("Pass (k) for boxplot", options=sorted(all_passes), key="box_pass")
box_suffix = f"@{selected_box_pass}"
box_cols = [c for c in combined_samples.columns if c.endswith(box_suffix)]

selected_box_cols = st.multiselect(
    "Select metrics to display", options=box_cols, default=box_cols[: min(5, len(box_cols))]
)

if selected_box_cols:
    melted = combined_samples[selected_box_cols].melt(var_name="Metric", value_name="Score")
    box_chart = (
        alt.Chart(melted).mark_boxplot(extent="min-max").encode(
            x="Metric:N", y="Score:Q", color="Metric:N"
        ).properties(height=400)
    )
    st.altair_chart(box_chart, use_container_width=True)

# -----------------------------------------------------------------------------
# Download filtered per-example results
# -----------------------------------------------------------------------------

st.divider()

export_df = pd.concat([meta_df[mask].reset_index(drop=True), combined_samples.reset_index(drop=True)], axis=1)

jsonl_bytes = export_df.to_json(orient="records", lines=True).encode("utf-8")

st.download_button(
    label="📥 Download results (JSONL)",
    data=jsonl_bytes,
    file_name="benchmark_results.jsonl",
    mime="application/json",
) 