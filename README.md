# cicd-pipeline-python

Pipeline de CI para una calculadora web en Flask con GitHub Actions, Docker, SonarCloud y Docker Hub. Taller 2, Integración y Entrega Continua de Software (EAFIT).

## Integrantes

| Nombre completo            | Usuario de GitHub | Rol                         |
| -------------------------- | ----------------- | --------------------------- |
| Angel David Martinez Doria | Angel2327         | Propietario del repositorio |
| Jorge Andres Duran Cotamo  | Jorgeandd10       | Colaborador                 |

## Evidencias

- **Pull Request de la sección 9:** https://github.com/Angel2327/cicd-pipeline-python/pull/1
- **Ejecución fallida del pipeline por el error intencional:** https://github.com/Angel2327/cicd-pipeline-python/actions/runs/43603685626/job/132473626319?pr=1

## Respuestas

### 1. Ventajas de usar un pipeline de CI

- **Detección temprana de errores:** cada push y cada Pull Request ejecuta automáticamente las pruebas unitarias, de componente y de aceptación. Un error se detecta minutos después de escribirlo, cuando es más barato de corregir, y no días después en producción. En este taller lo comprobamos con el error intencional en `restar`: el pipeline lo detectó antes de que llegara a `main`.
- **Calidad y seguridad consistentes:** Black, Pylint, Flake8 y SonarCloud revisan cada cambio con las mismas reglas, sin depender de que alguien se acuerde de hacerlo. El Quality Gate impide integrar código con bugs, vulnerabilidades o cobertura insuficiente.
- **Entregas confiables y reproducibles:** el pipeline construye la imagen Docker, la prueba y la publica siempre de la misma forma. Así se elimina el "en mi máquina funciona", porque lo que se publica es exactamente lo que se probó.
- **Protección de la rama principal y trabajo en equipo:** combinado con la protección de `main`, ningún cambio entra sin pipeline en verde y sin la revisión de un compañero, lo que reduce los conflictos y mantiene `main` siempre en un estado desplegable.

### 2. Prueba unitaria vs. de componente vs. de aceptación

Ejemplo: una **tienda en línea** donde el usuario agrega productos a un carrito, aplica un cupón de descuento y paga.

- **Prueba unitaria:** prueba una función aislada, sin servidor, base de datos ni navegador. Ejemplo: la función `calcular_total(productos, cupon)` retorna el valor correcto cuando se aplica un cupón del 10%.
- **Prueba de componente:** prueba un componente completo de la aplicación (rutas, lógica y plantillas juntas), pero sin levantar un servidor real ni un navegador. Ejemplo: con el cliente de pruebas del framework, enviar un POST a `/carrito/agregar` y verificar que la respuesta tiene código 200 y que el HTML muestra el producto en el carrito.
- **Prueba de aceptación:** prueba la aplicación como la usaría un usuario real, con un navegador sobre la aplicación en ejecución. Ejemplo: con Selenium, abrir la tienda, buscar un producto, agregarlo al carrito, aplicar el cupón y verificar que en pantalla aparece el total con el descuento.

### 3. Steps del workflow de GitHub Actions

| Step                               | Qué hace                                                                                                 | Para qué se hace                                                                                      |
| ---------------------------------- | -------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| **Checkout**                       | Clona el repositorio con todo el historial (`fetch-depth: 0`).                                           | Tener el código en el runner; SonarCloud usa el historial para identificar el código nuevo.           |
| **Set up Python**                  | Instala Python 3.13.                                                                                     | Usar la misma versión que en local y en el `Dockerfile`.                                              |
| **Install dependencies**           | Instala `requirements-dev.txt` solo desde wheels (`--only-binary :all:`).                                | Tener las herramientas de calidad y pruebas con versiones fijas, sin ejecutar scripts de instalación. |
| **Run Black**                      | Verifica el formato con `black app --check`.                                                             | Detener el pipeline si hay código sin formatear.                                                      |
| **Run Pylint / Run Flake8**        | Generan `pylint-report.txt` y `flake8-report.txt` (`--exit-zero`).                                       | Entregar los hallazgos a SonarCloud, que es quien decide con el Quality Gate.                         |
| **Run Unit and Component Tests**   | Ejecuta pytest con cobertura mínima del 80% y genera `coverage.xml`.                                     | Detener el pipeline si una prueba falla o la cobertura baja, antes de construir la imagen.            |
| **Build Docker image**             | Construye la imagen y la etiqueta con el SHA del commit.                                                 | Tener una imagen identificada de forma única con la versión del código.                               |
| **Start container**                | Ejecuta la imagen en el puerto 8000 y espera hasta 30 s a que responda.                                  | Tener la aplicación empaquetada corriendo para las pruebas de aceptación.                             |
| **Run Acceptance Tests**           | Ejecuta las pruebas de Selenium contra el contenedor (`APP_BASE_URL=http://localhost:8000`).             | Validar la imagen real que se va a publicar, como lo haría un usuario.                                |
| **Show container logs on failure** | Muestra los logs del contenedor solo si algo falló.                                                      | Facilitar el diagnóstico.                                                                             |
| **Upload Test Reports Artifacts**  | Sube los reportes de pruebas, cobertura y linters (siempre).                                             | Poder revisar los resultados aunque el pipeline falle.                                                |
| **SonarCloud Scan**                | Envía código y reportes a SonarCloud y espera el Quality Gate.                                           | Detener el pipeline si el código no cumple los criterios de calidad y seguridad.                      |
| **Login to Docker Hub**            | Inicia sesión con `DOCKERHUB_USERNAME` y el secreto `DOCKERHUB_TOKEN` (solo en push a `main`).           | Autorizar la publicación de la imagen.                                                                |
| **Push Docker image**              | Etiqueta la imagen probada como `latest` y publica las etiquetas SHA y `latest` (solo en push a `main`). | Publicar exactamente la imagen que pasó todas las validaciones, sin reconstruirla.                    |

