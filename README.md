# Análisis de Algoritmia en el Contexto de la Bibliometría

---
# **Requerimientos del Proyecto y Estado**  

---

### ![No implementado](https://img.shields.io/badge/Estado-No_implementado-red) **Requerimiento 1: Unificación de Datos**  
- Generar un archivo unificado (RIS/BibTex) con los datos de diferentes bases, asegurando la eliminación de registros duplicados.  
- Crear un archivo separado con los productos duplicados eliminados.  

---

### ![No implementado](https://img.shields.io/badge/Estado-No_implementado-red) **Requerimiento 2: Generación de Estadísticas**  
Desde el archivo unificado, calcular:  
- 15 autores más citados  
- Cantidad de publicaciones por tipo de producto y año  
- 15 journals con más apariciones  
- 15 publishers con más apariciones  

---

### ![No implementado](https://img.shields.io/badge/Estado-No_implementado-red) **Requerimiento 3: Análisis de Frecuencia y Visualización**  
- Determinar la frecuencia de aparición de palabras clave en los resúmenes  
- Unificar sinónimos para un análisis coherente  
- Generar nube de palabras y gráficos de co-word dentro de la aplicación  

---

### ![No implementado](https://img.shields.io/badge/Estado-No_implementado-red) **Requerimiento 4: Medición de Similitud de Abstracts**  
- Implementar al menos dos técnicas de similitud textual para agrupar artículos con contenido relacionado  

---

### ![No implementado](https://img.shields.io/badge/Estado-No_implementado-red) **Requerimiento 5: Despliegue y Documentación**  
- El proyecto debe estar desplegado con documentación técnica detallada  
- Incluir un documento de diseño con arquitectura y detalles de implementación  
- Justificar el uso de IA si se emplea  

---

### **Leyenda de Estados**  
- ![Implementado](https://img.shields.io/badge/Estado-Implementado-brightgreen) Requerimiento completado  
- ![No implementado](https://img.shields.io/badge/Estado-No_implementado-red) Requerimiento pendiente  


---

## Universidad del Quindío  
**Programa de Ingeniería de Sistemas y Computación**  
**Materia: Análisis de Algoritmos**  

## Introducción  
La bibliometría es una disciplina dentro de la cienciometría que permite analizar grandes volúmenes de datos científicos mediante métodos cuantitativos. Se basa en la matemática y la estadística para establecer descripciones, relaciones e inferencias sobre información proveniente de artículos, conferencias y publicaciones científicas en diversas áreas del conocimiento.

## Contexto  
En bibliometría, se identifican indicadores de productividad, impacto, tipologías de producción académica, relaciones entre autores, entre otros. Donthu et al. (2021) presentan técnicas de análisis como el análisis de desempeño, mapeo científico y técnicas enriquecidas, todas basadas en métodos estadísticos y algoritmos.

## Dominio  
El dominio de conocimiento del proyecto es el **pensamiento computacional** (*Computational Thinking*), un área con alta productividad científica. Se puede consultar información en los siguientes enlaces:
- [Artículo 1](https://revistas.itm.edu.co/index.php/tecnologicas/article/view/2950)
- [Artículo 2](https://www.mdpi.com/2227-7102/14/10/1124)
- [Artículo 3](https://revista.eia.edu.co/index.php/reveia/article/view/1716)

## Fuentes de Información  
Se utilizarán bases de datos científicas disponibles en la [biblioteca de la Universidad del Quindío](https://library.uniquindio.edu.co/databases), incluyendo ACM, SAGE, ScienceDirect. La información se obtendrá en formatos RIS, BibTex, CSV o texto plano, considerando restricciones de acceso y calidad de datos.

## Propósito del Proyecto  
Implementar algoritmos para el análisis bibliométrico y computacional sobre el dominio del pensamiento computacional, utilizando bases de datos disponibles en la universidad. Se desarrollarán técnicas bibliométricas, representación de información y análisis cuantitativo. Además, se desplegará la aplicación con su respectiva documentación.

## Requerimientos Funcionales  

### Requerimiento 1: Unificación de Datos  
- Generar un archivo unificado (RIS/BibTex) con los datos de diferentes bases, asegurando la eliminación de registros duplicados.
- Crear un archivo separado con los productos duplicados eliminados.

### Requerimiento 2: Generación de Estadísticas  
Desde el archivo unificado, calcular:
- **15 autores más citados**
- **Cantidad de publicaciones por tipo de producto y año**
- **15 journals con más apariciones**
- **15 publishers con más apariciones**

### Requerimiento 3: Análisis de Frecuencia y Visualización  
- Determinar la frecuencia de aparición de palabras clave en los resúmenes.
- Unificar sinónimos para un análisis coherente.
- Generar **nube de palabras** y **gráficos de co-word** dentro de la aplicación.

### Requerimiento 4: Medición de Similitud de Abstracts  
- Implementar al menos **dos técnicas** de similitud textual para agrupar artículos con contenido relacionado.

### Requerimiento 5: Despliegue y Documentación  
- El proyecto debe estar desplegado con documentación técnica detallada.
- Incluir un documento de diseño con arquitectura y detalles de implementación.
- Justificar el uso de IA si se emplea.

## Tecnologías Utilizadas  
- **Lenguajes**: Python
- **Bibliotecas**: Pandas, Scikit-learn, NLTK, Matplotlib, NetworkX.
- **Bases de Datos**: PostgreSQL, MongoDB (según sea necesario).
- **Frameworks**: Flask, FastAPI, o similar para la interfaz.

## Despliegue  
- La aplicación debe estar disponible en un entorno accesible con documentación clara.
- Se debe proporcionar instrucciones para instalación y uso.

