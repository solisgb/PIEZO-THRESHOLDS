# -*- coding: utf-8 -*-
"""
Created on Thu Jul 19 20:22:03 2018

@author: solis
"""

# parámetros de una ejecución, independientemente del proyecto

# rango de fechas 'd/m/yyyy' o 'now'
fecha1 = '1/1/2018'
fecha2 = 'now'

# indice piezométrico coef1 + coef2 must be 1
# (indice = coef1*media(n-1) * coef2*last_cnp)
coef1 = 0.4
coef2 = 1. - coef1

# directorio de resultados
# casa: C:\Users\solis\Documents\work\VM\umbrales_out
# pc oficina: C:\Users\solil\Documents\INT\CHS\VM\out
dir_out = r'\\Intsrv1008\sgd\00_Proyectos\42151\100_TRABAJO\100_10_DOC_COMUN\INFORMES_VM\20180809_INFORME_PIEZOMETRICO_SENCILLO\analisis_umbrales'

# nombre del fichero de resultados
file_out = '_VM_control_umbrales_piezo.txt'

# grabar gráficos de diferencias (0 no, 1 sí)
dif_xy = 1
