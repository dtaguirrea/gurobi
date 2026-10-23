# Entrega 3 del proyecto del curso ICS1113 Optimización
## Aspectos formales
### Integrantes
Daniel Tomás Aguirre Araya - 23640812 - Sección 5
Catalina Ignacia Casas Escobar - 24200581 - Sección 3
Raúl Ignacio Elgueta Herrera - 23200510 - Sección 5
Gonzalo Andrés Moraga Monsalve - 23642025 - Sección 3
Javier Ignacio Muñoz Andrade - 23641851 - Sección 3
Andrés Enrique Poblete Troncoso - 23644397 - Sección 3
Marianna Valentina Sanguinetti Durán - 23646896 - Sección 5
### Fecha de entrega
23 de octubre 2026

## Ejecución
__Todos los comandos se toman cómo referencia en la consola ubicándose en la raíz del proyecto (NO EN LA CARPETA DE "Script Python")__

1. __Creación Venv__: Recomendamos hacer un ´virtual environment´ de python3.11 para la ejecución del proyecto, para esto, ejecutar el siguiente comando (reemplazando ´python3.11´ por su comando respectivo)
~~~cmd
python3.11 -m venv .venv
~~~

2. __Instalar dependencias__: Para instalar las dependencias de este proyecto, se proporciona un archivo ´requirements.txt´. Así, la instalación se hace con el siguiente comando:
~~~cmd
pip install -r requirements.txt
~~~

3. __Correr el modelo__: Para correr el modelo, es necesario estar ubicado en la raíz del proyecto y correr
~~~cmd
python "Script Python"/main.py
~~~
en Linux, o
~~~cmd
"Script Python"\main.py
~~~
en Windows.
Se recomienda usar el autocompletado con tab para mayor facilidad.

## Estructura
- Los parámetros se encuentran definidos en la carpeta ´Instancias Excel´ en el archivo ´datos-opti-E3.xlsx´
- Los valores de las variables se encuentran en la carpeta "Análisis de Excels" en el archivo ´variables.xlsx´
### Archivos python
- ´load_data.py´: Se encarga de cargar los parámetros definidos en el excel cómo variables (y definir sus conjuntos respectivos). Además se realizan validaciones
- 'graficos.py´: Tiene 2 funciones: Una para cargar las variables desde un archivo xlsx y la otra para generar los datos respectivos.
- ´main.py´: Se cargan los datos con el módulo ´load_data.py', define el modelo, se resuelve, se exporta a un excel y se guardan los gráficos con la función definida en ´graficos.py´