"""FastAPI web application for the simulation dashboard."""

from pathlib import Path

import plotly.graph_objects as go
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from social_sim.models.basic_economy import BasicEconomyModel, EconomyParams

app = FastAPI(title="Social Simulation Dashboard")

BASE_DIR = Path(__file__).parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

current_model: BasicEconomyModel | None = None
current_params: EconomyParams = EconomyParams()


def create_wealth_distribution_chart(model: BasicEconomyModel) -> str:
    """Create a Plotly chart showing wealth distribution over time."""
    data = model.get_model_data()
    if not data:
        return "{}"

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=data.get("Gini", []),
        mode="lines",
        name="Gini Coefficient",
        line={"color": "#e74c3c"},
    ))

    fig.update_layout(
        title="Wealth Inequality (Gini Coefficient)",
        xaxis_title="Step",
        yaxis_title="Gini",
        yaxis_range=[0, 1],
        template="plotly_white",
        height=300,
        margin={"l": 50, "r": 20, "t": 50, "b": 50},
    )
    return fig.to_json()


def create_metrics_chart(model: BasicEconomyModel) -> str:
    """Create a Plotly chart showing mean wealth and happiness."""
    data = model.get_model_data()
    if not data:
        return "{}"

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=data.get("Mean Wealth", []),
        mode="lines",
        name="Mean Wealth",
        line={"color": "#3498db"},
    ))
    fig.add_trace(go.Scatter(
        y=[h * 20 for h in data.get("Mean Happiness", [])],
        mode="lines",
        name="Mean Happiness (×20)",
        line={"color": "#2ecc71"},
    ))

    fig.update_layout(
        title="Economic Metrics",
        xaxis_title="Step",
        yaxis_title="Value",
        template="plotly_white",
        height=300,
        margin={"l": 50, "r": 20, "t": 50, "b": 50},
    )
    return fig.to_json()


def create_final_distribution_chart(model: BasicEconomyModel) -> str:
    """Create a histogram of final wealth distribution."""
    wealth_values = [a.wealth for a in model.agents]

    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=wealth_values,
        nbinsx=20,
        marker_color="#9b59b6",
    ))

    fig.update_layout(
        title="Final Wealth Distribution",
        xaxis_title="Wealth",
        yaxis_title="Count",
        template="plotly_white",
        height=300,
        margin={"l": 50, "r": 20, "t": 50, "b": 50},
    )
    return fig.to_json()


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Render the main dashboard."""
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "params": current_params,
            "has_results": current_model is not None,
        },
    )


@app.post("/run", response_class=HTMLResponse)
async def run_simulation(
    request: Request,
    num_agents: int = Form(100),
    initial_wealth: float = Form(10.0),
    steps: int = Form(100),
    seed: int = Form(None),
):
    """Run the simulation with given parameters."""
    global current_model, current_params

    current_params = EconomyParams(
        num_agents=num_agents,
        initial_wealth=initial_wealth,
        seed=seed if seed else None,
    )

    current_model = BasicEconomyModel(current_params)
    current_model.run(steps=steps)

    data = current_model.get_model_data()
    final_stats = {
        "steps": steps,
        "final_gini": f"{data['Gini'][-1]:.3f}" if data.get("Gini") else "N/A",
        "mean_wealth": f"{data['Mean Wealth'][-1]:.2f}" if data.get("Mean Wealth") else "N/A",
        "mean_happiness": f"{data['Mean Happiness'][-1]:.3f}" if data.get("Mean Happiness") else "N/A",
    }

    return templates.TemplateResponse(
        "partials/results.html",
        {
            "request": request,
            "stats": final_stats,
            "gini_chart": create_wealth_distribution_chart(current_model),
            "metrics_chart": create_metrics_chart(current_model),
            "distribution_chart": create_final_distribution_chart(current_model),
        },
    )


@app.post("/reset", response_class=HTMLResponse)
async def reset_simulation(request: Request):
    """Reset the simulation."""
    global current_model, current_params
    current_model = None
    current_params = EconomyParams()

    return templates.TemplateResponse(
        "partials/results.html",
        {
            "request": request,
            "stats": None,
            "gini_chart": None,
            "metrics_chart": None,
            "distribution_chart": None,
        },
    )
