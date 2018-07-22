# -*- coding: Latin-1 -*-
"""
Created on Sun Jul 22 17:00:47 2018

@author: solis
"""


class Time_series():
    """
    define los datos y sus atributos para ser representados en un
        grafico
    """
    def __init__(self, fechas: [], values: [], legend: str,
                 marker: str):
        """
        fechas: cada elemento una lista de dates
        values: cada elemento una lista de floats o integeres
        legend: leyenda de la serie
        marker: marcador de la serie en el grafico
        """
        from copy import deepcopy
        if len(fechas) != len(values):
            raise ValueError('fechas y values != longitud')
        self.fechas = deepcopy(fechas)
        self.values = deepcopy(values)
        self.legend = legend
        self.marker = marker


def XYt_1(t_series, stitle, ylabel, dst):
    """
    dibuja un gráfico xy de una o más series

    input
        t_series: lista de objetos Time_series; el primer elemento se
            considera la series principal
        stitle: título del gráfico
        ylabel: título del eje Y
        dst: directorio donde se graba el gráfico (debe existir)
    """
    import matplotlib.pyplot as mpl
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates

    dateFmt = mdates.DateFormatter('%d-%m-%Y')

    fig, ax = plt.subplots()
    # El primer objeto es el principal
    for ts1 in t_series:
        ax.plot(ts1.fechas, ts1.values, marker=ts1.marker, label=ts1.legend)

    plt.ylabel(ylabel)
    # rotate and align the tick labels so they look better
    fig.autofmt_xdate()

    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    ax.xaxis.set_major_formatter(dateFmt)
    ax.set_title(stitle)
    mpl.legend(loc='best', framealpha=0.5)
#    mpl.legend(loc='best', framealpha=0.5)
    mpl.tight_layout()
    mpl.grid(True)

    fig.savefig(dst)
    plt.close('all')
