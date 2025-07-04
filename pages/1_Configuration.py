import streamlit as st
from typing import List

from configs.model_config import ModelConfig, ModelType
from configs.generation_config import GenerationConfig
from src.models import ModelFactory
from src.strategies import StrategyFactory

st.set_page_config(page_title="CodeReviewBench • Configuration", page_icon="⚙️", layout="wide")

# --------------------------------------------------
# Custom CSS for compact, reinvented design
# --------------------------------------------------
st.markdown(
    """
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border-radius: 12px;
        margin-bottom: 2rem;
        border: 1px solid #e2e8f0;
    }
    
    .main-title {
        font-family: 'Inter', sans-serif;
        font-size: 2rem;
        font-weight: 600;
        color: #1a202c;
        margin-bottom: 0.5rem;
    }
    
    .main-subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 0.95rem;
        color: #64748b;
        margin: 0;
    }
    
    .config-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 2rem;
        margin-bottom: 2rem;
    }
    
    .config-panel {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 1.5rem;
        height: fit-content;
    }
    
    .panel-title {
        font-family: 'Inter', sans-serif;
        font-size: 1.1rem;
        font-weight: 600;
        color: #2d3748;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e2e8f0;
    }
    
    .compact-row {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1rem;
    }
    
    .compact-label {
        font-family: 'Inter', sans-serif;
        font-size: 0.85rem;
        font-weight: 500;
        color: #4a5568;
        min-width: 80px;
        flex-shrink: 0;
    }
    
    .compact-control {
        flex: 1;
    }
    
    .metrics-panel {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 2rem;
    }
    
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
        gap: 0.75rem;
        margin-top: 1rem;
    }
    
    .metric-checkbox {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem;
        border: 1px solid #e2e8f0;
        border-radius: 6px;
        transition: all 0.2s ease;
        cursor: pointer;
        font-family: 'Inter', sans-serif;
        font-size: 0.85rem;
        color: #4a5568;
    }
    
    .metric-checkbox:hover {
        border-color: #cbd5e0;
        background: #f7fafc;
    }
    
    .metric-checkbox.selected {
        border-color: #4a5568;
        background: #f7fafc;
    }
    
    .generation-panel {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 2rem;
    }
    
    .generation-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1.5rem;
        margin-top: 1rem;
    }
    
    .param-group {
        text-align: center;
    }
    
    .param-label {
        font-family: 'Inter', sans-serif;
        font-size: 0.85rem;
        font-weight: 500;
        color: #4a5568;
        margin-bottom: 0.5rem;
        display: block;
    }
    
    .param-value {
        font-family: 'Inter', sans-serif;
        font-size: 1.5rem;
        font-weight: 600;
        color: #2d3748;
        margin-bottom: 0.5rem;
    }
    
    .param-slider {
        width: 100%;
    }
    
    .run-panel {
        background: linear-gradient(135deg, #4a5568 0%, #2d3748 100%);
        color: white;
        border-radius: 8px;
        padding: 2rem;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .run-title {
        font-family: 'Inter', sans-serif;
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .run-subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 0.9rem;
        opacity: 0.8;
        margin-bottom: 1.5rem;
    }
    
    .stButton > button {
        background: white !important;
        color: #2d3748 !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 0.75rem 2rem !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.2s ease !important;
    }
    
    .stButton > button:hover {
        background: #f7fafc !important;
        transform: translateY(-1px) !important;
    }
    
    .alert {
        padding: 1rem;
        border-radius: 6px;
        margin: 1rem 0;
        font-family: 'Inter', sans-serif;
        font-size: 0.9rem;
    }
    
    .alert-info {
        background: #ebf8ff;
        border: 1px solid #bee3f8;
        color: #2c5282;
    }
    
    .alert-warning {
        background: #fffbeb;
        border: 1px solid #fed7aa;
        color: #c05621;
    }
    
    .alert-success {
        background: #f0fff4;
        border: 1px solid #9ae6b4;
        color: #22543d;
    }
    
    /* Streamlit component overrides */
    .stSelectbox > div > div {
        border-radius: 6px !important;
        font-size: 0.9rem !important;
    }
    
    .stTextInput > div > div {
        border-radius: 6px !important;
        font-size: 0.9rem !important;
    }
    
    .stNumberInput > div > div {
        border-radius: 6px !important;
        font-size: 0.9rem !important;
    }
    
    .stSlider > div > div > div {
        height: 4px !important;
    }
    
    .stSlider > div > div > div > div {
        height: 16px !important;
        width: 16px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------
# Header
# --------------------------------------------------
st.markdown(
    """
    <div class="main-header">
        <div class="main-title">Benchmark Configuration</div>
        <div class="main-subtitle">Configure models, parameters, and metrics for evaluation</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------
# Helper functions
# --------------------------------------------------
def build_model_config(prefix: str, title: str) -> ModelConfig:
    """Build model configuration in a compact format without extra HTML wrappers."""
    
    # Model type selection
    model_type_str = st.selectbox(
        "Type", 
        options=[m.value for m in ModelType], 
        key=f"{prefix}_model_type",
        label_visibility="collapsed"
    )
    
    # Model path
    default_path = "/path/to/model" if model_type_str == "vllm" else "google/gemini-2.5-flash"
    model_path = st.text_input(
        "Model", 
        value=default_path,
        key=f"{prefix}_model_path",
        label_visibility="collapsed"
    )
    
    # Conditional parameters
    gpu_memory_utilization = None
    api_key = None
    base_url = None
    
    if model_type_str == "vllm":
        st.markdown('<div class="compact-row"><span class="compact-label">GPU Memory</span><div class="compact-control">', unsafe_allow_html=True)
        gpu_memory_utilization = st.slider(
            "GPU memory utilization",
            min_value=0.1,
            max_value=1.0,
            value=0.95,
            step=0.05,
            key=f"{prefix}_gpu_util",
            label_visibility="collapsed"
        )
        st.markdown('</div></div>', unsafe_allow_html=True)
    else:
        api_key = st.text_input(
            "API Key",
            type="password",
            key=f"{prefix}_api_key",
            label_visibility="collapsed"
        )
        base_url = st.text_input(
            "Base URL",
            value="https://openrouter.ai/api/v1",
            key=f"{prefix}_base_url",
            label_visibility="collapsed"
        )
    
    return ModelConfig(
        model_type=ModelType(model_type_str),
        api_key=api_key,
        base_url=base_url,
        gpu_memory_utilization=gpu_memory_utilization,
        model_path=model_path,
    )

# --------------------------------------------------
# Model Configuration – side-by-side columns (avoids crooked layout)
# --------------------------------------------------
col_bench, col_judge = st.columns(2, gap="large")

with col_bench:
    st.markdown("<div class='panel-title'>Benchmark Model</div>", unsafe_allow_html=True)
    benchmark_model_config = build_model_config("benchmark", "Benchmark Model")

with col_judge:
    st.markdown("<div class='panel-title'>Judge Model</div>", unsafe_allow_html=True)
    judge_model_config = build_model_config("judge", "Judge Model")

# --------------------------------------------------
# Generation Parameters
# --------------------------------------------------
st.markdown(
    """
    <div class="generation-panel">
        <div class="panel-title">Generation Parameters</div>
        <div class="generation-grid">
    """,
    unsafe_allow_html=True,
)

# Max tokens
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<div class="param-group">', unsafe_allow_html=True)
    max_tokens = st.number_input(
        "Max Tokens",
        min_value=16,
        max_value=4096,
        value=4096,
        step=64,
        label_visibility="collapsed"
    )
    st.markdown(f'<div class="param-label">Max Tokens</div><div class="param-value">{max_tokens}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="param-group">', unsafe_allow_html=True)
    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=2.0,
        value=1.0,
        step=0.1,
        label_visibility="collapsed"
    )
    st.markdown(f'<div class="param-label">Temperature</div><div class="param-value">{temperature}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="param-group">', unsafe_allow_html=True)
    top_p = st.slider(
        "Top-p",
        min_value=0.0,
        max_value=1.0,
        value=0.95,
        step=0.05,
        label_visibility="collapsed"
    )
    st.markdown(f'<div class="param-label">Top-p</div><div class="param-value">{top_p}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div></div>', unsafe_allow_html=True)

