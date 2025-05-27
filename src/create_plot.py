import pandas as pd
from src.constants import PLOT_OPTIONS, LABEL_CONVERSION, REVERSE_LABEL_CONVERSION

def generate_plot(plot_title, groupby_choice, query, db, fig_view):
    [ax.clear() for ax in fig_view.axes_list]
    df = pd.read_sql_query(query, db.cnx, parse_dates={"fecha_adquisicion": {"format":"%Y-%m-%d"}})

    col_name = PLOT_OPTIONS[plot_title][0]
    col_or_grouper = col_name if plot_title != "Número de equipos por antigüedad" else pd.Grouper(key=col_name, freq="ME")
    gb_col = LABEL_CONVERSION[groupby_choice] if groupby_choice in LABEL_CONVERSION else groupby_choice 
    cmap_choice = "plasma" if not groupby_choice else "viridis"

    if not groupby_choice:
        new_df = df.groupby(col_or_grouper)[col_name].apply(len)

    else:
        if groupby_choice in ["Años", "Meses"]:
            date_format = "%Y" if groupby_choice == "Años" else "%Y-%m"
            df[groupby_choice] = df["fecha_adquisicion"].apply(lambda x: x.strftime(date_format))

        new_df = df.groupby([col_or_grouper, gb_col])[col_name].apply(len).unstack()

        if plot_title == "Número de equipos por antigüedad":
            rng = pd.date_range(new_df.index.min(), new_df.index.max(), name=gb_col, freq="ME")
            new_df = new_df.reindex(rng)
        
        new_df.fillna(0, inplace=True)

    if plot_title == "Número de equipos por antigüedad":
        new_df.index = new_df.index.strftime("%Y-%m")

    new_df.plot(ax=fig_view.axes_list[0],
                kind="bar", colormap=cmap_choice,
                rot=0,
                alpha=0.6,
                edgecolor="black",
                linewidth=1.0,
                title=plot_title,
                xlabel=REVERSE_LABEL_CONVERSION[col_name],
                ylabel="Número de equipos")

    if plot_title == "Número de equipos por antigüedad":
        fig_view.axes_list[0].tick_params(axis="x", labelrotation=45)

    for container in fig_view.axes_list[0].containers:
        l_type = "edge" if plot_title == "Número de equipos por antigüedad" else "center"
        fig_view.axes_list[0].bar_label(container, label_type=l_type, fmt=lambda x: int(x) if x > 0 else "")

    fig_view.axes_list[0].yaxis.get_major_locator().set_params(integer=True)

    if groupby_choice:
        leg_title = REVERSE_LABEL_CONVERSION[gb_col] if gb_col in REVERSE_LABEL_CONVERSION else groupby_choice
        fig_view.axes_list[0].legend(title=leg_title)

    fig_view.fig_canvas.draw()