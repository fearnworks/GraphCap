uv venv --python 3.12.8
source .venv/bin/activate
uv pip install hf_transfer
uv pip install "git+https://github.com/ywang96/vllm@qwen2_5_vl"
uv pip install "git+https://github.com/huggingface/transformers"
VLLM_USE_V1=1 vllm serve unsloth/Qwen2.5-VL-7B-Instruct \
    --port 13434 \
    --host 0.0.0.0 \
    --max-model-len 16000 \
    --dtype bfloat16 \
    --served-model-name vision-worker \