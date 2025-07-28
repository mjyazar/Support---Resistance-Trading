import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def plot_unified_chart(df, levels, volume_profile, symbol):
    """
    Plots the candlestick chart with S/R levels and a horizontal volume profile.
    """
    # Use make_subplots to create a 1-row, 2-column figure.
    # The main chart will be wider than the volume profile.
    fig = make_subplots(rows=1, cols=2,
                        column_widths=[0.85, 0.15],
                        shared_yaxes=True,
                        horizontal_spacing=0.01)

    # 1. Add Candlestick trace to the first subplot (row 1, col 1)
    fig.add_trace(go.Candlestick(x=df["datetime"],
                                 open=df["open"],
                                 high=df["high"],
                                 low=df["low"],
                                 close=df["close"],
                                 name="Price"),
                  row=1, col=1)

    # 2. Plot static levels on the first subplot
    if 'poc' in levels:
        fig.add_hline(y=levels['poc'], line_width=2, line_dash="solid",
                      line_color="purple", name="POC", row=1, col=1)

    if 'hvns' in levels:
        for hvn in levels['hvns']:
            fig.add_hline(y=hvn, line_width=1, line_dash="solid",
                          line_color="blue", name="HVN", row=1, col=1)

    # 3. Plot dynamic Pivot Point levels on the first subplot
    if 'pivots' in levels:
        pivots_df = levels['pivots']
        pivots_to_plot = pivots_df[pivots_df['datetime'].isin(df['datetime'])]
        for col in ['r3', 'r2', 'r1', 'pivot', 's1', 's2', 's3']:
            fig.add_trace(go.Scatter(x=pivots_to_plot['datetime'],
                                     y=pivots_to_plot[col],
                                     mode='lines', name=col.upper(),
                                     line=dict(width=1, dash='dot')),
                          row=1, col=1)

    # 4. Plot Fractal levels on the first subplot
    if 'fractals' in levels:
        fractal_df = levels['fractals']
        fractals_to_plot = fractal_df[fractal_df['datetime'].isin(df['datetime'])]
        highs = fractals_to_plot.dropna(subset=['fractal_high'])
        fig.add_trace(go.Scatter(x=highs['datetime'], y=highs['fractal_high'],
                                 mode='markers', marker=dict(symbol='triangle-down', color='red', size=8),
                                 name='Fractal High'),
                      row=1, col=1)
        lows = fractals_to_plot.dropna(subset=['fractal_low'])
        fig.add_trace(go.Scatter(x=lows['datetime'], y=lows['fractal_low'],
                                 mode='markers', marker=dict(symbol='triangle-up', color='green', size=8),
                                 name='Fractal Low'),
                      row=1, col=1)

    # 5. Add Volume Profile bars to the second subplot (row 1, col 2)
    fig.add_trace(go.Bar(
        y=volume_profile['price_midpoint'],
        x=volume_profile['volume'],
        orientation='h',
        name='Volume Profile',
        marker_color='rgba(169, 169, 169, 0.5)'  # lightgrey with transparency
    ), row=1, col=2)

    # 6. Finalize layout
    fig.update_layout(
        title=f'<b>{symbol} - Unified S/R Analysis</b>',
        xaxis_title='Date',
        yaxis_title='Price (USDT)',
        xaxis_rangeslider_visible=False,
        template='plotly_white',
        legend_title="Levels",
        height=700,
        showlegend=True
    )

    # Hide x-axis labels, title, and grid for the volume profile subplot
    fig.update_xaxes(title_text="", showticklabels=False, row=1, col=2)

    fig.show()