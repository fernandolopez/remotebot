remotebot
=========

Remote control for duinobot

http://wiki.labmovil.linti.unlp.edu.ar/index.php?title=RemoteBot:_Android_%2B_Robots

## Descripción

RemoteBot es una aplicación cliente servidor para controlar los robots del proyecto "Aprendiendo a programar con Python y robots" [1] utilizando dispositivos Android como controles remotos. El proyecto proporciona además un wrapper completo en Java del módulo Python que controla el robot de forma que el código en Java es reutilizable y fácilmente extendible para aprovechar las distintas funcionalidades del robot.

## Diseño general

La aplicación consta de 2 componentes, un servidor en Python que accede al robot utilizando el módulo duinobot [2] y un cliente para Android en Java que envía las acciones a efectuar al servidor.

### Protocolo

La comunicación entre el cliente y el servidor es a través de mensajes POST de HTTP por el puerto 8000 y utilizando JSON para codificar los mensajes. Se diseñó un protocolo que permite instanciar los robots, enviarles mensajes y recibir los resultados de ejecutar los métodos correspondientes, el protocolo se adapta sin modificaciones a cualquier extensión que se le pueda hacer a las clases del módulo duinobot (tampoco es necesario modificar código del servidor si se agrega o quita un método, ver más abajo).

En el protocolo se distinguen 3 tipos de mensajes:

1.  Listas de peticiones del cliente (generalmente se traducen en la invocación de un método por petición en el servidor). En el caso de remotebot4Android el cliente típicamente envía de a una petición (listas con un solo elemento).
2.  Respuestas del servidor una lista de valores de retorno, un valor por operación requerida (eventualmente null en caso que el método invocado no retorne nada).
3.  Respuestas del servidor provocadas por una excepción en Python del lado del servidor, estas respuestas contienen el nombre de la excepción y el stacktrace correspondiente y resultan útiles para detectar errores en tiempo de ejecución como por ejemplo intentar conectarse a una placa que no existe por algún error en el cliente.

Las peticiones del cliente se pueden enviar a 3 entidades:

1.  "robot": Permite instanciar robots nuevos y además representa a todos los robots instanciados.
2.  "board": Permite instanciar una placa asociada a determinado dispositivo y además representa a todas las placas ya instanciadas.
3.  "modules": Permite acceder a la parte procedural del módulo duinobot, en especial se utiliza para obtener la lista de placas conectadas con la función boards().

De esta manera una petición debe tener entre sus datos:

*   La entidad destino (obligatoria).
*   La placa destino (opcional).
*   El robot destino (opcional).
*   La operación a ejecutar (obligatoria).
*   Una lista de argumentos para la operación, en caso de no especificar alguno de los últimos argumentos se consideran los argumentos por defecto de las funciones y métodos tal como están definidos en duinobot (obligatoria pero eventualmente vacía).

El siguiente es un ejemplo de un mensaje con 2 peticiones, la primer petición instancia un robot (si no estuviera previamente instanciado) en el servidor y la segunda provoca que se invoque el método Robot.forward(50, 2) en la instancia anteriormente creada:

[{
"target": "robot",
"board": {"device": "/dev/ttyUSB0"},
"id": 1,
"command": "__init__”
},
{
"target": "robot",
"board": {"device": "/dev/ttyUSB0"},
"id": 1,
"command": "forward",
"args": [50, 2]
}]

Por convención la instanciación del robot retornará null, en cuanto al método Robot.forward() el mismo siempre retorna None en Python por lo que retornará también null, así la respuesta del servidor será:

{
"type": "returnvalues",
"values": [null, null]
}

A menos que algo salga mal, en dicho caso se retornará una excepción y es responsabilidad del cliente manejarla de forma adecuada, el servidor no interrumpe su ejecución ante la ocurrencia de estas excepciones. Un mensaje (con los campos abreviados) del servidor indicando una excepción se ve de la siguiente forma:

{
"type": "exception",
"name": "SerialException(u\"could not open port
/dev/ttyUSB0...\"",
"stacktrace": "Traceback (most recent call last):..."
}

