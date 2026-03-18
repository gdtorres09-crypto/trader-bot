from openai import OpenAI
from app_config.settings import OPENROUTER_API_KEY

class LLMProvider:
    def __init__(self):
        self.api_key = OPENROUTER_API_KEY
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key,
        )

    def chat(self, user_message, history=None, context="", model_type="light"):
        """
        Envia uma mensagem para o LLM via OpenRouter com histórico.
        IA LEVE: google/gemini-2.0-flash-lite-001
        IA PESADA: google/gemini-2.0-flash-001
        """
        if not self.api_key:
            return "Erro: Chave OpenRouter não configurada."

        model = "google/gemini-2.0-flash-lite-001" if model_type == "light" else "google/gemini-2.0-flash-001"

        system_prompt = (
            "Você é o SPORTS_BETTING_ANALYST_AI. Analista direto, prático e sem enrolação. "
            "RESPONDA APENAS O QUE FOI PERGUNTADO. Evite avisos longos ou introduções desnecessárias. "
            "Se o usuário pedir uma aposta, dê o Jogo, a Aposta e a Odd (Betano) de forma curta e centralizada. "
            "Use negrito apenas para o essencial. "
            f"\nContexto Atual: {context}"
        )

        messages = [{"role": "system", "content": system_prompt}]
        if history:
            messages.extend(history)
        
        messages.append({"role": "user", "content": user_message})

        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Erro: {str(e)}"

    def transcribe_audio(self, audio_file_path):
        """
        Transcreve áudio usando o modelo Whisper-1 (OpenAI/OpenRouter).
        """
        if not self.api_key:
            return "Erro: Chave de API não configurada para transcrição."

        try:
            with open(audio_file_path, "rb") as audio_file:
                # Nota: OpenRouter pode requerer o modelo específico da OpenAI ou seu wrapper
                # Se estiver usando o client OpenAI padrão, ele tentará o endpoint de transcrição
                transcription = self.client.audio.transcriptions.create(
                    model="whisper-1", 
                    file=audio_file,
                    response_format="text"
                )
                return transcription
        except Exception as e:
            print(f"Erro na transcrição Whisper: {str(e)}")
            return f"Erro ao processar áudio: {str(e)}"
