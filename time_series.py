# -*- coding: utf-8 -*-
"""
Created on Mon Jul 16 09:22:00 2018
@author: Luis Solis

Serie temporal para gráficos con el módulo matplotlib

version: 0.2
"""


class Time_series():
    """
    define los datos y sus atributos para ser representados en un
        gráfico
    """
    def __init__(self, fechas: [], values: [], legend: str, marker: str = '.',
                 scatter: int = 0, slinestyle: str = '-'):
        """
        fechas: lista de dates
        values: lista de floats o integeres
        legend: leyenda de la serie
        """
        from copy import deepcopy
        if len(fechas) == 0 or len(values) == 0:
            raise ValueError('fechas y/0 values no tienen datos')
        if len(fechas) != len(values):
            raise ValueError('fechas y values != longitud')
        self.fechas = deepcopy(fechas)
        self.values = deepcopy(values)
        self.legend = legend
        if len(fechas) == 1:
            self.marker = '.'
            self.scatter = 1
        else:
            self.marker = marker
            self.scatter = scatter
        self.linestyle = slinestyle


def XYt_1(t_series: [], stitle: str, ylabel: str, dst: str):
    """
    dibuja un gráfico xy de una o más series

    input
        t_series: lista de objetos Time_series; el primer elemento se
            considera la series principal
        stitle: título del gráfico
        ylabel: título del eje Y
        dst: directorio donde se graba el gráfico (debe existir)
    """
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.ticker import AutoMinorLocator

    dateFmt = mdates.DateFormatter('%d-%m-%Y')
    xminorLocator = AutoMinorLocator()
    yminorLocator = AutoMinorLocator()

    fig, ax = plt.subplots()
    # El primer objeto es el principal
    for ts1 in t_series:
        if ts1.scatter == 0:
            ax.plot(ts1.fechas, ts1.values, marker=ts1.marker,
                    label=ts1.legend, linestyle=ts1.linestyle)
        else:
            ax.plot(ts1.fechas, ts1.values, marker=ts1.marker,
                    label=ts1.legend, linestyle='None')

    ax.xaxis.set_minor_locator(xminorLocator)
    ax.yaxis.set_minor_locator(yminorLocator)
    plt.ylabel(ylabel)
    # rotate and align the tick labels so they look better
    fig.autofmt_xdate()

    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    ax.xaxis.set_major_formatter(dateFmt)
    ax.set_title(stitle)
    plt.legend(loc='best', framealpha=0.5)
    plt.tight_layout()
    plt.grid(True)

    fig.savefig(dst)
    plt.close('all')