### Servidor

Dado que el módulo original que controla los robots está escrito en Python, el servidor también está codificado en ese lenguaje.

El servidor mantiene una colección con cada placa (Board) y una colección con cada robot (Robot) instanciados, estas instancias nunca se liberan durante la ejecución del servidor, sin embargo esto no es necesariamente malo ya que cada instancia puede ser reutilizada por sucesivos clientes y estas colecciones sirven como una suerte de caché.

En el manejo de las peticiones se utiliza reflection para acceder a las funciones, los métodos de los robots y placas. El uso de reflection permite que el servidor siga funcionando sin modificaciones a pesar que se alteren, amplíen o reduzcan los métodos de las clases Robot y Board en el módulo duinobot.

Como se especificó anteriormente el servidor acepta peticiones utilizando el método POST de HTTP, la respuesta a ese POST contendrá los valores de retorno de los métodos invocados o bien un mensaje de excepción si algo falló.

Por conveniencia el servidor también atiende peticiones GET. Cuando el servidor recibe alguna petición GET muestra una interfaz Web con JavaScript para interactuar con el servidor, en la misma se pueden escribir las listas de peticiones en JSON y ver las respuestas del servidor, además se puede alojar en el servidor el APK de remotebot4Android (maneja los MIME-Types necesarios para que el browser de Android los reconozca) para poder instalar la aplicación en el dispositivo cliente de forma sencilla y sin necesidad de subirla a Google Play.

### Cliente

 El cliente en Android contiene un wrapper completo de las clases Board y Robot que puede ser reutilizada sin modificaciones en otros proyectos Android o bien con algunas modificaciones en la clase Board (o agregando el paquete org.json y Apache HTTPComponents al proyecto) puede ser utilizada en aplicaciones Java normales.

El cliente cuenta con una GUI compuesta por 2 activities, la primera permite seleccionar la IP del servidor, el dispositivo que representa la placa (con un Spinner) y el robot al cual conectarse (con un Spinner). En determinadas ocasiones el módulo duinobot retornará una lista vacía de robots encendidos, en esos casos el cliente muestra una lista por defecto con los (supuestos) robots 1 a 6, luego de determinar esos parámetros se pasa a la siguiente activity.

En la segunda activity se encuentran los controles para manejar el robot:

*   Una SeekBar para controlar la velocidad del mismo (de 0 a 100).
*   Una CheckBox para el modo "avanzar sin chocar".
*   Una CheckBox para que se muestren los valores del sensor de obstáculos.
*   Una CheckBox que permite que el robot gire a la mitad de la velocidad marcada con el slide (esto hace el robot mucho más maniobrable).
*   4 botones para mover el robot hacia adelante, atrás, izquierda y derecha.
*   1 botón para detener el robot.
*   Una CheckBox que habilita el uso de los acelerómetros para controlar el robot, cuando se habilita se puede mover el robot simplemente inclinando el celular en la dirección deseada, el nivel de inclinación determina la velocidad (se ignora la velocidad indicada en la SeekBar).

Los movimientos en la GUI se hacen de forma asincrónica y no se espera la respuesta del servidor (incluso se ignoran algunos errores) todo esto es para que la interfaz restiponda de forma rápida y se ignoren problemas de conexión intermitentes, naturales en las conexiones inalámbricas, que de otra forma resultan muy molestos.

### Wrapper

El cliente incluye un wrapper completo en Java del módulo duinobot creado especialmente para la aplicación pero que fácilmente se puede adaptar para utilizar en otras aplicaciones Java, a continuación se muestra un ejemplo lado a lado de un script en Python con duinobot y su equivalente en Java utilizando esta API:

