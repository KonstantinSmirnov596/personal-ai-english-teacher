# Cómo instalar Personal AI English Teacher

La instalación se hace con un doble clic y sin permisos de administrador. No necesitas Python ni ninguna otra herramienta: el instalador trae las suyas. Calcula de 20 a 60 minutos, según tu conexión a internet; casi todo el tiempo se va en descargar unos 8 GB.

## Antes de empezar

- Revisa los requisitos en `hardware.md`: una tarjeta gráfica NVIDIA GeForce RTX serie 20 o más reciente con 6 GB de memoria de video, controlador 572.61 o más reciente, Windows 10 22H2 o Windows 11, 16 GB de RAM.
- Deja unos 15 GB libres en la unidad donde pongas la aplicación y en la unidad de tu perfil de usuario.
- Ten lista una clave de API o un servidor local de modelos (consulta `api-keys.md`). También puedes agregarla después.

## Descarga

<a id="download"></a>

Descarga `EnglishTeacher-<versión>.zip` desde la página de versiones (Releases) del proyecto en GitHub. Al lado, `SHA256SUMS.txt` indica su suma de comprobación; para verificarla, abre PowerShell en la carpeta de descargas y compara:

```powershell
Get-FileHash .\EnglishTeacher-0.1.0.zip -Algorithm SHA256
```

## Extracción

<a id="extract"></a>

1. Haz clic derecho en el `.zip` → Propiedades → marca «Desbloquear» → Aceptar. Así evitas advertencias de seguridad para cada script.
2. Extráelo en una carpeta tuya con una ruta corta, por ejemplo `C:\EnglishTeacher` o `Documentos\EnglishTeacher`. Evita `Archivos de programa` (necesita permisos de administrador) y las carpetas sincronizadas con OneDrive.

## Instalación

<a id="install"></a>

Haz doble clic en `install.cmd`. Una ventana de consola muestra cada paso:

1. **Requisitos.** El instalador revisa la tarjeta gráfica, el controlador, la memoria de video, el espacio en disco y la memoria antes de descargar nada. Si falta algo obligatorio, dice qué y se detiene (consulta `hardware.md`).
2. **Carpetas.** Revisa que se pueda escribir en la carpeta de la aplicación y en tu carpeta de datos, y que la ruta sirva.
3. **Herramientas y Python.** Descarga la herramienta `uv` y Python 3.12 dentro de la carpeta de la aplicación. No se agrega nada al sistema ni al `PATH`.
4. **Paquetes.** Unos 5 GB de paquetes de Python (PyTorch con CUDA, bibliotecas de voz), exactamente las versiones de `uv.lock`.
5. **Modelos.** Unos 3,2 GB de modelos de voz en `%LOCALAPPDATA%\VoiceTutor\models`. Si la conexión se corta, vuelve a ejecutar `install.cmd`: la descarga continúa donde se quedó.
6. **Fuentes y detector de voz** para la ventana de la aplicación.
7. **Accesos directos.** Pregunta si quieres accesos directos en el escritorio y en el menú Inicio (Enter significa sí). Siempre se crea uno en la carpeta de la aplicación.

Cada descarga está fijada a una versión exacta y se verifica con una suma de comprobación. Al terminar, Personal AI English Teacher se abre con su asistente de configuración inicial.

## Primer inicio

<a id="first-start"></a>

El asistente te guía en ocho pasos: idioma, revisión del equipo, modelos, una medición corta, micrófono, voz, conexión de API y nivel. Cada paso se puede repetir después desde Configuración → Rendimiento. `usage.md` explica la aplicación.

## Actualización

<a id="update"></a>

Descarga la nueva versión, extráela sobre la carpeta anterior (o en una nueva) y vuelve a ejecutar `install.cmd`. Solo se descarga lo que cambió. Tus sesiones, configuración, claves y modelos se conservan.

## Desinstalación

<a id="uninstall"></a>

Haz doble clic en `uninstall.cmd`. Quita el entorno de Python, las herramientas descargadas y los accesos directos. Pregunta aparte si quieres borrar tus datos (`%LOCALAPPDATA%\VoiceTutor`) y tus claves de API; si no dices que sí, se conservan. Después puedes borrar la carpeta de la aplicación.

## Si algo sale mal

Consulta `troubleshooting.md`. `install.cmd` siempre se puede volver a ejecutar: continúa donde se quedó.
