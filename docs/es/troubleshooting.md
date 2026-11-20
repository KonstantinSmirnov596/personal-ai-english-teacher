# Solución de problemas

La mayoría de los problemas muestran un mensaje en tu idioma en la ventana de la aplicación o en la consola del instalador. Esta página explica los más comunes. Si ninguno corresponde, mira «Cómo reportar un problema» al final.

## Instalación

<a id="install-warning"></a>
### Windows muestra una advertencia de seguridad

La versión publicada no está firmada con un certificado de firma de código, así que Windows puede advertir al abrir `install.cmd` desde un archivo descargado. Antes de extraerlo, haz clic derecho en el `.zip` → Propiedades → marca «Desbloquear» → Aceptar; o elige «Ejecutar» (o «Más información» → «Ejecutar de todas formas») en la advertencia. Los scripts son texto plano: puedes leerlos antes de ejecutarlos.

<a id="install-requirements"></a>
### El instalador se detiene en la revisión de requisitos

Indica qué falta (tarjeta gráfica, controlador, memoria de video, espacio en disco) y enlaza la sección correspondiente de `hardware.md`. En ese momento todavía no se descargó nada. Resuelve el punto y vuelve a ejecutar `install.cmd`.

<a id="install-path"></a>
### El instalador se queja de la carpeta

Extrae el archivo en una carpeta tuya, por ejemplo `C:\EnglishTeacher` o `Documentos\EnglishTeacher`, no en `Archivos de programa` (necesita permisos de administrador) ni en una carpeta sincronizada con OneDrive. Los espacios en la ruta no son problema. Las letras con acento tampoco, si Windows conserva un nombre corto para la carpeta; si el instalador dice lo contrario, elige una ruta sin acentos.

<a id="install-network"></a>
### Una descarga falla o se detiene

Vuelve a ejecutar `install.cmd`: cada paso revisa lo que ya está listo, y los modelos continúan donde se quedaron. Cada archivo se revisa con una suma de comprobación; un archivo dañado se descarga de nuevo. Un proxy o firewall de empresa puede bloquear GitHub, PyPI o Hugging Face; prueba con otra red.

<a id="antivirus"></a>
### Un antivirus eliminó archivos

Algunos antivirus ponen en cuarentena archivos del entorno de Python de la aplicación. Restáuralos, agrega la carpeta de Personal AI English Teacher a las excepciones y vuelve a ejecutar `install.cmd`.

## Al iniciar la aplicación

<a id="window"></a>
### La ventana no se abre

La aplicación usa Microsoft Edge como ventana. Si se quitó Edge, vuelve a instalarlo desde microsoft.com/edge. Si abres la aplicación cuando ya está abierta, pasa al frente la ventana que ya existe en lugar de abrir una segunda copia.

<a id="problems"></a>
### «La conversación no está disponible»

| Mensaje | Qué hacer |
| --- | --- |
| La computadora no cumple los requisitos mínimos | Mira el paso de revisión del equipo del asistente (botón «Ver detalles») y `hardware.md` |
| No hay una tarjeta gráfica NVIDIA compatible | Instala o actualiza el controlador de NVIDIA y reinicia la computadora y la aplicación |
| No se encontraron los modelos | Vuelve a ejecutar `install.cmd`; luego abre el paso de modelos del asistente y haz clic en «Revisar otra vez» |
| No se pudieron cargar los modelos | Reinicia la computadora; si se repite, vuelve a ejecutar `install.cmd` y reporta el problema con el archivo de diagnóstico |

## Micrófono y sonido

<a id="microphone"></a>
### El tutor no me escucha

1. Windows: Configuración → Privacidad y seguridad → Micrófono: activa «Acceso al micrófono» y «Permitir que las aplicaciones de escritorio accedan al micrófono».
2. En la ventana de la aplicación: haz clic en el ícono del candado junto a la dirección y permite el micrófono.
3. Configuración → Audio y voz: elige el micrófono correcto. El paso de micrófono del asistente (Configuración → Rendimiento → «Volver a ejecutar el asistente») mide el nivel y el ruido de la habitación.

<a id="sound"></a>
### No escucho al tutor

Configuración → Audio y voz → bocinas o audífonos; haz clic en «Escuchar» para probar. Revisa el mezclador de volumen de Windows.

<a id="auto-mode"></a>
### El modo automático envía mi respuesta antes de tiempo o no la envía

Configuración → Conversación → aumenta la pausa permitida. En una habitación ruidosa, repite el paso de micrófono del asistente: hace más estricto el detector de voz. Con bocinas, usa el modo manual o audífonos; si no, el micrófono escucha al tutor.

## Velocidad y memoria

<a id="slow"></a>
### Las respuestas tardan

- Con batería, la laptop baja la velocidad de la tarjeta gráfica: conecta el cargador.
- Los juegos, editores de video y otros programas que usan la tarjeta gráfica ocupan su memoria: ciérralos. Configuración → Rendimiento → `compacto` usa menos memoria de video.
- La velocidad del modelo de lenguaje depende del proveedor y del modelo: Configuración → Conexiones de API → «Probar» muestra el tiempo de una solicitud.

<a id="vram"></a>
### «No hay suficiente memoria de video»

Cierra los programas que usan la tarjeta gráfica y repite la respuesta. Si pasa seguido, elige `compacto` en Configuración → Rendimiento. Consulta `hardware.md`.

## El modelo de lenguaje

<a id="llm"></a>

Los mensajes sobre claves, saldo, esperas o proveedores que no responden se explican en `api-keys.md` («Cuando algo sale mal»).

## Cómo reportar un problema

<a id="report"></a>

1. Ejecuta `scripts\collect_diagnostics.ps1` (clic derecho → Ejecutar con PowerShell). Crea un archivo con las versiones, el perfil del equipo y el registro, sin claves y sin el texto de tus conversaciones.
2. Describe qué hiciste, qué esperabas y qué pasó, y adjunta el archivo.

El registro está en `%LOCALAPPDATA%\VoiceTutor\logs`. Nunca publiques una clave de API.

## Actualizar y reinstalar

<a id="update"></a>

Extrae la nueva versión sobre la carpeta anterior (o en una nueva) y ejecuta `install.cmd`. Tus sesiones, configuración, claves y modelos se quedan en `%LOCALAPPDATA%\VoiceTutor` y en el Administrador de credenciales de Windows. `uninstall.cmd` quita la aplicación y pregunta antes de borrar tus datos.
