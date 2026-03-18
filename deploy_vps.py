import paramiko
import os
import time

# Configuracoes da VPS
VPS_IP = "72.61.54.103"
VPS_USER = "root"
VPS_PASS = "16152590De@."
REMOTE_DIR = "/root/bot-trader"

# Lista de pastas e arquivos para upload
INCLUDE_DIRS = ['agents', 'config', 'core', 'integrations', 'services', 'skills', 'data']
INCLUDE_FILES = ['main.py', 'requirements.txt', '.env']

def deploy():
    print(f"--- Iniciando Migracao para {VPS_IP} ---")
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(VPS_IP, username=VPS_USER, password=VPS_PASS)
        print("OK: Conectado a VPS!")
        
        # 1. Preparar Ambiente
        print("PREPARANDO ambiente Linux...")
        commands = [
            "apt update && apt upgrade -y",
            "apt install python3 python3-pip nodejs npm git -y",
            "npm install -g pm2",
            f"mkdir -p {REMOTE_DIR}"
        ]
        
        for cmd in commands:
            print(f"Executando: {cmd}")
            stdin, stdout, stderr = ssh.exec_command(cmd)
            stdout.channel.recv_exit_status()
            
        # 2. Upload de Arquivos
        scp = ssh.open_sftp()
        
        # Criar subpastas
        for d in INCLUDE_DIRS:
            try: scp.mkdir(f"{REMOTE_DIR}/{d}")
            except: pass
            
            # Upload arquivos da pasta
            local_path = os.path.join(os.getcwd(), d)
            if not os.path.exists(local_path): continue
            
            for file in os.listdir(local_path):
                if file.endswith('.py') or file.endswith('.js') or file.endswith('.db'):
                    print(f"Enviando {d}/{file}...")
                    scp.put(os.path.join(local_path, file), f"{REMOTE_DIR}/{d}/{file}")

        # Upload arquivos raiz
        for f in INCLUDE_FILES:
            if os.path.exists(f):
                print(f"Enviando {f}...")
                scp.put(f, f"{REMOTE_DIR}/{f}")
            else:
                print(f"AVISO: Arquivo {f} nao encontrado localmente.")
        
        scp.close()
        
        # 3. Instalar Dependencias e Iniciar com PM2
        print("Finalizando instalacao e iniciando bot...")
        final_cmds = [
            f"cd {REMOTE_DIR} && pip3 install -r requirements.txt --break-system-packages --ignore-installed",
            f"cd {REMOTE_DIR} && pm2 stop bot-trader || true",
            f"cd {REMOTE_DIR} && pm2 start main.py --interpreter python3 --name bot-trader",
            "pm2 startup",
            "pm2 save"
        ]
        
        for cmd in final_cmds:
             print(f"Executando: {cmd}")
             stdin, stdout, stderr = ssh.exec_command(cmd)
             exit_status = stdout.channel.recv_exit_status()
             if exit_status != 0:
                 err_msg = stderr.read().decode('utf-8', errors='ignore')
                 sanitized_msg = err_msg.encode('ascii', 'ignore').decode('ascii')
                 print(f"ERRO em: {cmd}. Saida: {sanitized_msg}")

        print("\nDEPOIS DE TUDO: MIGRACAO CONCLUIDA COM SUCESSO!")
        print("Use 'pm2 logs bot-trader' no terminal da VPS para monitorar.")
        
    except Exception as e:
        sanitized_err = str(e).encode('ascii', 'ignore').decode('ascii')
        print(f"ERRO CRITICO NA DEPLOY: {sanitized_err}")
    finally:
        ssh.close()

if __name__ == "__main__":
    deploy()
