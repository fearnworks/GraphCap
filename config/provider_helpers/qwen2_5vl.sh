uv venv --python 3.12.8
source .venv/bin/activate
uv pip install vllm # ---> Now there is no need to install from source because of the latest release
uv pip install flash-attn --no-build-isolation # ---> Otherwise it will use xformers, or you can use flashinfer with uv pip install flashinfer-python
uv pip install "git+https://github.com/huggingface/transformers" # ---> This needs to be the last step, at least for now, once transformers release a new version, then you can just uv pip install transformers
VLLM_USE_V1=1 vllm serve Qwen/Qwen2.5-VL-7B-Instruct \
    --port 12434 \
    --host 0.0.0.0 \
    --max-model-len 16434 \
    --dtype bfloat16 \
    --served-model-name vision-worker \
    --limit-mm-per-prompt image=1,video=0