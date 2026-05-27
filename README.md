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

El archivo admite dos tipos de líneas:

1. **Línea de conexión** (3 campos separados por coma):

   ```
   origen,destino,minutos
   ```

2. **Línea de estación aislada** (1 único campo, sin comas):

   ```
   estacion
   ```

   Sirve para conservar estaciones que todavía no tienen ninguna conexión.
   Sin esta línea, una estación aislada se perdería al guardar y recargar.

Ejemplo combinado:

```
Atocha,Sol,5
Sol,Gran Via,3
EstacionSinConexiones
```

Las líneas vacías o que empiecen por `#` se ignoran. Como el grafo es no
dirigido, cada conexión se guarda **una sola vez** aunque se cargue en ambos
sentidos en memoria. El formato es compatible con archivos antiguos que solo
contienen líneas de conexión.

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

- Comprobar si una estación existe en **O(1)**.
- Acceder al diccionario de conexiones de una estación concreta también en
  **O(1)** (es solo una búsqueda por clave).
- **Recorrer** todas las conexiones de esa estación cuesta **O(k)**, donde *k*
  es el número de vecinos de la estación, no el total de estaciones del grafo.

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
| Mostrar conexiones de una estación | **O(k)** | *k* es el número de vecinos directos de esa estación. El acceso a su diccionario es O(1), pero recorrerlo es O(k). |
| Mostrar todas las estaciones | **O(V log V)** | Por el `sorted()` que ordena los nombres antes de mostrarlos. |
| Dijkstra | **O((V + E) log V)** | Es la complejidad habitual usando `heapq`; aunque una misma estación pueda insertarse varias veces en el heap, cada operación cuesta O(log V) y el número total de inserciones está acotado por E. |
| BFS (existe camino) | **O(V + E)** | En el peor caso visita todas las estaciones y recorre todas las conexiones una vez. |
| Cargar la red desde archivo | **O(E)** | Se procesa una línea por cada conexión y cada inserción es O(1). |
| Guardar la red en archivo | **O(V + E)** | El coste principal es recorrer las estaciones y todas sus conexiones, usando un `set` de aristas ya escritas para no duplicar. Si además se ordenan los datos con `sorted()`, se añade un coste logarítmico. |

Sobre **Dijkstra**: el algoritmo selecciona en cada paso la estación no
visitada con menor distancia acumulada. Gracias al heap esa selección es O(log
V), y como en total puede haber hasta E actualizaciones (una por arista), el
coste total es **O((V + E) log V)**. Es muy eficiente para grafos dispersos
como una red de metro real.

### 3. Complejidad espacial

- **Grafo en memoria**: en un grafo no dirigido cada conexión se guarda en
  ambos sentidos, por lo que internamente las listas de vecinos suman 2·E
  entradas. Sumando las V claves del diccionario externo, el coste total se
  simplifica como **O(V + E)**.
- **Dijkstra**: utiliza un diccionario de distancias (O(V)), un diccionario de
  predecesores (O(V)), un conjunto de visitados (O(V)) y un heap que en el peor
  caso puede contener O(E) entradas. Coste total aproximado **O(V + E)**.
- **BFS**: usa un `set` de visitados y una cola, ambos con coste **O(V)** en el
  peor caso.
- **Archivo en disco**: **O(E)**, una línea por conexión.

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

## Bonus

El proyecto incluye tres funcionalidades adicionales que amplían la
clase `RedTransporte` y añaden las opciones **9**, **10** y **11** al menú.

### 1. Estación hub

Una estación **hub** es la que tiene más conexiones directas con otras
estaciones, es decir, la de mayor **grado**. En un grafo no dirigido representado
como lista de adyacencia, el grado de una estación es simplemente:

```python
len(self.grafo[estacion])
```

El método `obtener_estacion_hub()` recorre todas las estaciones, calcula su
grado y devuelve una **lista** con las estaciones empatadas en el grado máximo,
junto con ese grado. Devolver una lista permite reflejar correctamente los
empates (típicos en redes pequeñas).

- **Complejidad temporal**: **O(V)**, porque se recorren todas las estaciones
  una vez para comparar sus grados.
- **Complejidad espacial**: **O(H)**, donde *H* es el número de estaciones
  empatadas como hub. En el peor caso *H* = V, pero normalmente es muy
  pequeño.

### 2. Informe JSON

El método `exportar_informe_json()` guarda un resumen de la red en el archivo
`informe_red.json` usando el módulo estándar `json` con `indent=4` y
`ensure_ascii=False` para que sea legible y conserve los acentos.

Datos exportados:

- `numero_estaciones`: total de nodos del grafo, calculado como `len(self.grafo)`.
- `numero_conexiones`: total de aristas. Como el grafo es no dirigido y cada
  conexión se guarda internamente en los dos sentidos, hay que **dividir entre
  2** para no contarlas dos veces:

  ```python
  sum(len(vecinos) for vecinos in self.grafo.values()) // 2
  ```

- `estaciones_hub`: lista con las estaciones de mayor grado.
- `grado_hub`: número de conexiones directas del hub.

La escritura está protegida con `try/except OSError` para informar al usuario si
no se puede crear el archivo.

- **Complejidad temporal**: **O(V + E)**, porque se recorren las estaciones y
  todas sus conexiones para contarlas y para detectar el hub.
- **Complejidad espacial**: **O(V)** como máximo (un diccionario con la
  información del informe), aunque en la práctica el contenido es muy pequeño.

### 3. Ruta más rápida pasando por una estación intermedia

El método `dijkstra_con_intermedia(origen, intermedia, destino)` calcula la ruta
más rápida que **obligatoriamente** debe pasar por una estación intermedia.

La idea es reutilizar el Dijkstra ya implementado y dividir el problema en dos
tramos:

1. `dijkstra(origen, intermedia)` → ruta1, t1
2. `dijkstra(intermedia, destino)` → ruta2, t2

Si los dos tramos existen, se unen evitando duplicar la estación intermedia:

```python
ruta_completa = ruta1 + ruta2[1:]
tiempo_total = t1 + t2
```

Si alguno de los dos tramos no tiene ruta, se avisa al usuario de que no existe
camino completo pasando por esa intermedia. También se validan los tres nombres
antes de ejecutar nada.

Para que esto funcione, el método `dijkstra` devuelve una tupla
`(ruta, distancia)` o `(None, None)` si no hay camino, sin perder la salida por
pantalla que ya usaba la opción 5 del menú.

- **Complejidad temporal**: **O(2 · (V + E) log V)**, que se simplifica como
  **O((V + E) log V)** porque la constante 2 desaparece en notación O grande.
- **Complejidad espacial**: **O(V + E)**, igual que Dijkstra normal, ya que se
  usan las mismas estructuras auxiliares (distancias, predecesores, heap).

### Opciones añadidas al menú

```
 9. Mostrar estacion hub
10. Exportar informe JSON de la red
11. Calcular ruta mas rapida pasando por estacion intermedia
```

### Ejemplo de `informe_red.json`

```json
{
    "numero_estaciones": 11,
    "numero_conexiones": 12,
    "estaciones_hub": [
        "Gran Via",
        "Retiro",
        "Sol"
    ],
    "grado_hub": 3
}
```
