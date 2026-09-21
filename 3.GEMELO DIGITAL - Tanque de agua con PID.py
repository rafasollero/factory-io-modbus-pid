## GEMELO DIGITAL - Tanque con PID ##

from pymodbus.client import ModbusTcpClient
import time

def escalar_valor(valor,min_inicial=0, max_inicial=32767, min_final=0.0, max_final=100.0):
    valor_escalado = (valor - min_inicial) * (max_final - min_final) / (max_inicial - min_inicial) + min_final
    return valor_escalado

class Tanque():
    def __init__(self,ip,dispositivo,dirNivel,dirValvula):
        self.ip = ip
        self.dispositivo = dispositivo
        self.dirNnivel = dirNivel
        self.dirValvula = dirValvula
        self.Nivel = 0 # nivel real del tanque
        self.Valvula = 0 # nivel de la válvula
        self.anteriores = []

        # ----------------- Configuramos el cliente Modbus -----------------
        self.cliente = ModbusTcpClient(self.ip)
        self.cliente.connect()

    def leerNivel(self):
        lectura = self.cliente.read_holding_registers(self.dirNnivel)
        # El tanque en Factory IO representa 1000 como 10.00v, correspondiente a 300 cm de altura
        # Escalamos
        salida = escalar_valor(lectura.registers[0],0,1000,0,300)
        return salida
    
    def comandarValvula(self):
        # la señal de la válvula viene desde el PID, y tiene limites de 0 a 100
        # el tanque espera de 0 a 1000. 
        #Escalamos
        valvulaEscalada = int(escalar_valor(self.Valvula,0,100,0,1000))
        #ahora si enviamos el comando
        self.cliente.write_register(self.dirValvula,valvulaEscalada)

    def PID(self,input, Man_Auto = False, SetpointMan = 0.0, SetpointAuto = 0.0):
                """
                    Calcula la salida de un controlador PID (Proporcional, Integral, Derivativo).

                    Args:
                        Man_Auto (bool): Modo manual (True) o automático (False).
                        SetpointMan (bool): Ignorado si Man_Auto es True. Modo manual de setpoint (True) o automático (False).
                        SetpointAuto (float): El valor del setpoint en modo automático.

                    Returns:
                        None

                    El método calcula la salida del controlador PID utilizando el valor actual (input) y el setpoint (SetpointAuto).
                    Se almacena el histórico de velocidades en self.anteriores y se limita a 100 elementos.
                    Se calculan los componentes P, I y D del controlador y se suman para obtener la salida.
                    La salida se limita al rango de 0 a 100.

                    """
                if Man_Auto == False:     
                    # Si el PID está en modo automático...

                    # Almaceno el vector velocidad en una lista de 100 elementos.
                    self.anteriores.append(input)
                    if len(self.anteriores) > 100:
                        self.anteriores = self.anteriores[-100:]

                    SP = SetpointAuto        
                    E = SP - input
                    self.error = E 
                    
                    #error es la diferencia entre lo que tengo, y mi setpoint actual. Usamos la lista para ello. 
                    E_accu = [(SP - elem) for elem in self.anteriores[-20:]]
                    self.error_accu = E_accu
                    
                    kP = 6.05
                    kI = 1.35
                    kD = 0.7

                    #La acción proporcional es el error multiplicado por una constante
                    aP = self.error * kP
                    
                    #La acción integral es el área de los valores, dividido por la constante
                    aI = (kP * (sum(self.error_accu) / (len(self.error_accu)) * kI))
                    
                    #La acción derivativa es la proyección a futuro (pendiente) del error, multiplicado por una constante
                    if len(self.anteriores)>2:
                        aD = (self.error_accu[-1]-self.error_accu[-2])*kD*kP
                    else:
                        aD = 0.0
                    
                    #sumamos las componentes de las acciones Proporcional, Integral y Derivativa
                    Salida = aP + aI + aD

                    #Limitamos la válvula de salida
                    if Salida < 0:
                        self.Valvula = 0
                    elif Salida > 100:
                        self.Valvula = 100         
                    else:
                        self.Valvula = Salida

                else:
                    # Si estamos en modo "Manual", la válvula se pone en la posición que definimos en el setpoint.
                    self.Valvula = SetpointMan
                self.comandarValvula()

TK1 = Tanque(
     ip = "192.168.1.26",
     dirNivel=0,
     dirValvula=5,
     dispositivo=1
)

try:
    while True:
        PV = TK1.leerNivel() #Lectura del tanque, usada para el PID
        SP = 125.0 # Asignamos cuánto queremos llenar el tanque
        TK1.PID(
            input=PV,
            SetpointAuto=SP,
        )

        print(f"Nivel: {PV}",f"Consigna: {SP}",f"Valvula: {TK1.Valvula:.2f}           ",end='\r')
        time.sleep(0.25)

except KeyboardInterrupt:
    print("Lectura finalizada")
    TK1.cliente.close()
    print("Cerrado")