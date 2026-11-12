# Cómo usar Voice Tutor

Voice Tutor tiene cuatro secciones en la barra superior: Conversación, Lectura, Vocabulario e Historial. La configuración está detrás del ícono de controles a la derecha. La interfaz, las correcciones, las traducciones y los consejos están en tu idioma (español o portugués); el tutor siempre habla inglés estadounidense general.

## Primer inicio

La primera vez se abre un asistente de configuración: idioma, revisión del equipo, modelos, una medición corta, micrófono, voz, conexión de API y nivel. Puedes abrirlo de nuevo cuando quieras desde Configuración → Rendimiento → «Volver a ejecutar el asistente». Consulta `hardware.md` para la revisión del equipo y `api-keys.md` para la conexión.

## Conversación

<a id="conversation"></a>

1. Elige un escenario (una entrevista de trabajo, una charla informal, una reunión…) y tu nivel, y haz clic en «Empezar la conversación». El tutor habla primero.
2. Presiona la **barra espaciadora** para empezar a responder y otra vez para enviar. **Esc** cancela la respuesta. Mientras el tutor habla, la barra espaciadora lo interrumpe.
3. Tu respuesta aparece como texto; el tutor responde en voz alta y por escrito.

Modos de turnos (el interruptor del panel inferior):

- **Manual**: la barra espaciadora empieza y termina cada respuesta. Es lo mejor con bocinas.
- **Automático**: solo habla; tu respuesta se envía después de una pausa (Configuración → Conversación define la pausa). Con bocinas, el micrófono se cierra mientras habla el tutor; con audífonos puedes interrumpirlo con la voz (Configuración → Conversación → «Uso audífonos»).

Debajo de cada línea del tutor: **Repetir**, **Más despacio** y **Traducir**. En el panel inferior: **Sugerencia** (ideas para tu respuesta), **¿Cómo se dice?** (escribe una frase en tu idioma y obtenla en inglés) y **Terminar**.

### Correcciones

Los errores de tu respuesta aparecen subrayados. La tarjeta muestra la corrección, una explicación corta en tu idioma y una forma más natural de decirlo. Elige cuándo aparecen en el panel inferior o en Configuración → Correcciones: al instante, al hacer clic, al final de la sesión o desactivadas. Los errores claros de pronunciación también se marcan en la conversación (en el perfil `compacto` esto viene desactivado; Configuración → Correcciones).

### Resumen

«Terminar» muestra el resumen de la sesión: lo más importante, todas las correcciones, ejercicios cortos de habla a partir de tus errores («Dilo en inglés: …»), los errores que se repiten en varias sesiones, los sonidos para practicar y las frases útiles del tutor, que puedes agregar a tu vocabulario.

## Lectura

<a id="reading"></a>

La lectura revisa tu pronunciación sonido por sonido, sin modelo de lenguaje (funciona sin conexión de API).

1. Si quieres, escucha la frase («Referencia», «Referencia lenta»).
2. Presiona la **barra espaciadora** o el micrófono, lee la frase en voz alta y presiona la **barra espaciadora** otra vez.
3. Las palabras con algún problema quedan marcadas: «impreciso» o «error». Haz clic en una palabra para ver qué sonido se escuchó en lugar de cuál, un consejo en tu idioma y botones para escuchar la palabra y repetir solo esa palabra.
4. Si una marca está mal, haz clic en «Eso estaba bien»: la revisión se vuelve menos estricta con ese sonido.

«Sonidos para practicar» muestra los sonidos que te costaron en los últimos 7 días. Cada frase indica los sonidos que entrena; «Anterior» y «Siguiente frase» recorren las 30 frases.

## Vocabulario

<a id="vocabulary"></a>

Las frases que agregas desde un resumen vuelven para repasarlas cada vez con más espacio. Lee la frase en inglés, piensa en el significado, haz clic en «Mostrar traducción» y luego en «Lo recuerdo» o «No lo recuerdo».

## Historial

<a id="history"></a>

Cada sesión con su transcripción, sus correcciones y su resumen. Puedes abrir, exportar (JSON o CSV) o eliminar una sesión; al eliminarla también se borran sus grabaciones.

## Configuración

<a id="settings"></a>

| Sección | Qué contiene |
| --- | --- |
| Conexiones de API | Tus proveedores y claves; una está activa (`api-keys.md`) |
| Idioma | Español o portugués para la interfaz y las explicaciones, sin reiniciar |
| Audio y voz | Micrófono, bocinas, la voz y la velocidad del tutor, supresión de ruido |
| Conversación | Nivel, modo de turnos, duración de la pausa en modo automático, reformulaciones del tutor, audífonos |
| Correcciones | Cuándo aparecen las correcciones; marcas de pronunciación en la conversación |
| Rendimiento | Perfil (`completo`, `compacto`, automático), última medición, volver a ejecutar el asistente |
| Datos | Cuánto tiempo se guardan las grabaciones, exportar, «Eliminar todos los datos», registro detallado |

## Teclado

| Tecla | Conversación | Lectura |
| --- | --- | --- |
| Barra espaciadora | Empezar, enviar, interrumpir | Empezar y detener la grabación |
| Esc | Cancelar la respuesta | Cancelar la grabación |
