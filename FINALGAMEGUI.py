import streamlit as st
import pandas as pd
import random

numberOfPlayers = 5
outputFilename = 'OUTPUT.txt'

# Initialize roundNumber in session state if it's not already initialized
if 'roundNumber' not in st.session_state:
    st.session_state['roundNumber'] = 1

# Initialize the player dictionary and player names input in session state
if 'player' not in st.session_state:
    st.session_state['player'] = {}

if 'player_names_entered' not in st.session_state:
    st.session_state['player_names_entered'] = False

if 'king' not in st.session_state:
    st.session_state['king'] = None

# Initialize numberChosen in session state if it's not already initialized
if 'numberChosen' not in st.session_state:
    st.session_state['numberChosen'] = []

# Calculate Average
def calculateAverage(file, numberChosen):
    avg = sum(numberChosen)/len(st.session_state['player'])
    file.write(f'\nAverage = {avg:.2f}' + '\n')
    file.write(f'\n{avg} * {0.8} = {(avg * 0.8):.2f}' + '\n')
    avg *= 0.8
    file.write(f'\nNew Average = {avg:.2f}' + '\n')
    return avg

# Find Closest
def findClosest(numberChosen, avg):
    closest = min(numberChosen, key=lambda x: abs(x - avg))
    return closest

# Check Elimination
def checkElimination():
    temp = []
    for key, values in st.session_state['player'].items():
        if values[1] <= -10:
            temp.append(key)
    for key in temp:
        st.session_state['player'].pop(key)

    # Displaying results after every round
    df = pd.DataFrame.from_dict(st.session_state['player'], orient='index', columns=['Other', 'Lives Remaining'])
    if not df.empty:
        st.dataframe(df[['Lives Remaining']].transpose())
    else:
        st.write('Every player\'s points are now 0')

# Display Rules
def popuprule(rules):
    displayRules = [
        'Players needs to choose a number between zero and 100. The average of the numbers everyone selected is multiplied by 0.8. The person who chose the number closest to that result is the winner. One point will be deducted from the remaining players, and the round is concluded. When a player reaches negative ten points, they will receive a game over. The last player standing will clear the game. However, every time a player is eliminated, a new rule is added.',
        'If two or more players choose the same number, they will be disqualified from the round and will each lose one point.',
        'Choosing the exact correct number will cause the other players to lose two points instead of one.',
        'If a player chooses zero as their number, the other player will win if they choose 100.'
    ]
    for i in range(0, rules):
        if i == 0:
            st.write(f'<span style="color: #1A86A3;">RULES</span>', unsafe_allow_html=True)
        else:
            st.write(f'<span style="color: #1A86A3;">NEW RULE ({i})</span>', unsafe_allow_html=True)
        st.write(f'<span style="color: #D0D242;">{displayRules[i]}</span>', unsafe_allow_html=True)
        st.write()

# Round Start
def roundStart(prules):
    rules = numberOfPlayers - len(st.session_state['player']) + 1
    skippingAverageCalculation = False
    skippingRule4Condition = False
    skippingRegularRule = False
    roundWinner = ''

    with open(outputFilename, 'w'):
        pass

    with open(outputFilename, 'a') as file:

        # Adding Rule-2
        if rules >= 2:
            seen = set()
            duplicates = []
            for num in st.session_state['numberChosen']:
                if num in seen:
                    if num not in duplicates:
                        duplicates.append(num)
                else:
                    seen.add(num)

            if duplicates:
                file.write('\nTwo or more players have selected the same number. Hence all of them are disqualified from this round.\n' + '\n')
                for key, value in st.session_state['player'].items():
                    if int(value[0]) in duplicates:
                        value[1] -= 1
                skippingAverageCalculation = True
                skippingRule4Condition = True

        # Adding Rule-4
        if rules >= 4:
            if not skippingRule4Condition:
                if (st.session_state['numberChosen'][0] == 0 and st.session_state['numberChosen'][1] == 100) or (st.session_state['numberChosen'][1] == 0 and st.session_state['numberChosen'][0] == 100):
                    for key, value in st.session_state['player'].items():
                        if int(value[0]) == 0:
                            value[1] -= 1
                        else:
                            file.write(f'\nPlayer: {key} wins the round.\n' + '\n')
                    skippingAverageCalculation = True
                elif (st.session_state['numberChosen'][0] == 0 or st.session_state['numberChosen'][1] == 0):
                    for key, value in st.session_state['player'].items():
                        if int(value[0]) != 0:
                            value[1] -= 1
                        else:
                            file.write(f'\nPlayer: {key} wins the round.\n' + '\n')
                    skippingAverageCalculation = True

        if not skippingAverageCalculation:
            avg = calculateAverage(file, st.session_state['numberChosen'])
            closest = findClosest(st.session_state['numberChosen'], avg)

            if st.session_state['numberChosen'].count(closest) > 1:
                file.write(f'\nTwo or more players are closest to the average. Hence King Wins!!!\n' + '\n')
                for key, value in st.session_state['player'].items():
                    if key != st.session_state['king']:
                        value[1] -= 1

                skippingRegularRule = True

            # Adding Rule-3
            elif rules >= 3:
                for key, value in st.session_state['player'].items():
                    if int(avg + 0.5) == int(value[0]):
                        file.write(f'Rounded Average = {int(avg + 0.5)}\n' + '\n')
                        file.write(f'\nPlayer: {key} has correctly predicted the average. Hence deducting 2 points from everyone else.\n' + '\n')
                        for key, value in st.session_state['player'].items():
                            if int(avg + 0.5) != int(value[0]):
                                value[1] -= 2
                        skippingRegularRule = True

            if not skippingRegularRule:
                for key, value in st.session_state['player'].items():
                    if int(value[0]) == closest:
                        file.write(f'\nPlayer: {key} is closest ({int(value[0])})\n' + '\n')
                        roundWinner = key

                for key, value in st.session_state['player'].items():
                    if key != roundWinner:
                        value[1] -= 1

    with open(outputFilename, 'a+') as file:
        file.seek(0)
        contents = file.read()
        st.write(f'<span style="color: #D5DA76;">{contents}</span>', unsafe_allow_html=True)

    checkElimination()
    return prules


