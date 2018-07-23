# -*- coding: utf-8 -*-
"""
realiza cálculos sencillos sobre la evolución piezométrica de uno o
varios pozos en relación sus umbrales piezométricos
piezo_CTH: piezometry Conpliance ThresHolds
"""

if __name__ == "__main__":

    try:
        from datetime import timedelta
        from time import time
        import log_file as lf
        from piezo_CTH import select_project, control_umbrales, dif_grapfs
        from piezo_CTH_parameters import dif_xy

        project = select_project()
        startTime = time()

        control_umbrales(project)

        if dif_xy == 1:
            dif_grapfs(project)

        xtime = time() - startTime
        print('The script took {0}'.format(str(timedelta(seconds=xtime))))
    except Exception as e:
        import traceback
        import logging
        logging.error(traceback.format_exc())
        msg = '\n{}'.format(traceback.format_exc())
        lf.write(msg)
        print('Se ha producido un error')
    finally:
        lf.to_file()
        print('Se ha escrito el fichero log.txt con las incidencias')