### 4. Problemas y aprendizajes

**Angel David Martinez Doria:**

- Al guardar `app/templates/index.html`, la extensión de formato de VS Code (Prettier) cambiaba `<!DOCTYPE html>` a `<!doctype html>`, y la prueba `test_index_get` fallaba porque busca el texto exacto. Lo solucioné guardando sin formato (_Save without Formatting_) y desactivando el formato automático para HTML. Aprendí que las herramientas del editor pueden romper pruebas sin que uno toque la lógica.
- En SonarCloud aparecieron issues que el enunciado no contemplaba: accesibilidad en el HTML (atributo `lang` y `label` en los campos), Flask escuchando en `0.0.0.0`, acciones de GitHub sin fijar a un SHA, `pip install` sin `--only-binary` y la imagen Docker ejecutándose como `root` (lo corregí creando un usuario sin privilegios en el `Dockerfile`). Los corregí en el código. También se presentaron dos issues sin solución dentro del alcance del taller: la protección CSRF del formulario y las dependencias sin lock de versiones transitivas. Esos los marqué como _Accepted_ en SonarCloud, cada uno con su justificación.

**Jorge Andres Duran Cotamo:**

- **Python no se encontraba en Windows:** al crear el entorno virtual, el comando `python` abría un mensaje de la Microsoft Store en lugar de ejecutar Python. Windows tenía activo el alias de ejecución de la Store, y en mi equipo solo había Python 3.8, 3.9 y 3.12, mientras que el taller y el pipeline usan 3.13. Lo solucioné instalando Python 3.13 y creando el entorno con el lanzador de Windows (`py -3.13 -m venv venv`). También aprendí que en Git Bash el entorno se activa con `source venv/Scripts/activate` y no con `venv\Scripts\activate`. Aprendizaje: usar la misma versión de Python en local y en el pipeline evita el clásico "en mi máquina sí funciona".
- **La carpeta `venv/` aparecía en `git status`:** el `.gitignore` no se había guardado en la raíz del repositorio, así que Git iba a subir el entorno virtual. Lo detecté con `git status` y `ls -a` (los archivos que empiezan con punto están ocultos) y lo creé de nuevo en la ubicación correcta.
- **Docker no se conectaba al construir la imagen:** `docker build` fallaba con el error `failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine`. El comando `docker` estaba instalado, pero el motor de Docker Desktop no estaba encendido. Lo solucioné abriendo Docker Desktop y esperando a que dijera "Engine running", y lo verifiqué con `docker version`, que debe mostrar las secciones Client y Server.

### 5. Ventajas de probar y publicar la misma imagen Docker

- **Lo que se publica es lo que se probó:** las pruebas de aceptación corren contra el contenedor real, con las mismas dependencias, sistema base y comando de arranque (Gunicorn). Si se reconstruyera la imagen después, podría cambiar algo (una dependencia, la imagen base) y publicarse una versión que nunca se probó.
- **Detecta errores de empaquetado:** validar solo el código no detecta un `Dockerfile` mal escrito, un archivo que no se copió a la imagen o una dependencia que falta en `requirements.txt`. Probar la imagen sí.
- **Trazabilidad:** la imagen se etiqueta con el SHA del commit, así se sabe exactamente qué código contiene cada versión publicada y se puede volver a una anterior.
- **Consistencia entre entornos:** la misma imagen se puede desplegar en cualquier entorno (pruebas, producción) y se comporta igual, lo que prepara el despliegue del Taller 3.

### 6. Pull Request de la sección 9

**Pruebas agregadas:**

| Prueba                               | Qué verifica                                                                            | Qué error detectaría                                                                                         |
| ------------------------------------ | --------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| `test_sumar_decimales`               | `sumar(0.1, 0.2) == pytest.approx(0.3)`                                                 | Que `sumar` convierta a entero o redondee mal los decimales.                                                 |
| `test_restar_dos_negativos`          | `restar(-5, -3) == -2`                                                                  | Un error de signos en `restar`, o que sume en lugar de restar (daría `-8`).                                  |
| `test_index_post_un_numero_invalido` | Un formulario con `num1='2'` y `num2='abc'` muestra "Error: Introduce números válidos". | Que la aplicación solo valide el primer número, o que falle con un error 500 en lugar de mostrar el mensaje. |

**Error intencional:** se cambió `restar` para que retornara `a + b`.

- **Paso donde falló:** `Run Unit and Component Tests`. Fallaron `test_restar`, `test_restar_dos_negativos` y `test_index_post_restar`.
- **Pasos que no se ejecutaron:** `Build Docker image`, `Start container`, `Run Acceptance Tests`, `SonarCloud Scan`, `Login to Docker Hub` y `Push Docker image`. Solo se ejecutaron `Show container logs on failure` (por `if: failure()`) y `Upload Test Reports Artifacts` (por `if: always()`).
- **Cómo se evitó que llegara a `main` y a Docker Hub:** la regla `proteger-main` exige un Pull Request con 1 aprobación y el check `build-and-test` en verde. Como el check falló, GitHub bloqueó el botón de merge, y nadie (ni el propietario) puede hacer push directo a `main`. Además, la publicación en Docker Hub solo ocurre en un push a `main` después de que todo pasa, así que la imagen con el error nunca se construyó ni se publicó. Al corregir `restar`, el pipeline volvió a quedar en verde, se aprobó el PR, se hizo el merge y se publicó la imagen correcta.
