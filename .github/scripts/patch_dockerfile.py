#!/usr/bin/env python3
"""Adapt vLLM's docker/Dockerfile for a CUDA 12.6 wheel build.

Two independent changes:

1. DeepEP: the Dockerfile compiles DeepEP for `9.0a 10.0a` unconditionally, but
   nvcc only understands sm_100 from CUDA 12.8 on. On CUDA < 12.8 fall back to
   sm_90a only.
2. Optionally drop the DeepEP build entirely. Its wheels are copied into the
   runtime image, not into the vllm wheel, so a wheel-only build does not need
   them and skips a large compile.
"""

import pathlib
import sys

DEEPEP_ARCH_OLD = """    DEEPEP_ARCH_LIST='9.0a 10.0a' && \\
"""

DEEPEP_ARCH_NEW = """    DEEPEP_ARCH_LIST='9.0a 10.0a' && \\
    # nvcc < 12.8 has no sm_100 support, so DeepEP can only target sm_90a there
    if [ "$(printf '%s\\n' 12.8 "$CUDA_VERSION" | sort -V | head -n1)" != 12.8 ]; then \\
        DEEPEP_ARCH_LIST='9.0a'; \\
    fi && \\
"""

DEEPEP_COPY_BLOCK = """# Copy extension wheels from extensions-build stage for later use
COPY --from=extensions-build /tmp/ep_kernels_workspace/dist /tmp/ep_kernels_workspace/dist

# Record the EP kernels wheel checksum for the same cache-busting purpose.
RUN sha256sum /tmp/ep_kernels_workspace/dist/*.whl \\
    > /tmp/ep_kernels_workspace/dist/wheels.sha256
"""


def replace_once(text: str, old: str, new: str, what: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"error: expected exactly 1 occurrence of {what}, found {count}")
    return text.replace(old, new)


def main() -> None:
    src = pathlib.Path(sys.argv[1])
    dst = pathlib.Path(sys.argv[2])
    build_deepep = len(sys.argv) > 3 and sys.argv[3].strip().lower() == "true"

    text = src.read_text()
    text = replace_once(text, DEEPEP_ARCH_OLD, DEEPEP_ARCH_NEW, "DeepEP arch list")

    if not build_deepep:
        text = replace_once(text, DEEPEP_COPY_BLOCK, "", "DeepEP wheel copy block")

    dst.write_text(text)
    print(f"wrote {dst} (deepep={build_deepep})")


if __name__ == "__main__":
    main()
