# -*- coding: utf-8 -*-
"""
Created on Thu Jul 19 19:16:33 2018

@author: solis

Funciones que realizan en análisis de la evolución piezométrica de los
pozos en relación a sus umbrales
"""

import log_file as lf

FLOAT_PRECISION = 'float64'


def select_project(filename='control_umbrales.xml'):
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
    print('Select project number:')
    choice = input()
    return projects[int(choice)]


def control_umbrales(project):
    """
    selecciona los datos
    """
    from os.path import join
    import pyodbc
    import numpy as np
    import control_umbrales_parameters as par
    import db_con_str

    db = project.find('db').text.strip()
    tag_pozos = project.findall('pozos/pozo')
    tag_umbrales = project.findall('umbral')
    cods_u, params_u = [(tag_u.get('cod'), tag_u.get('parametro')
                        ) for tag_u in tag_umbrales]
    select_umbral = project.find('select_umbral').text.strip()
    select_ne = project.find('select_ne').text.strip()
    select_nd = project.find('select_nd').text.strip()
    con = pyodbc.connect(db_con_str.con_str(db))
    cur = con.cursor()

    fo = open(join(par.dir_out, par.file_out), 'w')
    fo.write('{}\t'+4*'{}t'.format('cod', 'toponimia',
                         'x', 'y', 'z'))
    # TODO: HEADER
    for param_u in params_u:
        fo.write('{}'.format())

    for tag in tag_pozos:
        cod = tag.get('cod').strip()
        print(cod)
        flag1 = 1
        for cod_u, param_u in zip(cods_u, params_u):
            cod_u = tag_u.get('cod')
            par_u = tag_u.get('parametro')
            cur.execute(select_umbral, (cod, cod_u, par_u))
            row = cur.fetchone()
            toponimia = row.TOPONIMIA
            x = row.X_UTM
            y = row.Y_UTM
            z = row.Z
            umbral = row.UMBRAL

            fecha1 = str_to_validate_date(par.fecha1)
            fecha2 = str_to_validate_date(par.fecha2)

            if par_u == 'CNP NE':
                cur.execute(select_ne, (cod, fecha1, fecha2))
                tmp = [row.CNP for row in cur]
                cnp = np.array(tmp, dtype=FLOAT_PRECISION)

            if par_u == 'CNP ND':
                cur.execute(select_nd, (cod, par.fecha1, par.fecha2))
                tmp = [row.CNP for row in cur]
                cnp = np.array(tmp, dtype=FLOAT_PRECISION)

            mean = np.mean(cnp)

            if flag == 1:
                fo.write('{}\t{}'+3*'{:0.2f}\t'.format(cod, toponimia,
                         x, y, z)
                flag = 0



    con.close()
    fo.close()


def str_to_validate_date(sdate: str):
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
