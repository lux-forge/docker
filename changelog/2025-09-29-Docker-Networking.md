## 2025-09-29 — Docker Networking & Env Profiling


**Tags** 
`docker`, `python`, `networking`, `env profiling`, `pathloader`,`venv`,`requirements`,`gitignore`

Created the first Menu item to manage docker network instances. It detects any configs currently running and aligns with deployed configs located in the configs folder.
- Casts all env vars located in env files to global env variables.
- Integrated with Logging class.
- Auto-captures and warns on clashes and overrides.
- Profiled example env files for users to use and modify.
- Added PathLoader class to provide callable paths from anywhere in the tools, lifting the need to run from a specific locatin.
- Added venv auto-creation via bash (probably need a ps1 variant too).
- Added auto-creation of requirements.txt from within the venv.
- Upgraded .gitignore to be better placed to allow all EXAMPLE files so they're viable for external use.
- Added version.yaml
