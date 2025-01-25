from openai import OpenAI


class GeminiClient(OpenAI):
    def __init__(self, api_key, base_url):
        self.base_url = base_url
        super().__init__(api_key=api_key, base_url=base_url)
