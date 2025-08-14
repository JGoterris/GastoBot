class Routes:
    # Datos de callback
    ACEPTAR = "Aceptar"
    MODIFICAR = "Modificar"
    CANCELAR = "Cancelar"
    VOLVER_MENU = "Volver_Menu"
    MODIFICAR_ESTABLECIMIENTO = "Modificar_Establecimiento"
    MODIFICAR_IMPORTE = "Modificar_Importe"
    MODIFICAR_DESCRIPCION = "Modificar_Descripcion"
    MODIFICAR_FECHA = "Modificar_Fecha"
    MODIFICAR_CATEGORIA = "Modificar_Categoria"
    ATRAS_MODIFICACIONES = "Atras_Modificaciones"

    # Patrones exactos para handlers
    P_ACEPTAR = f"^{ACEPTAR}$"
    P_CANCELAR = f"^{CANCELAR}$"
    P_MODIFICAR = f"^{MODIFICAR}$"
    P_VOLVER_MENU = f"^{VOLVER_MENU}$"
    P_MODIFICAR_ESTABLECIMIENTO = f"^{MODIFICAR_ESTABLECIMIENTO}$"
    P_MODIFICAR_IMPORTE = f"^{MODIFICAR_IMPORTE}$"
    P_MODIFICAR_DESCRIPCION = f"^{MODIFICAR_DESCRIPCION}$"
    P_MODIFICAR_FECHA = f"^{MODIFICAR_FECHA}$"
    P_MODIFICAR_CATEGORIA = f"^{MODIFICAR_CATEGORIA}$"
    P_ATRAS_MODIFICACIONES = f"^{ATRAS_MODIFICACIONES}$"