# Function to reset the app
def reset_app():
    st.session_state.reset = True
    st.session_state.numbers_submitted = False

# Game Start
def game():
    # If player names have been entered, continue with the game
    if not st.session_state['player_names_entered']:
        st.write('<center> <h1> <span style="color: #38C5C3;">Player Registration</span> </h1> </center>', unsafe_allow_html=True)

        player_names = []
        for i in range(numberOfPlayers):
            name_input = st.text_input(f"Player {i + 1}:", key=f"player_name_{i}")
            if name_input:
                player_names.append(name_input)

        # Once all names are entered, populate player dictionary and randomly select a king
        if len(player_names) == numberOfPlayers:
            # Create player dictionary with initial points
            st.session_state['player'] = {name: [0, 0] for name in player_names}

            # Randomly select a king and save it in session state
            st.session_state['king'] = random.choice(player_names)

            if st.button('Submit Names and Start Game'):
                st.session_state['player_names_entered'] = True
                st.write(f'The game is starting... \n')
                st.write(f'KING: {st.session_state["king"]}')

    # Continue with the game after names are entered
    else:
        prules = 0
        rules = numberOfPlayers - len(st.session_state['player']) + 1

        # Initialize/reset session state
        if 'reset' not in st.session_state:
            st.session_state.reset = False

        if 'numbers_submitted' not in st.session_state:
            st.session_state.numbers_submitted = False

        if len(st.session_state['player']) > 1:
            # Streamlit app layout
            st.write('<center> <h1> <span style="color: #F30B0B;">KING OF DIAMONDS ♦</span> </h1> </center>', unsafe_allow_html=True)
            st.write('<center> <h3> <span style="color: #F30B0B;">GAME OF AVERAGES</span> </h3> </center>', unsafe_allow_html=True)
            if prules != rules:
                popuprule(rules)
                prules = rules
        else:
            st.session_state.numbers_submitted = False
            if not st.session_state['player']:
                st.write('<center> <h1> <span style="color: #F71E1E;">EVERYBODY DIED!!!</span> </h1> </center>', unsafe_allow_html=True)
                st.write('<center> <h1> <span style="color: #F71E1E;">NO WINNER!!!</span> </h1> </center>', unsafe_allow_html=True)
            else:
                st.write('<center> <h1> <span style="color: #E9F43D;">GAME CLEARED!!!</span> </h1> </center>', unsafe_allow_html=True)
                st.write(f'<center> <h1> <span style="color: #54EE4F;">WINNER: {list(st.session_state["player"].keys())[0]}</span> </h1> </center>', unsafe_allow_html=True)
                st.write('<center> <h1> <span style="color: #065B31;">CONGRATULATIONS!!!</span> </h1> </center>', unsafe_allow_html=True)

        # Input Fields for players
        if not st.session_state.reset:
            if len(st.session_state['player']) > 1:
                for name in st.session_state['player'].keys():
                    # Storing the number in session state and getting it from there
                    if f"{name}_number" not in st.session_state:
                        st.session_state[f"{name}_number"] = 0  # Initialize if not present
                    number = st.text_input(f"Player: {name}:", type='password', value=st.session_state[f"{name}_number"])

                    # Store the player's input in session state and update the dictionary
                    st.session_state[f"{name}_number"] = number
                    st.session_state['player'][name][0] = number  # Update the player dictionary with the input value

                # Variable to keep track of whether the submit button has been pressed
                if st.button("Confirm!"):
                    # Display the Field
                    df = pd.DataFrame.from_dict(st.session_state['player'], orient='index', columns=['Number Selected', 'Other'])
                    st.dataframe(df[['Number Selected']].transpose())

                    # Use session state to track the number submission
                    st.session_state.numbers_submitted = True

        if st.session_state.numbers_submitted:
            if st.button("View Results"):
                if len(st.session_state['player']) > 1:
                    st.write(f'<center> <span style="color: #7759DF;">ROUND: {st.session_state["roundNumber"]}</span> </center>', unsafe_allow_html=True)

                    # Collect the chosen numbers into numberChosen in session state
                    st.session_state['numberChosen'] = [int(st.session_state['player'][name][0]) for name in st.session_state['player'].keys()]

                    # Pass numberChosen from session state to roundStart
                    prules = roundStart(prules)

                    # Increment roundNumber in session state
                    st.session_state['roundNumber'] += 1

                    # Clear numberChosen for next round
                    st.session_state['numberChosen'] = []


                    # Add the "Move Next" button to reset the app
                    if st.button("Next Round"):
                        reset_app()

#START
game()
