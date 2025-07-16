
from typing import Dict, List
import yaml
import os

class PromptBuilder:
    def __init__(self, prompt_dir: str = "prompts", language: str = "en"):
        self.prompt_dir = prompt_dir
        self.language = language
        self.template_dir = os.path.join(prompt_dir, "templates")
        self.system_prompt_path = os.path.join(prompt_dir, "system", "system_prompt.txt")
        self.index_path = os.path.join(prompt_dir, "index.yaml")
        self.templates = {}
        self.load_index()
        self.load_system_prompt()

    def load_index(self):
        with open(self.index_path, "r", encoding="utf-8") as f:
            self.index = yaml.safe_load(f)

    def load_system_prompt(self):
        with open(self.system_prompt_path, "r", encoding="utf-8") as f:
            self.system_prompt = f.read()

    def _load_template(self, filename: str) -> str:
        if filename in self.templates:
            return self.templates[filename]
        path = os.path.join(self.template_dir, filename)
        with open(path, "r", encoding="utf-8") as f:
            template = f.read()
        self.templates[filename] = template
        return template

    def build(self,
              message: str,
              context: Dict,
              emotion: str,
              strategy: str,
              stage_name: str,
              needs: List[str],
              positive_indicators: str = "") -> str:
        # Select template
        template_file = self.index["mappings"].get(strategy, self.index["default"])
        template = self._load_template(template_file)

        # Format context
        context_str = self._format_context(context)
        needs_str = ", ".join(needs) if needs else "general support"

        prompt = template.format(
            message=message,
            context=context_str,
            emotion=emotion,
            stage_name=stage_name,
            needs=needs_str,
            positive_indicators=positive_indicators
        )

        full_prompt = f"{self.system_prompt}\n\n{prompt}"
        return full_prompt

    def _format_context(self, context: Dict) -> str:
        messages = context.get("messages", [])[-6:]
        formatted = []
        for msg in messages:
            role = "User" if msg["role"] == "user" else "Assistant"
            formatted.append(f"{role}: {msg['content']}")
        return "\n".join(formatted) if formatted else "(new conversation)"
