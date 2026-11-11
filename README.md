# vLLM 0.33.0 CUDA 12.6 wheel builder

Builds a `vllm 0.33.0` wheel for **CUDA 12.6** (torch 2.14.0+cu126) from the
upstream `vllm-project/vllm` v0.33.0 tag, on GitHub-hosted runners.

Targets `sm_86` (A40), `sm_89` (L40), `sm_90` (H100).

## Why this exists

Upstream vLLM stopped publishing CUDA 12 wheels (only CUDA 13.0 remains), but
the pinned `torch==2.14.0` is still published for `cu126` — PyTorch dropped
`cu129` after torch 2.13.0. So CUDA 12.6 is the only CUDA 12 line that matches
vLLM 0.33.0's torch pin.

## Usage

1. Create a **public** repository (public = unlimited Actions minutes and the
   4 vCPU / 16 GB runner; private gets 2 vCPU / 8 GB and a 2000 min/month cap).
2. Push this directory to it.
3. Actions -> "Build vLLM v0.33.0 CUDA 12.6 wheel" -> Run workflow.
4. Download the wheel from the run's **Release** (or the artifact).

## Install

```bash
pip install vllm-0.33.0-cp38-abi3-manylinux_2_28_x86_64.whl \
    --extra-index-url https://download.pytorch.org/whl/cu126
```

The extra index is required: without it pip resolves the PyPI `torch==2.14.0`,
which is the CUDA 13 build, and the wheel will not import.

## Inputs

| Input | Default | Notes |
|---|---|---|
| `deepep` | `false` | Compiles DeepEP kernels. They are **not** part of the vllm wheel — only the runtime Docker image installs them. Enable only if you also build the image. |
| `max_jobs` | `4` | Raise on larger runners. |

## Notes

- Standard runners have 14 GB on `/`; `easimon/maximize-build-space` mounts the
  ~74 GB scratch volume and moves the Docker root there.
- GitHub-hosted jobs are hard-capped at 6 hours. The build is expected to take
  3-4.5 h on 4 vCPU with three architectures.
- `vllm-rs` (Rust) and `csrc` are compiled from source; the Dockerfile patch is
  applied to a copy outside the clone so the tree stays clean and
  setuptools-scm reports exactly `0.33.0`.
