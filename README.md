# 🏭 Gemelo Digital & Control HIL: Lazo PID en Python vía Modbus TCP

Este repositorio contiene la implementación de un sistema de control **Hardware-in-the-Loop (HIL)** para la regulación continua de nivel de fluidos, utilizando un enfoque de **Soft-PLC** programado íntegramente en Python.

El proyecto integra un modelo de planta virtual (**Factory I/O**) con lógica de control externa, comunicando sensores y actuadores industriales en tiempo real mediante el protocolo estándar **Modbus TCP**.

<p align="center">
  <img src="Screenshot 2026-09-21 180749.png" alt="Gemelo Digital Factory IO" width="800"/>
</p>

## ⚙️ Arquitectura de Integración IT/OT

El sistema puentea el mundo informático (IT) y el operativo (OT) sin depender de bloques de control predefinidos en TIA Portal, trasladando el peso computacional del cálculo analógico a un script de Python.

* **Planta Virtual (OT):** Gemelo Digital de un tanque de agua en *Factory I/O*. Modelado de dinámica de fluidos con válvulas proporcionales de llenado y vaciado.
* **Controlador (IT/OT):** Script en Python actuando como nodo de control y pasarela IIoT.
* **Protocolo de Comunicación:** `Modbus TCP` (Puerto 502). Lectura de *Holding Registers* para sensores (telemetría) y escritura para comandos de actuación (válvulas).

## 🧠 Core Matemático: Controlador PID "From Scratch"

En lugar de utilizar librerías genéricas de control, se ha desarrollado un **controlador PID matemático personalizado** orientado a objetos (`class Tanque()`). Esto permite un control absoluto sobre el ajuste fino del lazo:

1. **Escalado de Señales:** Transformación de las variables raw del Modbus (0-1000) a magnitudes físicas operativas (0-300 cm de nivel) y variables de control (0-100% apertura de válvula).
2. **Histórico y Error Acumulado:** Implementación de un buffer dinámico para calcular la pendiente (Acción Derivativa) y la integral del error (Acción Integral) mitigando picos espurios.
3. **Saturación (Anti-Windup):** Limitación por software de la salida de control (0% al 100%) para evitar la saturación matemática de la válvula proporcional.
4. **Modos de Operación:** Soporte para transiciones bumpless entre modo *Manual* (SetPoint directo a la válvula) y *Automático* (SetPoint de nivel objetivo).

## 🛠️ Stack Tecnológico
* **Lenguaje:** Python 3
* **Librerías de red:** `pymodbus` (ModbusTcpClient), `struct`, `time`
* **Entornos Industriales:** Factory I/O (Gemelo Digital), TIA Portal (Siemens S7-1200)
* **Teoría Aplicada:** Control de procesos continuos, Lógica PID, Escalado analógico.

---
*Desarrollado por **Rafael Rodríguez Sollero** - Estudiante de Ingeniería Electrónica Industrial & Control Engineer.*
