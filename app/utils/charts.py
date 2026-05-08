import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def line_chart(df: pd.DataFrame, x: str, y: str, title: str, color: str | None = None, yaxis_label: str = "") -> go.Figure:
    fig = px.line(
        df,
        x=x,
        y=y,
        color=color,
        title=title,
        markers=True,
        labels={y: yaxis_label or y, x: x},
    )
    fig.update_layout(
        template="plotly_white",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=-0.3),
    )
    return fig


def bar_chart(df: pd.DataFrame, x: str, y: str, title: str, color: str | None = None, yaxis_label: str = "") -> go.Figure:
    fig = px.bar(
        df,
        x=x,
        y=y,
        color=color,
        title=title,
        labels={y: yaxis_label or y, x: x},
        barmode="group",
    )
    fig.update_layout(template="plotly_white")
    return fig


def beta_universe_bar(df: pd.DataFrame, metric: str, title: str) -> go.Figure:
    cols = ["ticker", metric]
    if "company_name" in df.columns:
        cols.append("company_name")
    sub = df[cols].dropna(subset=[metric]).sort_values(metric, ascending=False)

    hover_data = {"company_name": True} if "company_name" in sub.columns else {}

    fig = px.bar(
        sub,
        x="ticker",
        y=metric,
        title=title,
        labels={metric: metric, "ticker": "Ticker"},
        color="ticker",
        text_auto=".2f",
        hover_data=hover_data,
    )
    fig.update_layout(template="plotly_white", showlegend=False)
    return fig
