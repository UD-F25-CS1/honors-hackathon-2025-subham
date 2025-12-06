# --- 3. The Index Page ---

@route
def index(state: State) -> Page:
    
    net_worth = get_net_worth(state)
    card_style = "border: 1px solid #ccc; padding: 15px; margin: 10px; border-radius: 8px;"

    # --- Plot 1: SafeCorp ---
    # 1. Clear any existing data on the plot
    plt.clf() 
    
    # 2. Draw the first plot
    plt.plot(state.s1_history, color='green')
    plt.title(f"SafeCorp: ${state.s1_price:.2f}")
    plt.xlabel("Day")
    plt.ylabel("Price")
    
    # 3. Capture it into a component
    plot1_component = MatPlotLibPlot() 

    # --- Plot 2: RocketMoon ---
    # 4. CRITICAL: Clear the plot again so Stock 1 data doesn't appear on Stock 2's chart
    plt.clf()
    
    # 5. Draw the second plot
    plt.plot(state.s2_history, color='purple')
    plt.title(f"RocketMoon: ${state.s2_price:.2f}")
    plt.xlabel("Day")
    plt.ylabel("Price")
    
    # 6. Capture the second component
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
