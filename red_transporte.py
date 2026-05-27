"""
Planificador de rutas de transporte basado en grafos ponderados.

La red de estaciones se representa como un grafo no dirigido y ponderado:
    - Cada estacion es un nodo.
    - Cada conexion es una arista con un peso (tiempo en minutos).
    - Se almacena como lista de adyacencia mediante un diccionario de diccionarios.

Ejecucion:
    python3 red_transporte.py
"""

import heapq
import json
import os

ARCHIVO_POR_DEFECTO = "red_transporte.txt"
ARCHIVO_INFORME = "informe_red.json"


class RedTransporte:
    """Modela una red de transporte como un grafo no dirigido ponderado."""

    def __init__(self, archivo=ARCHIVO_POR_DEFECTO):
        self.archivo = archivo
        # Lista de adyacencia: {estacion: {vecina: minutos, ...}, ...}
        self.grafo = {}

    # ------------------------------------------------------------------
    # Persistencia
    # ------------------------------------------------------------------
    def cargar_desde_archivo(self):
        """Carga la red desde el archivo de texto asociado.

        Si el archivo no existe, se inicia con una red vacia.
        Las lineas mal formadas se ignoran avisando al usuario.
        """
        if not os.path.exists(self.archivo):
            print(f"[Aviso] No se encontro '{self.archivo}'. Se inicia con una red vacia.")
            return

        try:
            with open(self.archivo, "r", encoding="utf-8") as f:
                for numero, linea in enumerate(f, start=1):
                    linea = linea.strip()
                    # Saltar lineas vacias o comentarios
                    if not linea or linea.startswith("#"):
                        continue

                    partes = linea.split(",")

                    # Linea con un unico campo: estacion aislada (sin conexiones)
                    if len(partes) == 1:
                        nombre = partes[0].strip()
                        if not nombre:
                            print(f"[Aviso] Linea {numero} ignorada (nombre vacio): {linea}")
                            continue
                        self.grafo.setdefault(nombre, {})
                        continue

                    if len(partes) != 3:
                        print(f"[Aviso] Linea {numero} ignorada (formato invalido): {linea}")
                        continue

                    origen = partes[0].strip()
                    destino = partes[1].strip()
                    try:
                        minutos = int(partes[2].strip())
                    except ValueError:
                        print(f"[Aviso] Linea {numero} ignorada (minutos no es entero): {linea}")
                        continue

                    if not origen or not destino or minutos <= 0 or origen == destino:
                        print(f"[Aviso] Linea {numero} ignorada (datos invalidos): {linea}")
                        continue

                    # Insertar ambos sentidos (grafo no dirigido)
                    self.grafo.setdefault(origen, {})[destino] = minutos
                    self.grafo.setdefault(destino, {})[origen] = minutos

            print(f"[OK] Red cargada desde '{self.archivo}'.")
        except OSError as e:
            print(f"[Error] No se pudo leer el archivo: {e}")

    def guardar_en_archivo(self):
        """Guarda la red en el archivo asociado evitando duplicar aristas.

        Las estaciones sin conexiones se persisten como una linea con solo el
        nombre de la estacion, para que no se pierdan al guardar y recargar.
        """
        try:
            with open(self.archivo, "w", encoding="utf-8") as f:
                escritas = set()
                for origen in sorted(self.grafo):
                    if not self.grafo[origen]:
                        # Estacion aislada: una linea con solo el nombre
                        f.write(f"{origen}\n")
                        continue
                    for destino, minutos in sorted(self.grafo[origen].items()):
                        # Usamos un frozenset para tratar (A,B) y (B,A) como la misma arista
                        clave = frozenset((origen, destino))
                        if clave in escritas:
                            continue
                        escritas.add(clave)
                        f.write(f"{origen},{destino},{minutos}\n")
            print(f"[OK] Red guardada en '{self.archivo}'.")
        except OSError as e:
            print(f"[Error] No se pudo guardar el archivo: {e}")

    # ------------------------------------------------------------------
    # Modificacion de la red
    # ------------------------------------------------------------------
    def agregar_estacion(self, nombre):
        """Anade una estacion nueva si el nombre es valido y no esta repetida."""
        nombre = nombre.strip()
        if not nombre:
            print("[Error] El nombre de la estacion no puede estar vacio.")
            return False
        if nombre in self.grafo:
            print(f"[Error] La estacion '{nombre}' ya existe.")
            return False
        self.grafo[nombre] = {}
        print(f"[OK] Estacion '{nombre}' anadida.")
        return True

    def agregar_conexion(self, origen, destino, minutos):
        """Anade una conexion bidireccional entre dos estaciones existentes."""
        origen = origen.strip()
        destino = destino.strip()

        if origen not in self.grafo:
            print(f"[Error] La estacion de origen '{origen}' no existe.")
            return False
        if destino not in self.grafo:
            print(f"[Error] La estacion de destino '{destino}' no existe.")
            return False
        if origen == destino:
            print("[Error] No se permite conectar una estacion consigo misma.")
            return False
        if not isinstance(minutos, int) or minutos <= 0:
            print("[Error] El tiempo debe ser un numero entero positivo.")
            return False
        if destino in self.grafo[origen]:
            print(f"[Error] Ya existe una conexion entre '{origen}' y '{destino}'.")
            return False

        self.grafo[origen][destino] = minutos
        self.grafo[destino][origen] = minutos
        print(f"[OK] Conexion '{origen}' <-> '{destino}' ({minutos} min) anadida.")
        return True

    # ------------------------------------------------------------------
    # Consultas
    # ------------------------------------------------------------------
    def mostrar_estaciones(self):
        """Muestra por pantalla todas las estaciones de la red."""
        if not self.grafo:
            print("La red no contiene estaciones.")
            return
        print("Estaciones de la red:")
        for estacion in sorted(self.grafo):
            print(f"  - {estacion}")

    def mostrar_conexiones(self, estacion):
        """Muestra las conexiones directas de la estacion indicada."""
        estacion = estacion.strip()
        if estacion not in self.grafo:
            print(f"[Error] La estacion '{estacion}' no existe.")
            return
        vecinas = self.grafo[estacion]
        if not vecinas:
            print(f"La estacion '{estacion}' no tiene conexiones.")
            return
        print(f"Conexiones de '{estacion}':")
        for vecina, minutos in sorted(vecinas.items()):
            print(f"  -> {vecina} ({minutos} min)")

    # ------------------------------------------------------------------
    # Algoritmos
    # ------------------------------------------------------------------
    def dijkstra(self, origen, destino):
        """Calcula la ruta mas rapida entre dos estaciones con Dijkstra.

        Devuelve una tupla (ruta, tiempo_total) o (None, None) si no existe ruta.
        """
        origen = origen.strip()
        destino = destino.strip()

        if origen not in self.grafo:
            print(f"[Error] La estacion de origen '{origen}' no existe.")
            return None, None
        if destino not in self.grafo:
            print(f"[Error] La estacion de destino '{destino}' no existe.")
            return None, None

        # Distancias inicializadas a infinito y predecesores para reconstruir la ruta
        distancias = {nodo: float("inf") for nodo in self.grafo}
        predecesores = {nodo: None for nodo in self.grafo}
        distancias[origen] = 0

        # Cola de prioridad con tuplas (distancia_acumulada, nodo)
        cola = [(0, origen)]
        visitados = set()

        while cola:
            dist_actual, nodo = heapq.heappop(cola)
            if nodo in visitados:
                continue
            visitados.add(nodo)

            # Salida temprana al llegar al destino
            if nodo == destino:
                break

            for vecina, peso in self.grafo[nodo].items():
                if vecina in visitados:
                    continue
                nueva_dist = dist_actual + peso
                if nueva_dist < distancias[vecina]:
                    distancias[vecina] = nueva_dist
                    predecesores[vecina] = nodo
                    heapq.heappush(cola, (nueva_dist, vecina))

        if distancias[destino] == float("inf"):
            return None, None

        # Reconstruir la ruta desde destino hasta origen
        ruta = []
        actual = destino
        while actual is not None:
            ruta.append(actual)
            actual = predecesores[actual]
        ruta.reverse()
        return ruta, distancias[destino]

    def existe_camino(self, origen, destino):
        """Indica si existe algun camino entre origen y destino mediante BFS."""
        origen = origen.strip()
        destino = destino.strip()

        if origen not in self.grafo:
            print(f"[Error] La estacion de origen '{origen}' no existe.")
            return False
        if destino not in self.grafo:
            print(f"[Error] La estacion de destino '{destino}' no existe.")
            return False

        visitados = set()
        cola = [origen]
        while cola:
            actual = cola.pop(0)
            if actual == destino:
                return True
            if actual in visitados:
                continue
            visitados.add(actual)
            for vecina in self.grafo[actual]:
                if vecina not in visitados:
                    cola.append(vecina)
        return False

    # ------------------------------------------------------------------
    # Funcionalidades bonus
    # ------------------------------------------------------------------
    def obtener_estacion_hub(self):
        """Devuelve las estaciones con mayor grado y ese grado maximo.

        Como puede haber empates, se devuelve una lista de nombres ordenada.
        Si la red esta vacia se devuelve ([], 0).
        """
        if not self.grafo:
            return [], 0
        max_grado = max(len(vecinos) for vecinos in self.grafo.values())
        hubs = sorted(
            estacion for estacion, vecinos in self.grafo.items()
            if len(vecinos) == max_grado
        )
        return hubs, max_grado

    def exportar_informe_json(self, archivo=ARCHIVO_INFORME):
        """Exporta un informe resumen de la red en formato JSON."""
        if not self.grafo:
            print("[Error] La red esta vacia, no se puede exportar el informe.")
            return False

        hubs, grado = self.obtener_estacion_hub()
        # Cada conexion esta guardada en ambos sentidos, por eso dividimos entre 2
        numero_conexiones = sum(len(v) for v in self.grafo.values()) // 2

        datos = {
            "numero_estaciones": len(self.grafo),
            "numero_conexiones": numero_conexiones,
            "estaciones_hub": hubs,
            "grado_hub": grado,
        }

        try:
            with open(archivo, "w", encoding="utf-8") as f:
                json.dump(datos, f, indent=4, ensure_ascii=False)
            print(f"[OK] Informe exportado a '{archivo}'.")
            return True
        except OSError as e:
            print(f"[Error] No se pudo escribir el informe: {e}")
            return False

    def dijkstra_con_intermedia(self, origen, intermedia, destino):
        """Calcula la ruta mas rapida origen -> intermedia -> destino.

        Reutiliza el metodo dijkstra existente en dos tramos. Devuelve la
        tupla (ruta_completa, tiempo_total) o (None, None) si alguno de los
        dos tramos no tiene ruta.
        """
        origen = origen.strip()
        intermedia = intermedia.strip()
        destino = destino.strip()

        for nombre in (origen, intermedia, destino):
            if not nombre:
                print("[Error] Los nombres de las estaciones no pueden estar vacios.")
                return None, None
            if nombre not in self.grafo:
                print(f"[Error] La estacion '{nombre}' no existe.")
                return None, None

        ruta1, t1 = self.dijkstra(origen, intermedia)
        if ruta1 is None:
            print(f"No existe ruta entre '{origen}' y la intermedia '{intermedia}'.")
            return None, None

        ruta2, t2 = self.dijkstra(intermedia, destino)
        if ruta2 is None:
            print(f"No existe ruta entre la intermedia '{intermedia}' y '{destino}'.")
            return None, None

        # Unir las dos rutas evitando duplicar la estacion intermedia
        ruta_completa = ruta1 + ruta2[1:]
        return ruta_completa, t1 + t2

    # ------------------------------------------------------------------
    # Menu interactivo
    # ------------------------------------------------------------------
    def menu(self):
        """Bucle principal del menu de consola."""
        opciones = (
            "\n==== PLANIFICADOR DE RUTAS DE TRANSPORTE ====\n"
            " 1. Mostrar estaciones\n"
            " 2. Mostrar conexiones de una estacion\n"
            " 3. Anadir estacion\n"
            " 4. Anadir conexion\n"
            " 5. Calcular ruta mas rapida (Dijkstra)\n"
            " 6. Comprobar si existe camino entre dos estaciones\n"
            " 7. Guardar red\n"
            " 8. Salir\n"
            " 9. Mostrar estacion hub\n"
            "10. Exportar informe JSON de la red\n"
            "11. Calcular ruta mas rapida pasando por estacion intermedia\n"
        )

        while True:
            print(opciones)
            opcion = input("Elige una opcion (1-11): ").strip()

            if opcion == "1":
                self.mostrar_estaciones()

            elif opcion == "2":
                estacion = input("Nombre de la estacion: ")
                self.mostrar_conexiones(estacion)

            elif opcion == "3":
                nombre = input("Nombre de la nueva estacion: ")
                self.agregar_estacion(nombre)

            elif opcion == "4":
                origen = input("Estacion origen: ")
                destino = input("Estacion destino: ")
                tiempo_txt = input("Tiempo en minutos (entero positivo): ")
                try:
                    minutos = int(tiempo_txt)
                except ValueError:
                    print("[Error] El tiempo debe ser un numero entero.")
                    continue
                self.agregar_conexion(origen, destino, minutos)

            elif opcion == "5":
                origen = input("Estacion origen: ")
                destino = input("Estacion destino: ")
                ruta, tiempo = self.dijkstra(origen, destino)
                if ruta is None:
                    print("No existe ruta entre las estaciones indicadas.")
                else:
                    print("Ruta mas rapida: " + " -> ".join(ruta))
                    print(f"Tiempo total: {tiempo} minutos")

            elif opcion == "6":
                origen = input("Estacion origen: ")
                destino = input("Estacion destino: ")
                if self.existe_camino(origen, destino):
                    print(f"Si existe un camino entre '{origen.strip()}' y '{destino.strip()}'.")
                else:
                    print(f"No existe camino entre '{origen.strip()}' y '{destino.strip()}'.")

            elif opcion == "7":
                self.guardar_en_archivo()

            elif opcion == "8":
                respuesta = input("Deseas guardar los cambios antes de salir? (s/n): ").strip().lower()
                if respuesta == "s":
                    self.guardar_en_archivo()
                print("Saliendo del programa. Hasta pronto.")
                break

            elif opcion == "9":
                hubs, grado = self.obtener_estacion_hub()
                if not hubs:
                    print("La red esta vacia, no hay estacion hub.")
                elif len(hubs) == 1:
                    print(f"Estacion hub: '{hubs[0]}' con {grado} conexiones directas.")
                else:
                    print(f"Hay {len(hubs)} estaciones empatadas con grado {grado}:")
                    for h in hubs:
                        print(f"  - {h}")

            elif opcion == "10":
                self.exportar_informe_json()

            elif opcion == "11":
                origen = input("Estacion origen: ")
                intermedia = input("Estacion intermedia (obligatoria): ")
                destino = input("Estacion destino: ")
                ruta, tiempo = self.dijkstra_con_intermedia(origen, intermedia, destino)
                if ruta is not None:
                    print("Ruta mas rapida (pasando por intermedia): " + " -> ".join(ruta))
                    print(f"Tiempo total: {tiempo} minutos")

            else:
                print("[Error] Opcion no valida. Introduce un numero del 1 al 11.")


def main():
    red = RedTransporte()
    red.cargar_desde_archivo()
    try:
        red.menu()
    except (KeyboardInterrupt, EOFError):
        # Permite salir con Ctrl+C / Ctrl+D guardando la red para no perder datos
        print("\n[Aviso] Interrupcion detectada. Guardando red antes de salir...")
        red.guardar_en_archivo()


if __name__ == "__main__":
    main()
