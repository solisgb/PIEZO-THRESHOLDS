# -*- coding: utf-8 -*-
"""
realiza cálculos sencillos sobre la evolución piezométrica de uno o
varios pozos en relación sus umbrales piezométricos
"""

if __name__ == "__main__":

    try:
        from datetime import timedelta
        from time import time
        from control_umbrales import select_project, control_umbrales

        project = select_project()
        startTime = time()

        control_umbrales(project)

        xtime = time() - startTime
        print('The script took {0}'.format(str(timedelta(seconds=xtime))))
    except Exception as e:
        import traceback
        import logging
        logging.error(traceback.format_exc())
    finally:
        print('fin')
