# Claves de API y proveedores

Las respuestas del tutor, las correcciones, las traducciones y el resumen de la sesión vienen de un modelo de lenguaje grande (LLM) de un proveedor que tú eliges. Personal AI English Teacher le envía solo el texto de la conversación: nunca el audio, nunca tu nombre. Le pagas directamente al proveedor; Personal AI English Teacher no tiene cuentas ni cobros propios.

## Cómo elegir un proveedor

La ventana de conexiones trae plantillas listas. Cada valor se revisó en la documentación del proveedor (`docs/reports/providers.md`).

| Plantilla | Tipo | Clave | Notas |
| --- | --- | --- | --- |
| DeepSeek | Nube | Obligatoria | Saldo prepagado |
| OpenAI | Nube | Obligatoria | Límites de gasto por proyecto |
| OpenRouter | Nube | Obligatoria | Una clave para modelos de muchas empresas; escribes el nombre del modelo (`empresa/modelo`) |
| Ollama | Local | No hace falta | Funciona en tu computadora; comparte la tarjeta gráfica con el reconocimiento de voz (ver abajo) |
| LM Studio | Local | No hace falta | Funciona en tu computadora; la misma advertencia que Ollama |
| Otra compatible con OpenAI | Cualquiera | Casi siempre | Cualquier servicio con un endpoint `chat/completions` compatible con OpenAI |

## Cómo crear una clave con límite de gasto

Crea una clave aparte solo para Personal AI English Teacher y ponle un límite, para que un error nunca cueste más de lo que decidiste.

<a id="deepseek"></a>
### DeepSeek

1. Inicia sesión en [platform.deepseek.com](https://platform.deepseek.com), abre «API keys» y crea una clave ([DeepSeek: primera llamada a la API](https://api-docs.deepseek.com/), en inglés).
2. Recarga un monto pequeño. DeepSeek funciona con saldo prepagado: el uso se descuenta del saldo y, cuando se acaba, el proveedor responde «saldo insuficiente» (HTTP 402) en lugar de cobrar más ([códigos de error](https://api-docs.deepseek.com/quick_start/error_codes), en inglés). El propio saldo es tu límite.

<a id="openai"></a>
### OpenAI

1. En la plataforma de OpenAI, crea un proyecto para Personal AI English Teacher y dentro de ese proyecto crea una clave secreta ([administrar proyectos](https://help.openai.com/en/articles/9186755-managing-projects-in-the-api-platform), en inglés).
2. Define un límite de gasto mensual para el proyecto y activa «Enforce a hard limit»: así las solicitudes fallan cuando se alcanza el límite, en lugar de solo enviar un aviso ([límites de gasto](https://developers.openai.com/api/docs/guides/spend-limits), en inglés).

<a id="openrouter"></a>
### OpenRouter

1. Crea una clave en el panel de OpenRouter y ponle un límite de crédito, que puede reiniciarse cada día, semana o mes ([limitar claves](https://openrouter.ai/docs/guides/best-practices/capping-shared-agent-keys), en inglés).
2. Elige un modelo en OpenRouter y escribe su identificador (por ejemplo, `empresa/nombre-del-modelo`) en el campo «Modelo» de la conexión.

<a id="local"></a>
### Ollama y LM Studio

Los servidores locales no necesitan clave y no envían nada a internet. Pero un modelo de lenguaje en tu propia tarjeta gráfica compite por la memoria de video con el reconocimiento de voz, la voz del tutor y la revisión de pronunciación. Con 6 a 8 GB solo cabe un modelo pequeño, y la calidad de las correcciones baja. Si lo pruebas, elige el perfil `compacto` en Configuración → Rendimiento y un modelo pequeño.

## Cómo agregar la clave en la aplicación

1. Abre Configuración → Conexiones de API → Agregar conexión (el asistente de configuración inicial muestra el mismo formulario en el paso 7).
2. Elige la plantilla, pega la clave en «Clave de API», haz clic en «Guardar» y luego en «Probar». La prueba envía una solicitud corta y muestra cuánto tardó o el error del proveedor.
3. La primera conexión queda activa. Si tienes varias, el botón redondo de la tabla elige la activa; el cambio se aplica desde la siguiente respuesta.

La clave se guarda en el Administrador de credenciales de Windows, no en un archivo. La ventana solo muestra sus últimos cuatro caracteres. Nunca le envíes una clave a nadie, tampoco en un reporte de error.

## Cuánto cuesta una conversación

<a id="cost"></a>

Los proveedores cobran por token. Un token es un pedazo de palabra; DeepSeek, por ejemplo, cuenta unos 0,3 tokens por carácter en inglés ([uso de tokens](https://api-docs.deepseek.com/quick_start/token_usage), en inglés). Cada una de tus respuestas genera dos solicitudes: la respuesta del tutor y la corrección de tu oración (ninguna si las correcciones están desactivadas). El resumen de la sesión es una solicitud más, y cada sugerencia, traducción o «¿Cómo se dice?» es otra.

Medido con el proveedor de prueba (`scripts/token_usage.py`, una sesión de entrevista de trabajo en nivel B1, 10 respuestas de 10 a 15 palabras, correcciones activadas):

| Solicitud | Tokens de entrada | Tokens de salida, como máximo |
| --- | --- | --- |
| Respuesta del tutor | 850 en la primera respuesta, unos 50 más en cada una (1300 en la décima) | 400 |
| Corrección de tu respuesta | unos 1450 | 800 |
| Resumen de la sesión | unos 1000 | 1200 |
| Sugerencia | unos 300 | 600 |
| Una sesión completa de 10 respuestas con una sugerencia | unos 26 000 | casi siempre muy por debajo del máximo |

Costo de una sesión ≈ (tokens de entrada × precio de entrada + tokens de salida × precio de salida), sumado en todas las solicitudes. Los precios cambian seguido; revisa la página de precios de tu proveedor y la página de uso de tu cuenta después de las primeras sesiones.

## Cuando algo sale mal

| Lo que dice la aplicación | Causa habitual | Qué hacer |
| --- | --- | --- |
| El proveedor rechazó la clave o la cuenta no tiene saldo | Clave incorrecta o eliminada, saldo agotado, límite de gasto alcanzado | Revisa la clave y el saldo o el límite en el proveedor |
| El proveedor pide esperar | Demasiadas solicitudes por minuto | Espera un minuto; el botón «Reintentar» repite la respuesta |
| No se puede contactar al proveedor | Sin internet, firewall, URL base incorrecta | Revisa la conexión; para servidores locales, revisa que Ollama o LM Studio estén abiertos |
| El proveedor devolvió un error o una respuesta incompleta | Nombre de modelo incorrecto, el modelo no admite el formato pedido, falla del proveedor | Revisa el nombre del modelo; prueba otro modelo u otro proveedor |