![Remotebot y duinobot lado a lado](http://imageshack.us/a/img13/9748/remotebotyduinobotladoa.png)

## Arquitectura

### Diagrama de subsistemas

(los componentes en recuadros verdes son los desarrollados para este trabajo práctico)

![Diagrama de subsistemas](http://imageshack.us/a/img6/1617/diagramasubsistemas.png)

### Ilustración de una instalación típica

![Ilustración de una instalación típica](http://imageshack.us/a/img689/4617/instalaciontipica.png)

## Screenshots de la aplicación

Cliente Android, configuración de la conexión:

![Pantalla de configuración de remotebot4Android](http://imageshack.us/a/img17/9309/remotebot4androidconfig.png)

Cliente Android, pantalla de control:

![Pantalla de control de remotebot4Android](http://imageshack.us/a/img716/2451/remotebot4androidcontro.png)

Cliente JavaScript empotrado en el servidor (principalmente usado para depurar al mismo):

![Cliente Javascript incluido empotrado en el servidor](http://imageshack.us/a/img221/913/remotebotjavascriptnorm.png)

En la última línea se puede ver que cada None retornado por alguna operación se codifica en JSON como null, y que en el último valor correspondiente al mensaje Robot.getLine() la tupla con los valores (44, 25) se convierte en una lista con esos 2 valores.

## Aspectos de Interés

Si el robot utilizara el protocolo Bluetooth en lugar de ZigBee hubiera sido posible controlarlo directamente desde el dispositivo Android sin la necesidad de hardware extra, sin embargo esto hubiera implicado implementar el protocolo de bajo nivel del robot en Java, en lugar del protocolo de alto nivel utilizado en remotebot que específica directamente que métodos utilizar haciendo referencia a ellos por su nombre. En cambio, como se detalló anteriormente, la aplicación remotebot se comunica con el servidor utilizando HTTP y JSON a través de la red wifi, si bien HTTP y JSON tienen bastante sobrecarga comparados con lo que habría sido la implementación de un protocolo a medida para la aplicación esta elección de protocolos plantea una serie de ventajas:

*   Al codificar los mensajes en texto plano, el protocolo es mucho más fácil de comprender y depurar que un protocolo binario.
*   Cualquier lenguaje cuenta con librerías para implementar clientes HTTP y para codificar/decodificar JSON, facilitando la implementación de wrappers en casi cualquier lenguaje, de hecho el servidor remotebot cuenta con una rudimentaria interfaz en HTML con JavaScript útil para depurar el servidor y aprender el protocolo.
*   El uso de HTTP en teoría habilita la posibilidad de compartir robots a través de Internet entre usuarios geográficamente dispersos, para explotar esta posibilidad hay que considerar la configuración de un servidor de streaming para que el usuario vea el resultado de ejecutar su programa y agregar manejo de sesiones y multiusuario al servidor remotebot para impedir que las acciones de un usuario afecten a las de otros.

## Soluciones a los problemas encontrados durante el desarrollo

El principal problema fue la latencia en la comunicación que en el diseño inicial podía llegar a ser de más de un segundo por mensaje, esto puede no ser mucho para un browser pero para una aplicación interactiva tal demora es inaceptable. Se detectaron puntos que generaban esta latencia tanto en el cliente como en el servidor:

*   En el cliente DefaultHttpClient por defecto utiliza buffering en los mensajes salientes, como los mensajes enviados por el cliente son muy pequeños se acumulaban el en buffer y luego de generar varios mensajes el cliente los enviaba todos juntos. Para solucionar este problema se estableció el parámetro HttpConnectionParams.setTcpNoDelay al instanciar el cliente, conjuntamente se achicó el timeout de la conexión TCP.
*   Del lado del servidor no se enviaba el tamaño de la respuesta en los encabezados HTTP, por ello el cliente se demoraba esperando más datos desde el servidor hasta que expiraba el tiempo de conexión.
*   El servidor enviaba peticiones de DNS reverso para incluir el nombre de dominio de los clientes en los logs, se sobreescribió el método correspondiente para que el servidor no haga peticiones DNS (si es necesario hacer un log, el servidor directamente utilizará la dirección IP del cliente).

En algunos dispositivos (no en todos) enviar un mensaje al servidor cada vez que cambiaban los valores de los sensores producía un volumen tal de mensajes que era inevitable una demora en la transmisión de datos (aún usando SensorManager.SENSOR_DELAY_NORMAL), por lo que se acotó la frecuencia con que se evaluaban los cambios de los sensores a no más de una vez cada 250 milisegundos (teóricamente ese un tiempo de reacción normal de un ser humano a un estímulo visual [3]) en el mismo sentido se ignora cualquier variación en los sensores que implique un cambio de velocidad en el robot menor a 10 (en una escala de 0 a 100) que de todas maneras sería prácticamente imperceptible.

El robot no es sensible a velocidades abajo de 10 y apenas se mueve en velocidades entre 10 y 15, por lo que cualquier valor de los sensores que implique velocidad menor a 15 se traduce en el envío del mensaje stop al robot (a menos que previamente se le hubiera mandado stop).

El envío de mensajes sincrónicos supuso demasiadas demoras en la IGU del cliente, además como los mensajes que mueven al robot tienen un valor de retorno nulo se optó por crear la clase AsyncMoveRobot que sobreescribe los métodos de movimiento del robot y envía los mensajes correspondientes desde un thread separado ignorando errores de conexión y valores de retorno. Los metodos relacionados con los sensores donde obviamente el valor de retorno es importante se heredan de la clase Robot y tienen el comportamiento esperado, para utilizarlos (como no es posible ni deseable utilizar peticiones HTTP sincronicas en el thread principal de la aplicación) se utilizan AsyncTasks como ObstacleViewUpdater y MoveAndDontCrash para ejecutarlos y obtener su valor de retorno.

Como la aplicación puede pausarse en cualquier momento de forma automática es importante detener todos los threads y AsyncTasks y enviar el mensaje stop al robot en Controls.onPause() para no perder el control del robot y no tener threads de la aplicación activos cuando debería estar pausada. De la misma manera cuando vuelva a arrancar la aplicación hay que volver a habilitar las AsyncTasks correspondan como se hace en Controls.onResume().

## Requerimientos de instalación

*   El dispositivo móvil deberá tener al menos Android 2.2 para poder instalar remotebot4Android.
*   Una PC con GNU/Linux (de preferencia con la última versión de Lihuen) y con el módulo de Python duinobot y el servidor instalado y en ejecución.*
*   Al menos un robot Multiplo N6 de RobotGroup[7] configurado para ser utilizado con el módulo de Python duinobot (una versión estándar del N6 no funcionará con duinobot)**

* Instalación del módulo duinobot, del servidor de remotebot y ejecución del servidor en Lihuen 4.01:

<pre>apt-get install robot
git clone git://github.com/fernandolopez/remotebot.git
cd remotebot
python server.py
</pre>

** Los robots Multiplo N6 preparados para ser usados con el módulo duinobot deben tener la siguiente configuración:

*   Un firmware especial basado en firmata que les permite ser controlados con el módulo XBee
*   Un módulo XBee conectado a la placa controladora
*   Un módulo XBee con un conector USB para conectar a la PC servidora
*   Un sensor de distancia "ping" de Parallax
*   2 sensores de línea y/o 2 cuenta vueltas (encoders) en las ruedas

## Recursos utilizados (librerías, documentación, etc...)

Las liberías utilizadas fueron org.json, org.http.client y android.* incluidas por defecto en el SDK de Android.

La documentación utilizada fue principalmente la documentación oficial de Android [4], además de buscar asuntos puntuales en StackOverflow [5] y tomar ejemplos y recetas del sitio vogella.com [6].

[1] http://robots.linti.unlp.edu.ar/index.php?title=El_Proyecto

[2] https://robots.linti.unlp.edu.ar/index.php?title=Instalaci%C3%B3n_de_la_API

[3] http://www.efdeportes.com/efd139/el-factor-tiempo-en-el-gesto-deportivo.htm

[4] http://developer.android.com

[5] http://stackoverflow.com/questions/tagged/android

[6] http://www.vogella.com/android.html

[7] [http://www.robotgroup.com.ar/](http://www.robotgroup.com.ar/)
