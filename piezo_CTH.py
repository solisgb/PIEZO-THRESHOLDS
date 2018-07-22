# -*- coding: utf-8 -*-
"""
Created on Thu Jul 19 19:16:33 2018

@author: solis

Funciones que realizan en análisis de la evolución piezométrica de los
pozos en relación a sus umbrales
"""

import log_file as lf

FLOAT_PRECISION = 'float64'
file_xml_ini = 'piezo_CTH.xml'


def select_project(filename=file_xml_ini):
    """
    lee el fichero xml FILENAME, muestra los proyectos para que el usuario
        escoja uno de ellos

    input
    FILENAME: fichero xml de estructura adecuada situada donde se encuentran
        los scripts del programa

    return:
        el proyecto seleccionado por el usuario con un árbol xml
    """
    import xml.etree.ElementTree as ET
    tree = ET.parse(filename)
    root = tree.getroot()

    print('Projects in ' + filename)
    projects = []
    for i, project in enumerate(root.findall('project')):
        projects.append(project)
        print(i, end=' ')
        print('. ' + project.get('name'))
    print('Select project number:', end=' ')
    choice = input()
    return projects[int(choice)]


def control_umbrales(project):
    """
    selecciona los datos
    """
    from os.path import join
    import pyodbc
    import numpy as np
    import piezo_CTH_parameters as par
    import db_con_str

    db = project.find('db').text.strip()
    tag_pozos = project.findall('pozos/pozo')
    tag_umbrales = project.findall('umbral')
    cods_u = [tag_u.get('cod').strip() for tag_u in tag_umbrales]
    params_u = [tag_u.get('parametro').strip() for tag_u in tag_umbrales]
    selects_dp = [tag_u.find('select_data_param').text.strip()
                  for tag_u in tag_umbrales]
    select_umbral = project.find('select_umbral').text.strip()
#    select_ne = project.find('select_ne').text.strip()
#    select_nd = project.find('select_nd').text.strip()

    fecha1 = str_to_date(par.fecha1)
    fecha2 = str_to_date(par.fecha2)

    headers = ['cod', 'toponimia', 'x m', 'y m', 'z  msnm']
    for param_u in params_u:
        headers.append('umbral ' + param_u)
        headers.append('media ' + param_u)
        headers.append('media - umbral ' + param_u)
        headers.append('Últ. medida - umbral ' + param_u)
    headers.append('Oscilación máx NP')

    fmt1 = '{}\t{}\t'+3*'{:0.2f}\t'
    # ojo, si se modifican las columnas media, media-umbral y Ultmed-umbral
    # hay que cambiar posiblemente fmt2
    fmt2 = 3*'\t{:0.2f}'+'\t'

    fo = open(join(par.dir_out, par.file_out), 'w')
    fo.write('\t'.join(headers) + '\n')

    con = pyodbc.connect(db_con_str.con_str(db))
    cur = con.cursor()

    for tag in tag_pozos:
        cod = tag.get('cod').strip()
        print(cod)
        i = 0
        maximun = -99999999.
        minimun = 99999999.
        n_series = 0
        for cod_u, param_u, select_dp in zip(cods_u, params_u, selects_dp):
            cur.execute(select_umbral, (cod, cod_u, param_u))
            row = cur.fetchone()
            if row is None:
                raise ValueError('{} no tiene umbrales de {} {}'
                                 .format(cod, cod_u, param_u))
            toponimia = row.TOPONIMIA
            x = row.X_UTM
            y = row.Y_UTM
            z = row.Z
            umbral = row.UMBRAL

            cur.execute(select_dp, (cod, fecha1, fecha2))
            tmp = [row.CNP for row in cur]
            cnp = np.array(tmp, dtype=FLOAT_PRECISION)

            if cnp.size > 0:
                n_series += 1
                mean = np.mean(cnp)
                maximun = max(maximun, np.max(cnp))
                minimun = min(minimun, np.min(cnp))
            else:
                lf.write('{}; no tiene datos {}, {} entre las fechas {} y {}'
                         .format(cod, cod_u, param_u,
                                 fecha1.strftime('%d/%m/%Y'),
                                 fecha2.strftime('%d/%m/%Y')))

            if i == 0:
                fo.write(fmt1.format(cod, toponimia, x, y, z))

            fo.write('{:0.2f}'.format(umbral))
            if cnp.size > 0:
                y1 = cnp[-1]
                fo.write(fmt2.format(mean, mean-umbral, mean-y1))
            else:
                fo.write('\tNaN\tNaN\tNaN\t')

            i += 1
            if i == len(cods_u):
                if n_series > 0:
                    rango = abs(maximun - minimun)
                    fo.write('{:0.2f}\n'.format(rango))
                else:
                    fo.write('NaN\n')

    con.close()
    fo.close()


def str_to_date(sdate: str):
    """
    a partir de un str con formato "dd/mm/yyyy" devuelve un objeto date
    """
    from datetime import date
    if sdate == 'now':
        sdate = date.today().strftime('%d/%m/%Y')
    ws = sdate.split('/')
    try:
        return date(int(ws[2]), int(ws[1]), int(ws[0]))
    except Exception as error:
        raise ValueError('La fecha {} no es válida'.format(sdate))
