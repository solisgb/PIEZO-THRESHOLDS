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
        from piezo_CTH import select_project, control_umbrales

        project = select_project()
        startTime = time()

        control_umbrales(project)

        xtime = time() - startTime
        print('The script took {0}'.format(str(timedelta(seconds=xtime))))
    except Exception as e:
        import traceback
        import logging
        logging.error(traceback.format_exc())
        MSG = '\n{}'.format(traceback.format_exc())
        lf.write(MSG)
    finally:
        lf.to_file()
        print('Fin\nSe ha escrito el fichero log.txt con las incidencias')
