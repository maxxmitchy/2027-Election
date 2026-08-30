from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
exec((Path(__file__).resolve().parents[1]/"_phase7_runner_impl.tmp").read_text()) if (Path(__file__).resolve().parents[1]/"_phase7_runner_impl.tmp").exists() else None
