# Proyecto Final Business Intelligence

El proyecto final tiene como objetivo aplicar los conocimientos adquiridos a lo largo del curso para analizar datos reales y proponer una solución de valor para un negocio.

## Requisitos del Proyecto

* Propuesta de negocio: Formular una hipótesis o propuesta que represente una oportunidad o mejora en un sector específico.
* EDA (Análisis Exploratorio de Datos): Mostrar cómo están organizados y distribuidos los datos.
* Metodología de Ciencia de Datos: Aplicar al menos una técnica entre:
	* Aprendizaje Supervisado
	* Aprendizaje No Supervisado
	* Procesamiento de Lenguaje Natural (NLP)
	* Análisis de Imágenes
* Visualización y narrativa: Incorporar elementos visuales y storytelling para comunicar hallazgos.

## Requerimientos

* Se requiere Python (solo se ha testeado con 3.13) y Pip.
* https://business.yelp.com/data/resources/open-dataset/
* Se requiere GNU Make
* Se requiere SQLite3

## Instalación

```
git clone https://github.com/SebasJacome/fl-gyms-bi.git
cd fl-gyms-bi
make
```
* Antes de ejecutar todo el programa, asegúrate de tener las dependencias necesarias. Utiliza el comando `make install` para instalarlas.

## Uso

El proyecto se sigue construyendo...

Para correrlo, debes de tener los 4 archivos JSON de la base de datos de Yelp: user, review, business y tip. Estos, deben estar situados en el directorio: ./yelp_json/

Una vez que tengas estos archivos, puedes usar el comando `make` para correrlo por primera vez. Lo que hara un _build_ completo y tomará un poco de tiempo. Después, al usar el comando `make` por segunda ocasión, tardará menos tiempo en hacer el _build_ si detecta que se generó la base de datos de manera **correcta**.

Si deseas limpiar los archivos generados (.db), usa el comando `make clean`. 

## Consideraciones

* La base de datos que se genera pesa 5.8 GB, asegúrate de tener suficiente espacio.
