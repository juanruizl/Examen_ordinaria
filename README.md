# Planificador de Rutas de Transporte

Aplicacion de consola en Python que modela una red de estaciones de transporte
como un **grafo no dirigido y ponderado**, donde cada arista representa el
tiempo de viaje en minutos entre dos estaciones.

El proyecto esta pensado como actividad academica: codigo claro, sin librerias
externas, sin interfaz grafica y sin base de datos.

## Estructura del proyecto

```
.
|-- red_transporte.py    # Codigo principal con la clase RedTransporte y el menu
|-- red_transporte.txt   # Archivo de persistencia con la red de ejemplo
|-- README.md            # Este documento
```

## Requisitos

- Python 3.8 o superior.
- Solo se utilizan modulos de la biblioteca estandar: `heapq` y `os`.

## Como ejecutar

Desde la carpeta del proyecto:

```bash
python3 red_transporte.py
```

Al iniciar, el programa carga automaticamente el archivo `red_transporte.txt`
si existe. Si no existe, comienza con una red vacia.

## Formato del archivo de datos

Cada linea representa una conexion bidireccional con el formato:

```
origen,destino,minutos
```

Ejemplo:

```
Atocha,Sol,5
Sol,Gran Via,3
```

Las lineas vacias o que empiecen por `#` se ignoran. Como el grafo es no
dirigido, cada conexion se guarda **una sola vez** aunque se cargue en ambos
sentidos en memoria.

## Opciones del menu

Al ejecutar el programa veras este menu:

```
==== PLANIFICADOR DE RUTAS DE TRANSPORTE ====
1. Mostrar estaciones
2. Mostrar conexiones de una estacion
3. Anadir estacion
4. Anadir conexion
5. Calcular ruta mas rapida (Dijkstra)
6. Comprobar si existe camino entre dos estaciones
7. Guardar red
8. Salir
```

### 1. Mostrar estaciones
Lista por pantalla todas las estaciones cargadas en la red.

### 2. Mostrar conexiones de una estacion
Pide el nombre de una estacion y muestra sus vecinos directos junto con el
tiempo de viaje. Avisa si la estacion no existe o si no tiene conexiones.

### 3. Anadir estacion
Pide un nombre y crea una estacion nueva. Se valida que el nombre no este vacio
y que no exista ya.

### 4. Anadir conexion
Pide origen, destino y tiempo en minutos. Validaciones:
- Las dos estaciones deben existir previamente.
- El tiempo debe ser un entero positivo.
- No se permite conectar una estacion consigo misma.
- No se permiten conexiones duplicadas.

### 5. Calcular ruta mas rapida (Dijkstra)
Pide origen y destino y aplica el algoritmo de **Dijkstra** usando `heapq`
como cola de prioridad. Muestra la ruta completa y el tiempo total. Si no hay
ruta posible lo indica.

### 6. Comprobar si existe camino entre dos estaciones
Realiza un recorrido **BFS** usando un `set` para los nodos visitados e indica
simplemente si las dos estaciones estan conectadas.

### 7. Guardar red
Sobrescribe el archivo `red_transporte.txt` con el estado actual del grafo.
Evita guardar conexiones duplicadas.

### 8. Salir
Pregunta si quieres guardar los cambios antes de cerrar. Tambien si se
interrumpe con `Ctrl+C` el programa intenta guardar antes de salir.

## Ejemplo de ejecucion

```
[OK] Red cargada desde 'red_transporte.txt'.

==== PLANIFICADOR DE RUTAS DE TRANSPORTE ====
1. Mostrar estaciones
...
8. Salir

Elige una opcion (1-8): 5
Estacion origen: Atocha
Estacion destino: Velazquez
Ruta mas rapida: Atocha -> Retiro -> Principe de Vergara -> Goya -> Velazquez
Tiempo total: 16 minutos
```

```
Elige una opcion (1-8): 3
Nombre de la nueva estacion: Serrano
[OK] Estacion 'Serrano' anadida.

Elige una opcion (1-8): 4
Estacion origen: Velazquez
Estacion destino: Serrano
Tiempo en minutos (entero positivo): 2
[OK] Conexion 'Velazquez' <-> 'Serrano' (2 min) anadida.

Elige una opcion (1-8): 6
Estacion origen: Atocha
Estacion destino: Serrano
Si existe un camino entre 'Atocha' y 'Serrano'.

Elige una opcion (1-8): 8
Deseas guardar los cambios antes de salir? (s/n): s
[OK] Red guardada en 'red_transporte.txt'.
Saliendo del programa. Hasta pronto.
```

## Detalles tecnicos

- **Lista de adyacencia**: diccionario de diccionarios
  `{estacion: {vecina: minutos}}`.
- **Grafo no dirigido**: cada conexion se inserta en ambos sentidos.
- **Dijkstra**: cola de prioridad con `heapq`, distancias inicializadas a
  infinito y reconstruccion de la ruta mediante un diccionario de
  predecesores.
- **BFS**: lista usada como cola y `set` de visitados.
- **Persistencia**: lectura y escritura de texto plano con `try/except` para
  controlar errores de archivo.
- **Validaciones**: nombres no vacios, tiempos enteros positivos, estaciones
  existentes, sin conexiones duplicadas ni a si misma.

## Análisis teórico

Esta sección explica las decisiones técnicas del proyecto y analiza la
eficiencia del programa. Las complejidades se expresan en notación **O grande**,
donde **V** es el número de estaciones (vértices) y **E** es el número de
conexiones (aristas).

### 1. Estructuras de datos utilizadas

**Diccionarios (`dict`)**

El grafo se representa como una **lista de adyacencia** mediante un diccionario
de diccionarios:

```python
{
  "Atocha": {"Sol": 5, "Retiro": 7},
  "Sol":    {"Atocha": 5, "Gran Via": 3}
}
```

