"""Linux bridge build against a pinned, external official SDK (no vendor demos)."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys

SDK_COMMIT = "99478e5fb90de3b4a6db0080acacd373f8b36869"


def main():
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument("--sdk", type=Path, default=root/".deps"/"rplidar_sdk")
    args = parser.parse_args()
    if sys.platform != "linux":
        raise SystemExit("This bridge build is verified only on Linux; core demo/replay is portable")
    sdk = args.sdk.resolve()
    if not sdk.exists():
        sdk.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "clone", "https://github.com/Slamtec/rplidar_sdk.git", str(sdk)], check=True)
        subprocess.run(["git", "checkout", "--detach", SDK_COMMIT], cwd=sdk, check=True)
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=sdk, text=True).strip()
    if revision != SDK_COMMIT or subprocess.check_output(["git", "status", "--porcelain"], cwd=sdk):
        raise SystemExit("SDK must be clean and at the documented pinned revision")
    subprocess.run(["make", "-C", str(sdk/"sdk"), "-j2"], check=True)
    target = root/"artifacts"; target.mkdir(exist_ok=True)
    subprocess.run(["g++", "-std=c++17", "-Wall", "-Wextra", "-O2", "-I", str(sdk/"sdk"/"include"),
                    str(root/"drivers"/"c1_bridge.cpp"), str(sdk/"output"/"Linux"/"Release"/"libsl_lidar_sdk.a"),
                    "-pthread", "-o", str(target/"c1_bridge")], check=True)
    shutil.copyfile(sdk/"LICENSE", target/"SLAMTEC-SDK-LICENSE.txt")
    (target/"bridge-build.json").write_text(json.dumps({"sdk_commit": revision, "platform": sys.platform,
        "compiler": subprocess.check_output(["g++", "--version"], text=True).splitlines()[0]}, indent=2)+"\n")
    print(target/"c1_bridge")


if __name__ == "__main__":
    main()
