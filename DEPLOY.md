# 🚀 GUIA DE DEPLOY: PLATAFORMA SPORTS TRADER AI

Este sistema foi projetado para rodar 24/7 em uma VPS e ter um dashboard acessível via web.

---

## 📂 1. PREPARAÇÃO GITHUB

1. Crie um repositório no GitHub (Privado recomendado).
2. Suba todos os arquivos do projeto:
   ```bash
   git init
   git add .
   git commit -m "Deploy: Plataforma Híbrida Profissional"
   git remote add origin https://github.com/SEU_USUARIO/SEU_REPO.git
   git push -u origin main
   ```

---

## 💻 2. DASHBOARD (STREAMLIT CLOUD)

Para ter o painel acessível online via link:
1. Vá em [Streamlit Cloud](https://share.streamlit.io/).
2. Conecte seu repositório do GitHub.
3. Aponte o arquivo de entrada para: `dashboard/app.py`.
4. Em **Secrets**, adicione suas chaves do `.env`:
   - `OPENROUTER_API_KEY`
   - `THE_ODDS_API_KEY`
   - `TELEGRAM_BOT_TOKEN` (opcional aqui se quiser sincronizar)

---

## 🖥️ 3. AUTOMAÇÃO 24H (VPS/LINUX)

Para que o robô envie sinais e monitore o YouTube sem parar:

1. Acesse sua VPS (via SSH).
2. Instale as dependências:
   ```bash
   cd AGENTE_ANALISTE_DE_FUTEBOL
   pip install -r requirements.txt
   ```
3. Instale o **PM2** (Gerenciador de Processos):
   ```bash
   sudo npm install -g pm2
   ```
4. Inicie o sistema:
   ```bash
   pm2 start main.py --name "trader-bot" --interpreter python3
   ```
5. Salve para reiniciar com a VPS:
   ```bash
   pm2 save
   pm2 startup
   ```

---

## ✅ 4. VERIFICAÇÃO FINAL

- **Telegram:** Verifique se os sinais estão chegando a cada 10 minutos.
- **YouTube:** O arquivo `data/youtube_seen_videos.json` deve começar a encher.
- **Dashboard:** Acesse o link do Streamlit Cloud para ver sua performance.

**BOAS OPERAÇÕES! 🚀🏦**
