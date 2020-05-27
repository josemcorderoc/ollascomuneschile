# ollascomuneschile (en desarrollo)

Aplicación web para ver en tiempo real información de las ollas comunes por comuna a partir de datos de Twitter. Busca ser un aporte a la seguridad alimentaria en la pandemia del COVID-19, 2020.

Sitio web: [http://ollascomuneschile.cl/](http://ollascomuneschile.cl/)

Autor: José Miguel Cordero [jcordero@dcc.uchile.cl](mailto:jcordero@dcc.uchile.cl)

### ¿Cómo ejecutarlo?

Simplemente copia el repositorio y ejecuta "docker-compose up -d --build" en la carpeta principal 
(se requiere tener Docker Compose instalado).
Debes tener definidas las siguientes variables de entorno con las credenciales de AWS y Twitter API:
* AWS_ACCESS_KEY_ID
* AWS_SECRET_ACCESS_KEY
* CONSUMER_API_KEY
* CONSUMER_API_SECRET_KEY
* ACCESS_TOKEN
* ACCESS_TOKEN_SECRET

La estructura del proyecto se basa en cinco (5) microservicios:
* Zookeeper (requerido para Kafka)
* Apache Kafka: envía los mensajes desde el productor al consumidor 
* Twitter Streamer: recolecta los mensajes de Twitter en tiempo real con tweepy.
* Twitter Processing: procesa los mensajes utilizando Apache Spark (Structured Steaming).
* Dashboard: visualización web con Flask y Plotly.

### Objetivos del diseño
Busco desarrollar un sistema de lectura, procesamiento y distribución de información en base a tres principios:

* Minimalismo: ocupar la menor cantidad de código y de recursos posibles.
* Escalabilidad: que soporte altos volúmenes de datos.
    * actualmente uso el stack big data de Apache (Kafka + Spark), lo que permite una configuración multicluster
    en caso de requerirse.
* Extensibilidad: un software que sea fácil de adaptar para otros propósitos, acrecentar productores/consumidores o
que pueda conectarse con otras herramientas

(lo complicado es compatibilizar los tres)
### to-do
* Cambiar tipo csv a parquet u otro más estable/eficiente
    * Probé grabar parquet con Spark Structured Streaming, pero (por razones desconocidas) los archivos no se
    grababan
* Disminuir el tiempo de refresco al mínimo (objetivo: data actualizada a menos de 15 segundos)
    * Actualmente se escribe a S3 y se lee desde S3. Rediseñando la arquitectura la aplicación web podría recibir
    los mensajes directamente, evitando el delay de lectura y escritura (¿pero cómo respaldamos los datos?)
* Mejorar la clasificación por comuna: identificar calles, números de contacto y otros
* Mapa de visualización para seleccionar comuna + mejorar interfaz de usuario
    * Hay problemas con modo responsive
* Integrar el Confluent S3 Sink para respaldar la data raw (actualmente solo se guarda el output procesado)
* Explicitar la creación de los tópicos de Kafka (?) (actualmente los crea automáticamente el producer)