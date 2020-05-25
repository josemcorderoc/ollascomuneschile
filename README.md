# ollascomuneschile (en desarrollo)

Aplicación web para ver en tiempo real información de las ollas comunes por comuna a partir de datos de Twitter. Busca ser un aporte a la seguridad alimentaria en la pandemia del COVID-19, 2020.

Autor: José Miguel Cordero [jcordero@dcc.uchile.cl](mailto:jcordero@dcc.uchile.cl)

``### ¿Cómo funciona?

Para correr el código, simplemente copia el repositorio y ejecuta "docker-compose up -d --build" en la carpeta principal.
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

### to-do
* Mejorar la clasificación por comuna: identificar calles, números de contacto y otros
* Mapa de visualización para seleccionar comuna
* Integrar el Confluent S3 Sink para respaldar la data raw (actualmente solo se guarda el output procesado)
* Explicitar la creación de los tópicos de Kafka (?) (actualmente los crea automáticamente el producer)