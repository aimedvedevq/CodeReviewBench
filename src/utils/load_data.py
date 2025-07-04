import pandas as pd
import os

def load_data(max_samples: int = None):
    # Get the project root directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(current_dir, '..', '..')
    data_path = os.path.join(project_root, 'data', 'ru_codereview_new_data.jsonl')
    
    df = pd.read_json(data_path, lines=True)
    if max_samples is not None:
        df = df.head(max_samples)
    outputs = df["outputs"].tolist()
    diffs = df["inputs"].apply(lambda x: x["diff_block"]).tolist()
    prompts = df.apply(
        lambda row: row["instruction"].format(diff_block=row["inputs"].get("diff_block", "")),
        axis=1,
    ).tolist()

    # Additional taxonomy columns if present; fallback to None-list of same length
    comment_language = (
        df.get("comment_language") if "comment_language" in df.columns else pd.Series([None] * len(df))
    ).tolist()
    programming_language = (
        df.get("language") if "language" in df.columns else pd.Series([None] * len(df))
    ).tolist()
    topic = (
        df.get("topic") if "topic" in df.columns else pd.Series([None] * len(df))
    ).tolist()

    return {
        "prompts": prompts,
        "diffs": diffs,
        "outputs": outputs,
        "comment_language": comment_language,
        "language": programming_language,
        "topic": topic,
    }