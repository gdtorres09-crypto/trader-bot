from youtube_transcript_api import YouTubeTranscriptApi
import logging

def test_yt_api():
    video_id = "4BIFErzjeJM" # Um dos IDs que falhou
    print(f"Testando API para {video_id}")
    try:
        # Tentativa 1: list + fetch
        print("Tentando list().fetch()...")
        ts = YouTubeTranscriptApi.list_transcripts(video_id).find_transcript(['pt', 'en']).fetch()
        print(f"Sucesso! Caracteres: {len(str(ts))}")
    except Exception as e:
        print(f"Falha 1: {e}")
        try:
            # Tentativa 2: get_transcript (se o dir mentiu)
            print("Tentando get_transcript()...")
            ts = YouTubeTranscriptApi.get_transcript(video_id)
            print(f"Sucesso! Caracteres: {len(str(ts))}")
        except Exception as e2:
            print(f"Falha 2: {e2}")

if __name__ == "__main__":
    test_yt_api()