generation_config = GenerationConfig(
    max_new_tokens=max_tokens,
    temperature=temperature,
    top_p=top_p
)

# --------------------------------------------------
# Metrics Selection
# --------------------------------------------------
st.markdown(
    """
    <div class="metrics-panel">
        <div class="panel-title">Evaluation Metrics</div>
        <div class="metrics-grid">
    """,
    unsafe_allow_html=True,
)

metrics_options = [
    "exact_match",
    "bleu", 
    "chrf",
    "llm_exact_match",
    "multi_metric"
]

selected_metrics = st.multiselect(
    "Select metrics",
    options=metrics_options,
    default=["exact_match"],
    label_visibility="collapsed"
)

st.markdown('</div></div>', unsafe_allow_html=True)

# --------------------------------------------------
# Run Section
# --------------------------------------------------
st.markdown(
    """
    <div class="run-panel">
        <div class="run-title">Ready to Run</div>
        <div class="run-subtitle">Start benchmark evaluation with your configuration</div>
    </div>
    """,
    unsafe_allow_html=True,
)

run_button = st.button("Start Benchmark", type="primary")

# --------------------------------------------------
# Benchmark Execution
# --------------------------------------------------
if run_button:
    if not selected_metrics:
        st.markdown(
            """
            <div class="alert alert-warning">
                <strong>No metrics selected</strong><br>
                Please select at least one evaluation metric.
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.stop()

    model_factory = ModelFactory()
    strategy_factory = StrategyFactory()

    with st.status("Loading models", expanded=False):
        benchmark_model = model_factory.get_model(benchmark_model_config)
        judge_model = model_factory.get_model(judge_model_config)
        strategy = strategy_factory.get_strategy(
            "default", benchmark_model, judge_model, selected_metrics
        )

    st.markdown(
        """
        <div class="alert alert-info">
            <strong>Benchmark running</strong><br>
            This may take several minutes depending on your configuration.
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    progress_bar = st.progress(0.0, text="Initializing...")

    def _ui_progress_callback(progress: float, message: str):
        progress_bar.progress(min(max(progress, 0.0), 1.0), text=message)

    try:
        results = strategy.evaluate(
            generation_config=generation_config, 
            progress_callback=_ui_progress_callback
        )
    except Exception as exc:
        st.markdown(
            f"""
            <div class="alert alert-warning">
                <strong>Benchmark failed</strong><br>
                {str(exc)}
            </div>
            """,
            unsafe_allow_html=True,
        )
        raise

    progress_bar.progress(1.0, text="Complete")

    # Store results
    st.session_state["last_benchmark_results"] = results
    st.session_state["last_predictions"] = getattr(strategy, "latest_predictions", None)
    st.session_state["prompts"] = strategy.prompts
    st.session_state["references"] = strategy.outputs
    st.session_state["comment_language"] = getattr(strategy, "comment_language", [])
    st.session_state["programming_language"] = getattr(strategy, "programming_language", [])
    st.session_state["topic"] = getattr(strategy, "topic", [])

    st.markdown(
        """
        <div class="alert alert-success">
            <strong>Benchmark completed</strong><br>
            Results are available in the Observation and Examples pages.
        </div>
        """,
        unsafe_allow_html=True,
    ) 