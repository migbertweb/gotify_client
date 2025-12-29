# Gotify Desktop Client (Arch Linux)

Cliente de escritorio para Gotify escrito en Python con PyQt6. Soporta notificaciones de sistema, icono en la bandeja del sistema (System Tray) y minimizado.

## Características

- Conexión WebSocket a servidor Gotify.
- Notificaciones nativas de escritorio.
- Icono en bandeja del sistema.
- Minimizar a la bandeja al cerrar.
- Configuración persistente.

## Requisitos

- Python 3
- PyQt6
- websocket-client
- requests (opcional, para futuras expansiones)

### Instalación de dependencias

En Arch Linux:

```bash
sudo pacman -S python-pyqt6 python-websocket-client python-requests
```

O usando pip:

```bash
pip install -r requirements.txt
```

## Instalación Manual y Ejecución

1.  **Dar permisos de ejecución:**

    ```bash
    chmod +x main.py
    ```

2.  **Ejecutar:**

    ```bash
    ./main.py
    ```

3.  **Configuración:**
    - Al iniciar por primera vez, se abrirá la ventana de configuración.
    - Ingrese la URL de su servidor Gotify (ej. `https://gotify.midominio.com`).
    - Ingrese el Token del Cliente (Client Token) creado en su servidor Gotify.
    - Click en "Save & Connect".

## Test Manual

1.  Abra la aplicación y asegúrese de que el estado en la parte superior diga **"Connected"** en verde.
2.  Vaya a su servidor Gotify y envíe un mensaje de prueba a través de la interfaz web o usando `curl`:
    ```bash
    curl -X POST "https://gotify.midominio.com/message?token=<APP_TOKEN>" -F "title=Test" -F "message=Hola Mundo"
    ```
3.  Debería ver:
    - Una notificación emergente en su escritorio.
    - El mensaje listado en la ventana principal de la aplicación.
4.  Cierre la ventana principal. La aplicación debería seguir corriendo en la bandeja del sistema (icono visible).
5.  Click derecho en el icono de la bandeja -> "Quit" para cerrar totalmente.

## Integración con el Escritorio (.desktop)

Para que aparezca en su menú de aplicaciones:

```bash
# Copiar el archivo desktop a las aplicaciones locales
mkdir -p ~/.local/share/applications
cp gotify-client.desktop ~/.local/share/applications/

# Actualizar base de datos
update-desktop-database ~/.local/share/applications
```

## Ejecutar como Servicio Systemd (Usuario)

Puede configurar la aplicación para que inicie automáticamente en segundo plano con su sesión de usuario.

1.  **Copiar el archivo de servicio:**

    ```bash
    mkdir -p ~/.config/systemd/user/
    cp gotify-client.service ~/.config/systemd/user/
    ```

2.  **Recargar Systemd:**

    ```bash
    systemctl --user daemon-reload
    ```

3.  **Habilitar e Iniciar el servicio:**

    ```bash
    systemctl --user enable --now gotify-client.service
    ```

4.  **Verificar estado:**
    ```bash
    systemctl --user status gotify-client.service
    ```

**Nota:** Al correr como servicio, la aplicación necesitará acceso al servidor X11/Wayland para mostrar la GUI y el icono de tray. El archivo de servicio incluido ya tiene configurada la variable `DISPLAY=:0`.
