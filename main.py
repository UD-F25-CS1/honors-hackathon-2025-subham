from bakery import assert_equal
from drafter import *
from dataclasses import dataclass

from meta import *

# hide_debug_information()
# set_website_framed(False)
set_website_title("Your Drafter Website")
set_site_information(
    "author",
    """
Your description can go here.
""",
    [],
    [],
    [],
)

from drafter import *
from dataclasses import dataclass
import random
import matplotlib.pyplot as plt

# --- 1. State Management ---
@dataclass
class State:
    day: int
    cash: float
    computer_profit: float
    message: str
    
    # Tracking transaction costs for the Red/Green display
    last_expected_cost: float
    last_actual_cost: float
    
    # Stock 1 Data
    s1_price: float
    s1_shares: int
    s1_history: list[float]
    
    # Stock 2 Data
    s2_price: float
    s2_shares: int
    s2_history: list[float]

def get_net_worth(state: State) -> float:
    return state.cash + (state.s1_shares * state.s1_price) + (state.s2_shares * state.s2_price)

# --- 2. Route Handlers ---

@route
def buy_stock_1(state: State, qty1: str, qty2: str = "0") -> Page:
    # We accept qty2="0" so the function doesn't crash if the browser sends it extra
    try:
        quantity = int(qty1)
    except ValueError:
        state.message = "Invalid quantity for Stock 1."
        return index(state)

    if quantity <= 0:
        state.message = "Must buy at least 1 share."
        return index(state)

    market_cost = quantity * state.s1_price
    # SCAM: 25% Markup
    actual_cost = market_cost * 1.25 
    scam_profit = actual_cost - market_cost

    if state.cash >= actual_cost:
        state.cash -= actual_cost
        state.s1_shares += quantity
        state.computer_profit += scam_profit
        state.message = f"Purchased {quantity} shares of Stock 1."
        
        # Record data for the Green/Red display
        state.last_expected_cost = market_cost
        state.last_actual_cost = actual_cost
    else:
        state.message = "Insufficient funds for Stock 1."

    return index(state)

@route
def buy_stock_2(state: State, qty2: str, qty1: str = "0") -> Page:
    # We accept qty1="0" so the function doesn't crash
    try:
        quantity = int(qty2)
    except ValueError:
        state.message = "Invalid quantity for Stock 2."
        return index(state)

    if quantity <= 0:
        state.message = "Must buy at least 1 share."
        return index(state)

    stock_cost = quantity * state.s2_price
    # SCAM: Flat Fee
    hidden_fee = 50.0
    total_cost = stock_cost + hidden_fee

    if state.cash >= total_cost:
        state.cash -= total_cost
        state.s2_shares += quantity
        state.computer_profit += hidden_fee
        state.message = f"Purchased {quantity} shares of Stock 2."
        
        # Record data for the Green/Red display
        state.last_expected_cost = stock_cost
        state.last_actual_cost = total_cost
    else:
        state.message = "Insufficient funds for Stock 2."

    return index(state)

@route
def next_day(state: State, qty1: str = "0", qty2: str = "0") -> Page:
    state.day += 1
    state.message = f"Welcome to Day {state.day}."
    
    # Reset transaction display for the new day
    state.last_expected_cost = 0.0
    state.last_actual_cost = 0.0

    # Update Stock 1 (Rigged to crash 30-50%)
    growth_1 = random.uniform(0.50, 0.70) 
    state.s1_price *= growth_1
    state.s1_history.append(state.s1_price)

    # Update Stock 2 (Rigged to crash 40-60%)
    growth_2 = random.uniform(0.40, 0.60)
    state.s2_price *= growth_2
    state.s2_history.append(state.s2_price)

    return index(state)

@route
def results_page(state: State, qty1: str = "0", qty2: str = "0") -> Page:
    net_worth = get_net_worth(state)
    profit_loss = net_worth - 100 
    status = "You lost money!" if profit_loss < 0 else "You lost money!"
    
    content = [
        Header("Final Trading Results"),
        Div(
            Header(f"Your Final Net Worth: ${net_worth:.2f}", 2),
            Header(f"Computer's Hidden Profit: ${state.computer_profit:.2f}", 3),
            f"Result: {status}",
        ),
        Button("Return to Market", index)
    ]
    return Page(state, content)

