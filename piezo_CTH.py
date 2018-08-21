# -*- coding: utf-8 -*-
"""
Created on Thu Jul 19 19:16:33 2018

@author: solis

Funciones que realizan en análisis de una serie temporal (piezométrica) en
    puntos que tienen definidos umbrales de referencia
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
    selecciona los datos y hace los análisis

    input:
        project: tag proyecto seleccionado
    """
    from os.path import join
    import pyodbc
    import numpy as np
    import piezo_CTH_parameters as par
    import db_con_str

    db = project.find('db').text.strip()
    tag_pozos = project.findall('point')
    tag_umbrales = project.findall('umbral')
    cods_u = [tag_u.get('cod').strip() for tag_u in tag_umbrales]
    params_u = [tag_u.get('parametro').strip() for tag_u in tag_umbrales]
    selected2xy = [int(tag_u.get('selected2xy')) for tag_u in tag_umbrales]
    selects_dp = [tag_u.find('select_data_param').text.strip()
                  for tag_u in tag_umbrales]
    select_umbral = project.find('select_umbral').text.strip()

    fecha1 = str_to_date(par.fecha1)
    fecha2 = str_to_date(par.fecha2)

    headers = ['Id pozo', 'Nombre', 'X m', 'Y m', 'Z  msnm']
    for param_u in params_u:
        headers.append('Umbral m ' + param_u)
        headers.append('Media m ' + param_u)
        headers.append('Media - umbral m ' + param_u)
        headers.append('Últ. medida - umbral m ' + param_u)
        headers.append('Índice ' + param_u)
    headers.append('Oscilación máx NP m')

    fmt1 = '{}\t{}\t'+3*'{:0.2f}\t'
    # ojo, si se modifican las columnas media, media-umbral y Ultmed-umbral
    # hay que cambiar posiblemente fmt2
    fmt2 = 3*'\t{:0.2f}'+'\t'

    pozos_iue, pozos_iud, values_iue, values_iud = [], [], [], []

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
        for cod_u, param_u, select_dp, toxy in zip(cods_u, params_u,
                                                   selects_dp,
                                                   selected2xy):
            if toxy == 1:
                if param_u == 'CNP ND':
                    pozos = pozos_iud
                    indexes = values_iud
                elif param_u == 'CNP NE':
                    pozos = pozos_iue
                    indexes = values_iue

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

            # clasificación del comportamiento piezométrico
            if cnp.size > 2:
                median = np.median(cnp[:-1]) - umbral
                cnp_index = par.coef1 * median + par.coef2 * (cnp[-1] - umbral)
                fo.write('{:0.2f}\t'.format(cnp_index))
            else:
                cnp_index = None
                fo.write('NaN\t')

            if toxy == 1:
                pozos.append(cod)
                indexes.append(cnp_index)

            i += 1
            if i == len(cods_u):
                if n_series > 0:
                    rango = abs(maximun - minimun)
                    fo.write('{:0.2f}\n'.format(rango))
                else:
                    fo.write('NaN\n')

    con.close()
    fo.close()

    boreholes, ines, inds = [], [], []
    if pozos_iue:
        for pozo, ne, nd in zip(pozos_iue, values_iue, values_iud):
            if ne is None or nd is None:
                continue
            boreholes.append(pozo)
            ines.append(ne)
            inds.append(nd)

        _made_xy_graph(boreholes, ines, inds)


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


def dif_grapfs(project):
    """
    graba gráficos de diferencias (serie -piezométrica- - umbral)

    input:
        project: tag proyecto seleccionado
    """
    from os.path import join
    import numpy as np
    import pyodbc
    import piezo_CTH_parameters as par
    import db_con_str
    from piezo_CTH_XY import Time_series, XYt_1

    lf.write('\n Gráficos de diferencias')

    db = project.find('db').text.strip()
    tag_pozos = project.findall('point')
    tag_umbrales = project.findall('umbral')
    cods_u = [tag_u.get('cod').strip() for tag_u in tag_umbrales]
    params_u = [tag_u.get('parametro').strip() for tag_u in tag_umbrales]
    selects_dp = [tag_u.find('select_data_param').text.strip()
                  for tag_u in tag_umbrales]
    ylegends = [tag_u.get('ylegend').strip()
                for tag_u in tag_umbrales]

    select_umbral = project.find('select_umbral').text.strip()

    fecha1 = str_to_date(par.fecha1)
    fecha2 = str_to_date(par.fecha2)

    con = pyodbc.connect(db_con_str.con_str(db))
    cur = con.cursor()

    print('gráficos xy')
    for tag in tag_pozos:
        cod = tag.get('cod').strip()
        print(cod)
        for cod_u, param_u, select_dp, ylegend in zip(cods_u, params_u,
                                                      selects_dp,
                                                      ylegends):
            cur.execute(select_umbral, (cod, cod_u, param_u))
            row = cur.fetchone()
            if row is None:
                raise ValueError('{} no tiene umbrales de {} {}'
                                 .format(cod, cod_u, param_u))
            toponimia = row.TOPONIMIA
            umbral = row.UMBRAL

            cur.execute(select_dp, (cod, fecha1, fecha2))
            rows = [row for row in cur]
            if len(rows) < 2:
                lf.write('{}; tiene < 2 datos {}, {} entre las fechas {} y {}'
                         .format(cod, cod_u, param_u,
                                 fecha1.strftime('%d/%m/%Y'),
                                 fecha2.strftime('%d/%m/%Y')))
                continue

            fechas = [row.FECHA for row in rows]
            values = [row.CNP for row in rows]
            values = np.array(values, dtype=FLOAT_PRECISION)
            values = values - umbral

            s1 = Time_series(fechas, values, ylegend, '.')
            stitle = '{} ({})\nDiferencia serie vs umbral {} ({})' \
                     .format(cod, toponimia, param_u, cod_u)
            tmp = cod + '_' + param_u + '_' + cod_u + '.png'
            tmp2 = tmp.replace(' ', '_')
            file_name = tmp2.replace('/', '_')
            dst = join(par.dir_out, file_name)
            XYt_1([s1], stitle, ylegend, dst)

    con.close()


def _made_xy_graph(pozos, values_iue, values_iud):
    """
    hace un gáfico de valores del índice para estáticos y dinámicos
    """
    import matplotlib.pyplot as plt
    from os.path import join
    from piezo_CTH_parameters import dir_out
    name_graph = '_XY_INDICES.png'
    dst = join(dir_out, name_graph)
    print(name_graph)

    fig, ax = plt.subplots()
    ivalues_iue = sorted(range(len(values_iue)), key=values_iue.__getitem__)
    for i in ivalues_iue:
        if values_iue[i] is not None and values_iud[i] is not None:
            ax.scatter(values_iue[i], values_iud[i], label=pozos[i])
    ax.set_title('Caracterización piezométrica')
    plt.xlabel('IUNE (m)')
    plt.ylabel('IUND (m)')
    plt.legend(loc='upper left', ncol=3, fontsize=9, bbox_to_anchor=(0, 0),
               borderaxespad=4.0)
    plt.tight_layout()
    plt.grid(True)

    fig.savefig(dst)
    plt.close('all')
