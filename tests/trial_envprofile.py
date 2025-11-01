import sys
from pathlib import Path

# Add /docker/scripts to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent / "scripts"))

print(sys.path)

from envprofile import EnvProfile
from luxforge_logger import luxforgeLogger

luxforgeLogger.task("envprofile_trial")
profile = EnvProfile()

luxforgeLogger.changelog("Trial EnvProfile loaded", profile.as_dict())

print("=== ENV PROFILE PREVIEW ===")
print(profile.preview())