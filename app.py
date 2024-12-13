import sys
import serial
import serial.tools.list_ports
from PyQt5 import QtWidgets, QtGui, QtCore

class ESP32Configurator(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Configurador ESP32")
        self.setGeometry(100, 100, 400, 600)

        self.layout = QtWidgets.QVBoxLayout()

        # Estado de dispositivo detectado
        self.device_status_box = QtWidgets.QFrame()
        self.device_status_box.setFrameShape(QtWidgets.QFrame.Box)
        self.device_status_box.setFrameShadow(QtWidgets.QFrame.Raised)
        self.device_status_layout = QtWidgets.QVBoxLayout()
        
        self.device_status_label = QtWidgets.QLabel("Dispositivo detectado: No")
        self.device_status_label.setFont(QtGui.QFont("Arial", 12))
        self.device_status_label.setAlignment(QtCore.Qt.AlignCenter)
        self.device_status_layout.addWidget(self.device_status_label)
        
        self.instructions_label = QtWidgets.QLabel("Instrucciones si no se detecta el dispositivo:\n1. Cierre esta aplicación.\n2. Conecte el dispositivo y vuelva a abrir la aplicación.")
        self.instructions_label.setFont(QtGui.QFont("Arial", 10))
        self.instructions_label.setAlignment(QtCore.Qt.AlignCenter)
        self.device_status_layout.addWidget(self.instructions_label)

        self.device_status_box.setLayout(self.device_status_layout)
        self.layout.addWidget(self.device_status_box)

        # Título
        title = QtWidgets.QLabel("Configuración del ESP32")
        title.setFont(QtGui.QFont("Arial", 18))
        title.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(title)

        # Formulario de entrada de datos
        self.device_id_input = self.create_input_field("ID del Dispositivo")
        self.ssid_input = self.create_input_field("SSID Wi-Fi")
        self.password_input = self.create_input_field("Clave Wi-Fi", password=True)
        self.user_email_input = self.create_input_field("Correo del Usuario")
        self.user_password_input = self.create_input_field("Contraseña de Usuario", password=True)

        # Botón de registro
        self.register_button = QtWidgets.QPushButton("Registrar Datos")
        self.register_button.setFont(QtGui.QFont("Arial", 12))
        self.register_button.clicked.connect(self.register_data)
        self.layout.addWidget(self.register_button)

        # Spinner de carga
        self.spinner = QtWidgets.QLabel("")
        self.spinner.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.spinner)

        self.setLayout(self.layout)
        self.update_device_status()

    def create_input_field(self, label_text, password=False):
        layout = QtWidgets.QVBoxLayout()

        label = QtWidgets.QLabel(label_text)
        label.setFont(QtGui.QFont("Arial", 12))
        layout.addWidget(label)

        input_field = QtWidgets.QLineEdit()
        input_field.setFont(QtGui.QFont("Arial", 12))
        if password:
            input_field.setEchoMode(QtWidgets.QLineEdit.Password)
        layout.addWidget(input_field)

        self.layout.addLayout(layout)
        return input_field

    def register_data(self):
        self.register_button.setEnabled(False)
        self.spinner.setText("Enviando datos... 🔃")

        device_id = self.device_id_input.text()
        ssid = self.ssid_input.text()
        wifi_password = self.password_input.text()
        user_email = self.user_email_input.text()
        user_password = self.user_password_input.text()

        if not all([device_id, ssid, wifi_password, user_email, user_password]):
            self.show_error_message("Por favor, complete todos los campos.")
            self.spinner.setText("")
            self.register_button.setEnabled(True)
            return

        port = self.detect_esp32_port()
        if port:
            try:
                self.send_data_to_esp32(port, device_id, ssid, wifi_password, user_email, user_password)
                self.show_success_message(device_id, ssid, wifi_password, user_email, user_password)
            except Exception as e:
                self.show_error_message(f"Error al enviar los datos: {str(e)}")
        else:
            self.show_error_message("No se detectó ningún ESP32 conectado.")

        self.spinner.setText("")
        self.register_button.setEnabled(True)
        self.update_device_status()

    def detect_esp32_port(self):
        ports = list(serial.tools.list_ports.comports())
        for port in ports:
            if "USB-SERIAL" in port.description or "CH340" in port.description or "CP2102" in port.description or "Silicon Labs" in port.description:
                return port.device
        return None

    def send_data_to_esp32(self, port, device_id, ssid, wifi_password, user_email, user_password):
        ser = serial.Serial(port, 115200, timeout=2)
        ser.write(f"ID:{device_id}\n".encode())
        ser.write(f"SSID:{ssid}\n".encode())
        ser.write(f"PASSWORD:{wifi_password}\n".encode())
        ser.write(f"EMAIL:{user_email}\n".encode())
        ser.write(f"USERPASS:{user_password}\n".encode())
        ser.close()

    def show_error_message(self, message):
        msg_box = QtWidgets.QMessageBox()
        msg_box.setIcon(QtWidgets.QMessageBox.Critical)
        msg_box.setWindowTitle("Error")
        msg_box.setText(message)
        msg_box.exec_()

    def show_success_message(self, device_id, ssid, wifi_password, user_email, user_password):
        message = (
            f"ID del Dispositivo: {device_id}\n"
            f"SSID: {ssid}\n"
            f"Clave Wi-Fi: {wifi_password}\n"
            f"Correo de Usuario: {user_email}\n"
            f"Contraseña de Usuario: {user_password}\n"
        )

        msg_box = QtWidgets.QMessageBox()
        msg_box.setIcon(QtWidgets.QMessageBox.Information)
        msg_box.setWindowTitle("Datos Actualizados")
        msg_box.setText("Los datos se actualizaron correctamente.")
        msg_box.setDetailedText(message)
        msg_box.exec_()

        QtCore.QCoreApplication.quit()
    
    def update_device_status(self):
        port = self.detect_esp32_port()
        status = "Sí" if port else "No"
        self.device_status_label.setText(f"Dispositivo detectado: {status}")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = ESP32Configurator()
    window.show()
    sys.exit(app.exec_())
