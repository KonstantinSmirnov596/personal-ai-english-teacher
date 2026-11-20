# Privacidad

Personal AI English Teacher es una aplicación de escritorio sin cuentas, sin estadísticas de uso y sin telemetría. Esta página dice exactamente qué sale de tu computadora, qué se queda en ella y cómo borrarlo.

## Qué sale de la computadora

<a id="llm"></a>
### Mientras practicas

Solo un tipo de tráfico: solicitudes HTTPS a la URL base de tu conexión de API activa (o a `http://127.0.0.1` si usas un servidor local como Ollama). Contienen:

- el texto de la conversación: las líneas del tutor y la transcripción de tus respuestas;
- el escenario y tu nivel, para que el tutor se adapte;
- para correcciones, traducciones, sugerencias y el resumen: las oraciones de las que tratan.

Nunca contienen audio, tu nombre, tu usuario de Windows, datos del equipo ni las claves de tus otras conexiones. Lo que recibe el proveedor queda sujeto a su propia política de privacidad; léela antes de elegir un proveedor, o usa un servidor local.

La aplicación no busca actualizaciones, no envía reportes de fallas y no carga fuentes, scripts ni imágenes desde internet. Una prueba (`tests/gpu/test_network.py`) registra cada conexión que abre la aplicación durante una sesión completa y falla si alguna va a otro lugar que no sea el modelo de lenguaje.

<a id="install"></a>
### Durante la instalación

`install.cmd` descarga, una sola vez: la herramienta `uv` desde su versión publicada en GitHub, Python desde las versiones de `python-build-standalone` en GitHub, los paquetes de Python desde PyPI y el índice de paquetes de PyTorch, los modelos de voz desde Hugging Face, y las fuentes y el detector de voz desde el registro de npm. Cada descarga está fijada a una versión exacta y se verifica con una suma de comprobación. No se envía nada sobre ti más allá de lo que envía cualquier descarga (tu dirección IP).

## Qué se queda en la computadora

<a id="local"></a>

Todo lo demás está en `%LOCALAPPDATA%\VoiceTutor`:

| Qué | Dónde | Cuánto tiempo |
| --- | --- | --- |
| Sesiones, transcripciones, correcciones, vocabulario, resultados de pronunciación, configuración, mediciones del equipo | `voicetutor.db` (SQLite) | Hasta que los borres |
| Grabaciones de tus respuestas | `audio\` | 30 días por defecto (Configuración → Datos; 0 no guarda ninguna) |
| Registro | `logs\` | Como máximo 6 archivos de 2 MB; el más antiguo se reemplaza |
| Modelos de voz | `models\` | Hasta que desinstales |
| Perfil del navegador de la ventana (permiso del micrófono) | `edge-profile\` | Hasta que desinstales |

Las claves de API se guardan en el Administrador de credenciales de Windows con el nombre `VoiceTutor`, nunca en un archivo, en el registro ni en la base de datos. La ventana solo recibe los últimos cuatro caracteres de una clave.

<a id="logs"></a>
### Registro

Por defecto el registro no contiene el texto de tus conversaciones: solo eventos, tiempos y códigos de error. Para un reporte de error puedes activar Configuración → Datos → «Registro detallado», que también escribe el texto de cada turno; la ventana te avisa, y conviene desactivarlo después. `scripts\collect_diagnostics.ps1` reúne versiones, el perfil y el registro para un reporte de error, y quita de ellos las claves y el texto de los turnos.

<a id="server"></a>
### El servidor local

El núcleo de la aplicación solo escucha en `127.0.0.1` (tu propia computadora), en el primer puerto libre entre 47613 y 47622. Solo acepta la ventana de la aplicación: un token de inicio de un solo uso, una cookie de sesión y la revisión de los encabezados `Origin` y `Host` dejan fuera a otros sitios web y programas.

## Cómo borrar tus datos

<a id="delete"></a>

- Configuración → Datos → «Eliminar todos los datos» borra sesiones, correcciones, estadísticas, vocabulario y grabaciones; marca la casilla para borrar también las conexiones de API y sus claves. La configuración se conserva.
- Configuración → Datos → «Exportar todos los datos» guarda todo antes en JSON o CSV, si quieres una copia.
- `uninstall.cmd` quita la aplicación, su entorno de Python y los accesos directos; pregunta antes de borrar `%LOCALAPPDATA%\VoiceTutor` y tus claves.
