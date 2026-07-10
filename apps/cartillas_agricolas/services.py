"""
Servicios para Cartillas Agrícolas.
Consultas a AREA, area_plantilla, Plantilla en APP_AGRICOLA.
"""
try:
    from apps.connection.connect_app_agricola import connection_app_agricola
except ImportError:
    connection_app_agricola = None


def get_areas_cartillas_agricolas():
    """
    Lista áreas con mostrar_en_cartillas_agricolas = 1.
    Retorna: [{'idArea': int, 'nombreArea': str}, ...]
    """
    if not connection_app_agricola:
        return []
    areas = []
    sql = """
        SELECT id_area, nombre_area
        FROM dbo.AREA
        WHERE mostrar_en_cartillas_agricolas = 1
        ORDER BY nombre_area
    """
    try:
        cursor = connection_app_agricola.cursor()
        cursor.execute(sql)
        for row in cursor.fetchall():
            id_val, nom_val = row[0], row[1]
            if id_val is not None and nom_val:
                areas.append({'idArea': int(id_val), 'nombreArea': str(nom_val).strip()})
        cursor.close()
    except Exception:
        pass
    return areas


def get_plantillas_por_area(id_area):
    """
    Lista plantillas del área vía area_plantilla.
    Plantilla: PlantillaId, Nombre. area_plantilla.id_plantilla -> Plantilla.PlantillaId.
    Retorna: [{'idPlantilla': int, 'nombrePlantilla': str}, ...]
    """
    if not connection_app_agricola or id_area is None:
        return []
    plantillas = []
    sql = """
        SELECT p.PlantillaId, p.Nombre
        FROM dbo.area_plantilla ap
        INNER JOIN dbo.Plantilla p ON p.PlantillaId = ap.id_plantilla
        WHERE ap.id_area = ? AND ap.is_active = 1
          AND (p.IsActive = 1 OR p.IsActive IS NULL)
        ORDER BY ISNULL(ap.orden, 9999), p.Nombre
    """
    try:
        cursor = connection_app_agricola.cursor()
        cursor.execute(sql, [id_area])
        for row in cursor.fetchall():
            id_val, nom_val = row[0], row[1]
            if id_val is not None and nom_val:
                plantillas.append({'idPlantilla': int(id_val), 'nombrePlantilla': str(nom_val).strip()})
        cursor.close()
    except Exception:
        pass
    return plantillas
