"""FastAPI web application for the simulation dashboard."""

from pathlib import Path

import plotly.graph_objects as go
from fastapi import FastAPI, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from social_sim.models.basic_economy import (
    BasicEconomyModel,
    DisasterParams,
    EducationParams,
    EconomyParams,
    IncomeParams,
    TaxBracket,
    TaxParams,
)
from social_sim.web.api import router as api_router

app = FastAPI(title="Nation Builder")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

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


def create_tax_chart(model: BasicEconomyModel) -> str:
    """Create a chart showing tax revenue and UBI amount over time."""
    data = model.get_model_data()
    if not data:
        return "{}"

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=data.get("Tax Revenue", []),
        mode="lines",
        name="Tax Revenue",
        line={"color": "#e67e22"},
    ))
    fig.add_trace(go.Scatter(
        y=data.get("UBI Amount", []),
        mode="lines",
        name="UBI per Person",
        line={"color": "#1abc9c"},
    ))

    fig.update_layout(
        title="Taxation & Redistribution",
        xaxis_title="Step",
        yaxis_title="Amount",
        template="plotly_white",
        height=300,
        margin={"l": 50, "r": 20, "t": 50, "b": 50},
    )
    return fig.to_json()


def create_lorenz_chart(model: BasicEconomyModel) -> str:
    """Create a Lorenz curve showing wealth inequality."""
    import numpy as np

    wealth_values = sorted(a.wealth for a in model.agents)
    n = len(wealth_values)
    if n == 0:
        return "{}"

    total_wealth = sum(wealth_values)
    if total_wealth == 0:
        cumulative_wealth = [0.0] * n
    else:
        cumulative_wealth = list(np.cumsum(wealth_values) / total_wealth)

    population_pct = [(i + 1) / n * 100 for i in range(n)]
    wealth_pct = [w * 100 for w in cumulative_wealth]

    population_pct = [0] + population_pct
    wealth_pct = [0] + wealth_pct

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=[0, 100],
        y=[0, 100],
        mode="lines",
        name="Perfect Equality",
        line={"color": "#95a5a6", "dash": "dash"},
    ))

    fig.add_trace(go.Scatter(
        x=population_pct,
        y=wealth_pct,
        mode="lines",
        name="Lorenz Curve",
        fill="toself",
        fillcolor="rgba(52, 152, 219, 0.2)",
        line={"color": "#3498db"},
    ))

    fig.update_layout(
        title="Lorenz Curve (Wealth Distribution)",
        xaxis_title="Cumulative Population (%)",
        yaxis_title="Cumulative Wealth (%)",
        xaxis_range=[0, 100],
        yaxis_range=[0, 100],
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
    enable_income: str | None = Form(None),
    base_income: float = Form(1.0),
    enable_tax: str | None = Form(None),
    tax_rate_1: float = Form(0.0),
    tax_rate_2: float = Form(0.1),
    tax_rate_3: float = Form(0.2),
    tax_rate_4: float = Form(0.3),
    enable_ubi: str | None = Form(None),
    enable_disaster: str | None = Form(None),
    disaster_probability: float = Form(1.0),
    disaster_damage: float = Form(20.0),
    enable_education: str | None = Form(None),
    education_rate: float = Form(10.0),
    max_productivity: float = Form(3.0),
):
    """Run the simulation with given parameters."""
    global current_model, current_params

    income_enabled = enable_income == "true"
    tax_enabled = enable_tax == "true"
    ubi_enabled = enable_ubi == "true"
    disaster_enabled = enable_disaster == "true"
    education_enabled = enable_education == "true"

    income_params = IncomeParams(
        enabled=income_enabled,
        base_income=base_income,
    )

    tax_params = TaxParams(
        enabled=tax_enabled,
        brackets=[
            TaxBracket(threshold=0, rate=tax_rate_1 / 100),
            TaxBracket(threshold=10, rate=tax_rate_2 / 100),
            TaxBracket(threshold=30, rate=tax_rate_3 / 100),
            TaxBracket(threshold=50, rate=tax_rate_4 / 100),
        ],
        ubi_enabled=ubi_enabled,
    )

    disaster_params = DisasterParams(
        enabled=disaster_enabled,
        probability=disaster_probability / 100,
        damage_rate=disaster_damage / 100,
    )

    education_params = EducationParams(
        enabled=education_enabled,
        investment_rate=education_rate / 100,
        max_productivity=max_productivity,
    )

    current_params = EconomyParams(
        num_agents=num_agents,
        initial_wealth=initial_wealth,
        seed=seed if seed else None,
        income=income_params,
        tax=tax_params,
        disaster=disaster_params,
        education=education_params,
    )

    current_model = BasicEconomyModel(current_params)
    current_model.run(steps=steps)

    data = current_model.get_model_data()
    disaster_count = sum(1 for d in data.get("Disaster Damage", []) if d > 0) if disaster_enabled else 0
    total_disaster_damage = sum(data.get("Disaster Damage", [])) if disaster_enabled else 0
    final_stats = {
        "steps": steps,
        "final_gini": f"{data['Gini'][-1]:.3f}" if data.get("Gini") else "N/A",
        "mean_wealth": f"{data['Mean Wealth'][-1]:.2f}" if data.get("Mean Wealth") else "N/A",
        "mean_happiness": f"{data['Mean Happiness'][-1]:.3f}" if data.get("Mean Happiness") else "N/A",
        "total_income": f"{data['Total Income'][-1]:.2f}" if data.get("Total Income") and income_enabled else None,
        "income_enabled": income_enabled,
        "tax_revenue": f"{data['Tax Revenue'][-1]:.2f}" if data.get("Tax Revenue") and tax_enabled else None,
        "ubi_amount": f"{data['UBI Amount'][-1]:.2f}" if data.get("UBI Amount") and ubi_enabled else None,
        "tax_enabled": tax_enabled,
        "ubi_enabled": ubi_enabled,
        "disaster_enabled": disaster_enabled,
        "disaster_count": disaster_count,
        "total_disaster_damage": f"{total_disaster_damage:.2f}" if disaster_enabled else None,
        "education_enabled": education_enabled,
        "mean_productivity": f"{data['Mean Productivity'][-1]:.2f}" if data.get("Mean Productivity") else None,
    }

    return templates.TemplateResponse(
        "partials/results.html",
        {
            "request": request,
            "stats": final_stats,
            "gini_chart": create_wealth_distribution_chart(current_model),
            "metrics_chart": create_metrics_chart(current_model),
            "distribution_chart": create_final_distribution_chart(current_model),
            "tax_chart": create_tax_chart(current_model) if tax_enabled else None,
            "lorenz_chart": create_lorenz_chart(current_model),
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


@app.get("/health")
async def health_check():
    return JSONResponse({"status": "ok"})
