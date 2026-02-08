# Prompt para crear claude.md

Actúa como un Senior Backend Engineer.

Crea un archivo `claude.md` con guía de estilos y arquitectura
basado en:

- Django Style Guide
- Clean Architecture
- Domain Driven Design (light)
- 12 Factor App
- Best practices de microservicios

Stack:
- Python 3.12
- FastAPI 0.111.0
- PostgreSQL 16.3
- Sin ORM (sanitizar queries para evitar SQL injection)
- Pydantic
- Pytest
- Docker

Incluye:

- Arquitectura por capas
- Flujo request → domain → db
- Manejo de transacciones
- Versionado
- Migraciones sin ORM
- Performance
- Seguridad
- Observabilidad
- Testing
- Anti-patterns

Formato: Markdown
Idioma: Español
Nivel: Senior
Con ejemplos.

Ten estos requisitos que nos solicitan 
    • Diseñe e implemente un modelo Entidad-Relación en base de datos de la tabla o conjuntos de tablas en PostgreSQL que almacenarán la información de cada uno de los casos de soporte o requerimientos. Algunos campos que pueden tener sentido: base de datos, esquema, consulta, persona que lo hace, etc. Está en su criterio definir cada uno de estos. Recuerde que a partir de esta información se podría hacer la trazabilidad de cada uno de estos casos por lo tanto las tablas deben tener las columnas necesarias como para poder hacer un análisis de los datos generados hipotéticamente.
    • Creación de un API con FastAPI y Python para el manejo de cada una de las tablas diseñadas. 
        ◦ Solo se insertan y se leen registros. 
        ◦ No usar ORMs.
        ◦ Respuestas en formato JSON.
        ◦ Respuestas que incluyan códigos http response.
        ◦ No debe estar todo el proyecto en 1 solo archivo, dividir responsabilidades y enrutamientos.

Finalmente esto es lo que va a consumir/necesitar el Frontend
    B. Frontend:

Se deben crear las siguientes vistas usando React y TypeScript:
    1. Creación de un nuevo caso de soporte/requerimiento de negocio: acá es donde se deberían emplear los endpoints de tipo post, o en otras palabras, debería estar el formulario donde se ingresa la información de un nuevo caso o requerimiento.
        a. Que cada parte de la vista sea un componente.
        b. Crear un compendio de componentes por aparte que se usen en la vista.
    2. Seguimiento: acá es donde se deberían emplear los endpoints de tipo get, o en otras palabras, donde se debe visualizar todos los registros que se han insertado hasta el momento. Esta vista debe contar con diferentes filtros para el análisis de los datos. No es necesario crear ningún tipo de gráfica como diagramas de barras o líneas de tiempo, con tablas y campos de texto es más que suficiente.
        a. Que la tabla tenga paginación y un máximo de 10 elementos.
        b. (opcional) Redirigir a una página de detalle de cada registro con los datos presentados al hacer click en esa fila.


# Implementación con claude.md luego de ajustes manuales realizados

Lee mi archivo @claude.md. Luego genera genera el esqueleto del proyecto con los modelos y migraciones y instala dependencias para crear el primer hola mundo de fast api  


# Endpoint creacion de casos

crear primer endpoint para crear casos @claude.md  con tests, usa un bulk create para guardar todas las queries del request

# Ajustes en tests

Para los tests usa una BD diferente (modifica @tests/conftest.py para crear base de datos y hacer migraciones correspondientes) 