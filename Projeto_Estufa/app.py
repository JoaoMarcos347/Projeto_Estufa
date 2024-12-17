from flask import Flask, jsonify, render_template, request
import serial
import threading

app = Flask(__name__)

# Configuração da porta serial
ser = None
modo_automatico = False  # Variável para armazenar o estado do modo automático

# Dados iniciais
data = {
    "ldr": 0,
    "humidity_soil": 0,
    "temperature": 0,
    "humidity_dht": 0,
    "lamp": "Desligado",
    "cooler": "Desligado",
    "pump": "Desligado",
    "modo_automatico": False
}

# Função para inicializar a porta serial
def init_serial():
    global ser
    try:
        ser = serial.Serial('COM3', 9600, timeout=1)  # Configura a porta COM3 com timeout
        print("Porta serial COM3 aberta com sucesso!")
    except serial.SerialException as e:
        print(f"Erro ao abrir a porta serial: {e}")
        ser = None

# Função para leitura contínua da porta serial
def read_from_serial():
    if ser:
        while True:
            try:
                if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8').strip()
                    print(f"Received line: {line}")  # Log da linha recebida
                    process_serial_data(line)
            except Exception as e:
                print(f"Erro ao ler da porta serial: {e}")

# Função para processar e atualizar os dados recebidos
def process_serial_data(line):
    print(f"Processando linha recebida: {line}")  # Exibe a linha recebida para depuração
    try:
        parts = line.split(", ")  # Divide os dados por ", "
        for part in parts:
            key, value = part.split(": ")  # Divide cada parte em chave e valor
            key = key.strip()  # Remove espaços em branco extras
            value = value.strip()  # Remove espaços em branco extras
            
            # Atualiza o dicionário de dados com base na chave
            if key in ["LDR", "Valor LDR"]:
                data["ldr"] = int(value)
                print(f"LDR processado: {data['ldr']}")  # Log do valor do LDR
            elif key == "Temp":
                data["temperature"] = float(value)
                print(f"Temperatura processada: {data['temperature']}")  # Log do valor da temperatura
            elif key in ["HumidityAir", "Umidade do ar"]:
                data["humidity_dht"] = float(value)
            elif key in ["HumiditySoil", "Umidade do solo"]:
                data["humidity_soil"] = float(value)
            elif key == "LAMPADA":
                data["lamp"] = "Ligado" if value == "ON" else "Desligado"
            elif key == "COOLER":
                data["cooler"] = "Ligado" if value == "ON" else "Desligado"
            elif key == "BOMBA":
                data["pump"] = "Ligado" if value == "ON" else "Desligado"
    except ValueError as e:
        print(f"Erro ao processar a linha: {line} - {e}")

    print("Dicionário atualizado:", data)  # Exibe o dicionário atualizado



# Rota para alternar o modo automático
@app.route('/toggle_auto_mode', methods=['POST'])
def toggle_auto_mode():
    global modo_automatico
    modo_automatico = not modo_automatico
    data["modo_automatico"] = modo_automatico
    return jsonify(data)

# Rota para controle manual dos atuadores
@app.route('/control', methods=['POST'])
def control_actuator():
    if modo_automatico:
        return jsonify({"error": "Modo automático ativado. Desative para controle manual."}), 403
    
    actuator = request.json.get("actuator")
    action = request.json.get("action")
    
    if actuator == "lamp":
        data["lamp"] = "Ligado" if action == "on" else "Desligado"
        enviar_comando_serial("LIGAR_LAMPADA" if action == "on" else "DESLIGAR_LAMPADA")
    elif actuator == "cooler":
        data["cooler"] = "Ligado" if action == "on" else "Desligado"
        enviar_comando_serial("LIGAR_COOLER" if action == "on" else "DESLIGAR_COOLER")
    elif actuator == "pump" and action == "on":
        data["pump"] = "Ligado"
        enviar_comando_serial("LIGAR_BOMBA")
        threading.Timer(2, desligar_bomba).start()
    
    return jsonify(data)

# Envia comandos ao Arduino via porta serial
def enviar_comando_serial(comando):
    if ser:
        try:
            ser.write(f"{comando}\n".encode())
            print(f"Enviado: {comando}")
        except Exception as e:
            print(f"Erro ao enviar comando: {e}")

# Desliga a bomba após um intervalo de tempo
def desligar_bomba():
    data["pump"] = "Desligado"
    enviar_comando_serial("DESLIGAR_BOMBA")

# Rota para obter os dados dos sensores
@app.route('/data', methods=['GET'])
def get_data():
    print("Dados enviados para o frontend:", data)  # Log para depuração
    return jsonify(data)


# Rota para exibir a página principal
@app.route('/')
def index():
    return render_template('index.html')

# Inicialização do sistema
if __name__ == '__main__':
    init_serial()
    if ser:
        threading.Thread(target=read_from_serial, daemon=True).start()
    app.run(host='0.0.0.0')