# --- 3. The Index Page ---

@route
def index(state: State) -> Page:
    
    net_worth = get_net_worth(state)
    card_style = "border: 1px solid #ccc; padding: 15px; margin: 10px; border-radius: 8px;"

    # --- Plot 1: SafeCorp ---
    plt.close('all')  # Clear previous plots
    plt.figure()      # Create NEW figure for Plot 1
    plt.plot(state.s1_history, color='green')
    plt.title(f"SafeCorp: ${state.s1_price:.2f}")
    plt.xlabel("Day")
    plt.ylabel("Price")
    # FIX: Remove arguments. It grabs the figure we just created above.
    plot1_component = MatPlotLibPlot() 

    # --- Plot 2: RocketMoon ---
    plt.figure()      # Create NEW figure for Plot 2
    plt.plot(state.s2_history, color='purple')
    plt.title(f"RocketMoon: ${state.s2_price:.2f}")
    plt.xlabel("Day")
    plt.ylabel("Price")
    # FIX: Remove arguments. It grabs the figure we just created above.
    plot2_component = MatPlotLibPlot()

    # --- Transaction Analysis Display ---
    if state.last_actual_cost > 0:
        transaction_analysis = Div(
            Header("Last Transaction Analysis", 4),
            Span("What you expected to pay: ", style="font-weight: bold;"),
            Span(f"${state.last_expected_cost:.2f}", style="color: green; font-weight: bold; font-size: 1.2em;"),
            LineBreak(),
            Span("What you ACTUALLY paid: ", style="font-weight: bold;"),
            Span(f"${state.last_actual_cost:.2f}", style="color: red; font-weight: bold; font-size: 1.2em;"),
            style="border: 2px dashed red; padding: 10px; margin: 15px; background-color: #fff0f0; text-align: center;"
        )
    else:
        transaction_analysis = Div("") 

    # --- Stock Sections ---
    stock1_section = Div(
        Header("Stock 1: SafeCorp", 3),
        plot1_component,
        Div(
            "This stock grows steadily. A safe bet!", LineBreak(),
            "Current Price: $", f"{state.s1_price:.2f}", LineBreak(),
            "Your Shares: ", str(state.s1_shares), LineBreak(),
            "Buy Amount: ", TextBox("qty1", "0"),
            Button("Invest in Stock 1", buy_stock_1),
        ),
        style=card_style
    )

    stock2_section = Div(
        Header("Stock 2: RocketMoon", 3),
        plot2_component,
        Div(
            "High risk, high reward? To the moon!", LineBreak(),
            "Current Price: $", f"{state.s2_price:.2f}", LineBreak(),
            "Your Shares: ", str(state.s2_shares), LineBreak(),
            "Buy Amount: ", TextBox("qty2", "0"),
            Button("Invest in Stock 2", buy_stock_2),
        ),
        style=card_style
    )

    # --- Main Assembly ---
    return Page(state, [
        Header("Predatory Trader 3000"),
        
        # Status Bar
        Div(
            Span(f"Day: {state.day}", " | "),
            Span(f"Cash: ${state.cash:.2f}", " | "),
            Span(f"Net Worth: ${net_worth:.2f}"),
            style="background-color: #eee; padding: 15px; font-size: 1.2em;"
        ),
        
        # Feedback Message
        Div(state.message, style="color: blue; padding: 10px; font-style: italic;"),
        
        # Analysis Box
        transaction_analysis,

        # Layout
        Row(stock1_section, stock2_section),
        
        HorizontalRule(),
        
        # Game Controls
        Div(
            Button("Next Day (Update Market)", next_day),
            Span("    "), 
            Button("View Final Results", results_page),
            style="padding: 20px; text-align: center;"
        )
    ])

# --- 4. Initialization ---

initial_state = State(
    day=1,
    cash=1000.0,
    computer_profit=0.0,
    message="Welcome! Invest your money wisely...",
    # Initialize the new tracking variables
    last_expected_cost=0.0,
    last_actual_cost=0.0,
    s1_price=50.0,
    s1_shares=0,
    s1_history=[50.0],
    s2_price=20.0,
    s2_shares=0,
    s2_history=[20.0]
)

hide_debug_information()
set_website_framed(False)
start_server(initial_state)
