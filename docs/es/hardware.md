# Requisitos de hardware

Personal AI English Teacher reconoce tu voz, habla como tutor y revisa tu pronunciación en tu propia computadora, con tu tarjeta gráfica NVIDIA. El audio nunca sale de la computadora. Esta página explica cada punto que revisan el instalador (`install.cmd`) y el asistente de configuración inicial, y qué hacer cuando alguno no se cumple.

## Mínimo y recomendado

| Componente | Mínimo | Recomendado |
| --- | --- | --- |
| Windows | Windows 10 22H2 (compilación 19045) o Windows 11, de 64 bits | Windows 11 |
| Tarjeta gráfica | NVIDIA, arquitectura Turing o más reciente (GeForce RTX serie 20 y posteriores), 6 GB de memoria de video | NVIDIA con 8 GB o más |
| Controlador de NVIDIA | 572.61 o más reciente | El controlador estable más reciente |
| Memoria (RAM) | 16 GB | 16 GB o más |
| Disco | 15 GB libres para la instalación, en un SSD | 20 GB libres |
| Micrófono | Cualquiera | Diadema o audífonos |
| Red | Para la instalación y para el modelo de lenguaje | — |

El instalador se detiene antes de descargar nada cuando falta un punto obligatorio, y dice cuál. El asistente muestra los mismos puntos en su segundo paso, con la memoria de video libre medida en ese momento.

## Qué significa cada punto

<a id="gpu"></a>
### Tarjeta gráfica

El reconocimiento de voz (Whisper), la voz del tutor (Kokoro) y la revisión de pronunciación (wav2vec2) funcionan en una tarjeta gráfica NVIDIA con CUDA. Una computadora que solo tiene gráficos Intel o AMD no puede ejecutarlos. Si tu computadora tiene dos tarjetas gráficas (una laptop con Intel y NVIDIA), asegúrate de que el controlador de NVIDIA esté instalado: la revisión usa la primera tarjeta NVIDIA que encuentra.

<a id="driver"></a>
### Controlador de NVIDIA

La aplicación usa CUDA 12.8 Update 1, que necesita el controlador 572.61 o más reciente ([notas de la versión de CUDA, "Corresponding Driver Versions"](https://docs.nvidia.com/cuda/cuda-toolkit-release-notes/index.html)). Actualiza el controlador desde [nvidia.com/drivers](https://www.nvidia.com/drivers) o la aplicación NVIDIA, reinicia la computadora y vuelve a ejecutar el instalador. Si la revisión dice que falta el controlador, Windows está usando un controlador de pantalla genérico: instala el de NVIDIA.

<a id="architecture"></a>
### Arquitectura de la tarjeta

Las bibliotecas de CUDA que usa la aplicación tienen código para la capacidad de cómputo 7.5 (Turing) y posteriores. La GeForce RTX serie 20 (por ejemplo, la RTX 2060) es la generación más antigua confirmada. Las tarjetas anteriores (GTX serie 10, capacidad de cómputo 6.1) no son compatibles. La revisión lee la capacidad de cómputo desde el controlador, así que no necesitas buscar tu modelo.

<a id="vram"></a>
### Memoria de video

El instalador y la aplicación necesitan una tarjeta con unos 6 GB de memoria de video. El asistente mide la memoria de video *libre*, porque el escritorio de Windows, los navegadores y los juegos usan una parte:

- 7 GB libres o más: perfil `completo`;
- de 5 a 7 GB libres: perfil `compacto`;
- menos de 5 GB libres en una tarjeta que por lo demás sirve: cierra juegos, editores de video y otros programas que usen la tarjeta gráfica y haz clic en «Revisar otra vez». Si continúas, la aplicación usa `compacto`.

En la computadora de desarrollo (tarjeta de 8 GB) la aplicación usó como máximo 3,7 GB en `completo` y 2,5 GB en `compacto` durante una sesión completa.

<a id="ram"></a>
### Memoria (RAM)

Con menos de 16 GB la aplicación funciona, pero cargar los modelos y la ventana junto con otros programas puede hacerla lenta. Es un aviso, no impide la instalación.

<a id="disk"></a>
### Espacio en disco

La instalación necesita unos 15 GB: el entorno de Python (unos 5 GB), los modelos (unos 3,2 GB) y la caché de paquetes (unos 5 GB). Mientras la aplicación funciona, las grabaciones, el registro y la base de datos necesitan espacio: deja al menos 2 GB libres.

<a id="power"></a>
### Alimentación

Con batería, una laptop baja la velocidad de la tarjeta gráfica para ahorrar energía, y el tutor responde más tarde. La aplicación lo avisa una vez; conecta el cargador para tener la mejor velocidad.

<a id="windows"></a>
### Versión de Windows

La aplicación se prueba en Windows 10 22H2 y Windows 11. Una compilación anterior solo genera un aviso; si algo no funciona, primero actualiza Windows.

## Perfiles

<a id="profiles"></a>

| Perfil | Cuándo | Reconocimiento de voz | Modelo de pronunciación |
| --- | --- | --- | --- |
| `completo` | 7 GB de memoria de video libres o más | Whisper turbo, `float16` | Se queda en memoria una vez cargado; las marcas de pronunciación en la conversación están activadas |
| `compacto` | De 5 a 7 GB libres | Whisper turbo, `int8_float16` (menos memoria, la misma precisión en nuestras pruebas) | Se carga cuando «Lectura» o una revisión lo necesita y se descarga después de 5 minutos sin uso; las marcas de pronunciación en la conversación vienen desactivadas |

El paso de medición del asistente (alrededor de un minuto) confirma el perfil. `completo` baja a `compacto` cuando el tiempo desde el final de tu respuesta hasta el primer sonido del tutor (sin contar el modelo de lenguaje) pasa de 1,2 s, o cuando después de cargar los modelos quedan menos de 0,8 GB de memoria de video libre.

Para elegir el perfil tú mismo, abre Configuración → Rendimiento. «Automático» sigue la medición. Esa página también muestra la última medición y permite volver a ejecutar el asistente.

## Cuando falta memoria de video

Si abres un juego u otro programa que use la tarjeta gráfica mientras practicas:

- la aplicación primero libera el modelo de pronunciación;
- si al reconocimiento de voz todavía le falta memoria, la aplicación lo dice y te pide cerrar otros programas; no se cierra;
- los controladores recientes de NVIDIA en Windows también pueden usar la memoria del sistema cuando la memoria de video está llena ([NVIDIA: uso de la memoria del sistema](https://nvidia.custhelp.com/app/answers/detail/a_id/5490/~/system-memory-fallback-for-stable-diffusion), en inglés). Todo sigue funcionando, solo más lento.

Cuando cambia la tarjeta gráfica o su controlador, la aplicación propone repetir la revisión del equipo y la medición en el siguiente inicio.