- Cada **clave externa** es el nombre de una estación.
- Cada **valor** es otro diccionario donde las claves son las estaciones vecinas
  y los valores son los tiempos de viaje en minutos.

Esta estructura es adecuada porque el acceso a un diccionario por clave es de
**tiempo medio O(1)** gracias a la tabla hash interna de Python. Eso permite:

- Comprobar si una estación existe en O(1).
- Obtener todas las conexiones directas de una estación en O(1) (acceso al
  diccionario interno).
- Recorrer los vecinos de una estación en tiempo proporcional al número de
  vecinos, no al total de estaciones.

Una alternativa habría sido usar una **matriz de adyacencia**, pero ocuparía
O(V²) aunque la red fuera dispersa, mientras que la lista de adyacencia ocupa
solo lo necesario.

**Conjuntos (`set`)**

Se usan en la búsqueda de conectividad (BFS) y dentro de Dijkstra para guardar
las estaciones ya visitadas. Los conjuntos permiten comprobar la pertenencia
(`x in visitados`) en **tiempo medio O(1)**, mucho más rápido que una lista, que
sería O(n). Esto evita visitar dos veces la misma estación y previene bucles
infinitos en grafos cíclicos.

**Heap o cola de prioridad (`heapq`)**

Dijkstra necesita extraer en cada iteración la estación con **menor tiempo
acumulado** desde el origen. Usar una lista normal obligaría a recorrerla entera
en cada paso (O(V)). Con `heapq` (un *min-heap* binario) las operaciones de
inserción y extracción del mínimo cuestan **O(log V)**, lo que mejora mucho la
eficiencia del algoritmo.

Cada elemento del heap es una tupla `(distancia_acumulada, nodo)`, y Python
ordena automáticamente por el primer elemento.

**Archivo de texto**

La red se guarda en `red_transporte.txt` con una línea por conexión:

```
origen,destino,minutos
```

Es un formato sencillo, legible por humanos y fácil de procesar con
`split(",")`. Como el grafo es no dirigido, cada conexión se guarda **una sola
vez** aunque internamente se almacene en ambos sentidos. Así se evita duplicar
información en disco.

### 2. Complejidad temporal

| Operación | Complejidad | Justificación |
|---|---|---|
| Añadir una estación | **O(1)** | Se inserta una nueva clave en el diccionario. |
| Añadir una conexión | **O(1)** | Se comprueba la existencia de las estaciones (O(1)) y se inserta en los dos diccionarios de adyacencia (no dirigido). |
| Mostrar conexiones de una estación | **O(k)** | k es el número de vecinos directos de esa estación. |
| Mostrar todas las estaciones | **O(V log V)** | Por el `sorted()` que ordena los nombres para mostrarlos. |
| Dijkstra | **O((V + E) log V)** | Cada arista puede provocar como mucho una inserción en el heap, y cada operación del heap cuesta O(log V). |
| BFS (existe camino) | **O(V + E)** | En el peor caso visita todas las estaciones y recorre todas las conexiones una vez. |
| Cargar la red desde archivo | **O(E)** | Se procesa una línea por cada conexión y cada inserción es O(1). |
| Guardar la red en archivo | **O(V + E)** | Se recorren todas las estaciones y todas sus conexiones, usando un `set` de aristas ya escritas para no duplicar. El `sorted()` añade un factor logarítmico. |

Sobre **Dijkstra**: el algoritmo selecciona en cada paso la estación no
visitada con menor distancia acumulada. Gracias al heap esa selección es O(log
V), y como en total puede haber hasta E actualizaciones (una por arista), el
coste total es **O((V + E) log V)**. Es muy eficiente para grafos dispersos
como una red de metro real.

### 3. Complejidad espacial

- **Grafo en memoria**: O(V + E). Hay V claves en el diccionario externo y, en
  total, las listas de vecinos suman 2·E entradas porque cada arista se guarda
  en los dos sentidos. Esto se simplifica como **O(V + E)**.
- **Dijkstra**: utiliza un diccionario de distancias (O(V)), un diccionario de
  predecesores (O(V)), un conjunto de visitados (O(V)) y un heap que en el peor
  caso puede contener O(E) entradas. Coste total aproximado **O(V + E)**.
- **BFS**: usa un `set` de visitados y una cola, ambos con coste **O(V)** en el
  peor caso.
- **Archivo en disco**: O(E), una línea por conexión.

### 4. Posibles mejoras

Algunas extensiones razonables para una versión futura del proyecto:

- **Eliminar estaciones y conexiones**, asegurando que se borren también las
  referencias en los diccionarios vecinos.
- **Actualizar el tiempo** de una conexión existente sin tener que borrarla y
  crearla de nuevo.
- **Cambiar el formato de persistencia** a JSON o CSV con cabecera, lo que
  permitiría validaciones más estrictas y mejor compatibilidad con otras
  herramientas.
- **Añadir pruebas unitarias** con el módulo `unittest` para verificar
  automáticamente cada método de la clase `RedTransporte`.
- **Separar el menú de consola de la lógica del grafo** en archivos distintos
  (por ejemplo `red.py` y `main.py`), siguiendo mejor el principio de
  responsabilidad única.
- **Permitir grafos dirigidos o no dirigidos** según una opción de
  configuración, útil si algunas líneas son de sentido único.
- **Añadir más criterios de ruta**, como la ruta con menos transbordos o con el
  menor número de estaciones intermedias.
- **Mejorar los mensajes de error** y la experiencia de usuario, por ejemplo
  con autocompletado de nombres o sugerencias cuando una estación no existe.
- **Añadir documentación más detallada** de cada función con `docstrings` y
  generar documentación automática con herramientas como `pydoc`.
