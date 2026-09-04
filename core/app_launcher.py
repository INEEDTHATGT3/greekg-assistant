import os
import difflib

FILLER_WORDS = ("please", "open", "launch", "start", "the", "app", "application")
FUZZY_MATCH_CUTOFF = 0.4


class AppLauncher:
    def __init__(self, apps_config: dict):
        self.apps = apps_config

    def reload(self, apps_config: dict):
        self.apps = apps_config

    def find_and_launch(self, raw_text: str) -> tuple[bool, str]:
        cleaned = raw_text.lower().strip()
        for filler in FILLER_WORDS:
            cleaned = cleaned.replace(filler, "")
        cleaned = cleaned.strip()

        if not self.apps:
            return False, "No apps configured"

        match = difflib.get_close_matches(cleaned, self.apps.keys(), n=1, cutoff=FUZZY_MATCH_CUTOFF)
        if not match:
            match = [name for name in self.apps if name in raw_text]

        if match:
            app_name = match[0]
            path = self.apps[app_name]
            try:
                os.startfile(path)
                return True, f"Launched '{app_name}'"
            except Exception as e:
                return False, f"Launch failed for '{app_name}': {e}"
        return False, f'No matching app for "{cleaned}"'
