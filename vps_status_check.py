import paramiko

# Configuracoes da VPS
VPS_IP = "72.61.54.103"
VPS_USER = "root"
VPS_PASS = "16152590De@."

def check_status():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(VPS_IP, username=VPS_USER, password=VPS_PASS)
        print("--- STATUS DO PM2 ---")
        stdin, stdout, stderr = ssh.exec_command("pm2 list")
        out = stdout.read().decode('utf-8', errors='ignore')
        print(out.encode('ascii', 'ignore').decode('ascii'))
        
        print("--- ULTIMOS LOGS ---")
        stdin, stdout, stderr = ssh.exec_command("pm2 logs bot-trader --lines 20 --nostream")
        out_logs = stdout.read().decode('utf-8', errors='ignore')
        print(out_logs.encode('ascii', 'ignore').decode('ascii'))
        
    except Exception as e:
        print(f"Erro ao verificar: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    check_status()
