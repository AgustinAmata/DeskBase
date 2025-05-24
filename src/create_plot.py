import pandas as pd

def generate_plot(plot_title, query, db, fig_view):
    [ax.clear() for ax in fig_view.axes_list]
    if plot_title == "Número de equipos por antigüedad":
        df = pd.read_sql_query(query, db.cnx, parse_dates={"fecha_adquisicion": {"format":"%Y-%m-%d"}})
        df.set_index(pd.DatetimeIndex(df["fecha_adquisicion"].values), inplace=True)
        df = df.groupby(pd.Grouper(freq="ME")).count()
        df.set_index(df.index.strftime("%Y-%m"), inplace=True)
        fig_view.axes_list[0].bar(x=df.index, height=df["fecha_adquisicion"])
        fig_view.axes_list[0].tick_params(axis="x", labelrotation=45)

    else:
        df = pd.read_sql_query(query, db.cnx)
        col_name = df.columns[1]
        df = df.groupby(col_name).count().rename(columns={df.columns[0]: "count"})
        fig_view.axes_list[0].bar(x=df.index, height=df["count"])

    fig_view.axes_list[0].yaxis.get_major_locator().set_params(integer=True)
    fig_view.axes_list[0].set_title(plot_title)
    fig_view.fig_canvas.draw()