import random
import customtkinter as ctk
import cv2
import easyocr
import numpy as np
import matplotlib.pyplot as plt

# --------------------------
# Original Blackjack Game Code
# --------------------------

# Points of cards
cards = {
    'A': 11, '2': 2, '3': 3, '4': 4, '5': 5, 
    '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
    'J': 10, 'Q': 10, 'K': 10
}

nocards = dict.fromkeys(cards, 4)

# Sample space
deck = list(cards.keys()) * 4  # Simulating a full deck
random.shuffle(deck)

win = {}
st = {}
los = {}

def remove_cards(l, k, nocards):
    for i in l:
        nocards[i] -= 1
    for i in k:
        nocards[i] -= 1

def blackjack(player, score):
    if score == 21:
        output(f"{player} wins!!")
        disable_choice_buttons()

def Calc(score, nocards, cards, deck):
    if score >= 10:
        guaranteed = 21 - score

        # Events
        setofwinning = [key for key, value in cards.items() if value == guaranteed]
        setofstaying = [key for key, value in cards.items() if value < guaranteed]
        setoflosing = [key for key, value in cards.items() if value > guaranteed]

        # prob
        probofwinning = probofstaying = proboflosing = 0

        for i in setofwinning:
            win[i] = nocards[i]
            probofwinning += nocards[i] / len(deck)
        output(f"probability of winning for sure: {format(probofwinning*100, '.2f')}%")

        for i in setofstaying:
            st[i] = nocards[i]
            probofstaying += nocards[i] / len(deck)
        output(f"probability of staying in the game: {format(probofstaying*100, '.2f')}%")

        for i in setoflosing:
            los[i] = nocards[i]
            proboflosing += nocards[i] / len(deck)
        output(f"probability of losing for sure (going beyond 21): {format(proboflosing*100, '.2f')}%")
    else:
        output("probability of you staying in thee game provided you hit is 1")
        output("so hit ra pussy")

def Calc_d(dealer_hand, nocards, cards, deck):
    dealer_diff = 16 - cards[dealer_hand[0]]

    probofhit = probofstand = 0
    setofhit = [key for key, value in cards.items() if value <= dealer_diff]
    setofstand = [key for key, value in cards.items() if value > dealer_diff]

    for i in setofhit:
        probofhit += nocards[i] / (len(deck) + 1)
    for i in setofstand:
        probofstand += nocards[i] / (len(deck) + 1)
    
    output(f"probability of dealer hitting: {format(probofhit*100, '.2f')}%")
    output(f"probability of dealer standing: {format(probofstand*100, '.2f')}%")

# Global game state variables for GUI
player_hand = []
dealer_hand = []
player_score = 0
dealer_score = 0

# Create the main window
app = ctk.CTk()
app.geometry("600x600")
app.title("Blackjack Game")

# Create a text box to display output (simulating console prints)
output_box = ctk.CTkTextbox(app, width=580, height=350)
output_box.pack(padx=10, pady=10)
output_box.configure(state="disabled")  # read-only

def output(text):
    """Append text to the output box."""
    output_box.configure(state="normal")
    output_box.insert("end", text + "\n")
    output_box.see("end")
    output_box.configure(state="disabled")

# Modify choice buttons enabling/disabling to include the new OCR button
def disable_choice_buttons():
    hit_button.configure(state="disabled")
    stand_button.configure(state="disabled")
    try:
        ocr_button.configure(state="disabled")
    except NameError:
        pass

def enable_choice_buttons():
    hit_button.configure(state="normal")
    stand_button.configure(state="normal")
    try:
        ocr_button.configure(state="normal")
    except NameError:
        pass

def start_game():
    global deck, player_hand, dealer_hand, player_score, dealer_score, nocards, win, st, los
    # Reset global game state
    nocards = dict.fromkeys(cards, 4)
    deck = list(cards.keys()) * 4  # full deck
    random.shuffle(deck)
    win = {}
    st = {}
    los = {}
    
    # Initial hands
    player_hand = [deck.pop(), deck.pop()]
    dealer_hand = [deck.pop(), deck.pop()]
    remove_cards(player_hand, dealer_hand, nocards)
    
    # Calculate scores
    player_score = sum(cards[card] for card in player_hand)
    dealer_score = sum(cards[card] for card in dealer_hand)
    
    # Adjust for Aces
    if player_score > 21 and 'Ace' in player_hand:
        player_score -= 10
    if dealer_score > 21 and 'Ace' in dealer_hand:
        dealer_score -= 10

    # Clear output box and print initial hands
    output_box.configure(state="normal")
    output_box.delete("1.0", "end")
    output_box.configure(state="disabled")
    
    output("Player Hand: " + str(player_hand) + " Score: " + str(player_score))
    output("Dealer Hand: " + str([dealer_hand[0], "Hidden"]) + " Score: ?")
    
    blackjack('player', player_score)
    
    output("")
    output("Player Turn")
    output("Your Probabilities: ")
    Calc(player_score, nocards, cards, deck)
    output("")
    output("Dealers Probabilities (wrt hidden card)")
    Calc_d(dealer_hand, nocards, cards, deck)
    output("")
    output("Enter choice (h/s): (Use the buttons below)")
    
    enable_choice_buttons()

def player_hit():
    global player_score
    disable_choice_buttons()
    new_card = deck.pop()
    player_hand.append(new_card)
    player_score += cards[new_card]
    if player_score > 21 and 'Ace' in player_hand:
        player_score -= 10
    output("Player Hits: " + new_card + " New Score: " + str(player_score))
    dealer_play()

def player_stand():
    disable_choice_buttons()
    dealer_play()

def dealer_play():
    global dealer_score
    if dealer_score > 16:
        output("Dealer Stands")
    else:
        while dealer_score < 17:
            new_card = deck.pop()
            dealer_hand.append(new_card)
            dealer_score += cards[new_card]
            if dealer_score > 21 and 'Ace' in dealer_hand:
                dealer_score -= 10
        output("Dealer Reveals: " + str(dealer_hand) + " Score: " + str(dealer_score))
    
    output("")
    # Determine winner
    if player_score > 21:
        output("Player Busted! Dealer Wins!")
    elif dealer_score > 21:
        output("Dealer Busted! Player Wins!")
    elif player_score > dealer_score:
        output("Player Wins!")
    elif dealer_score > player_score:
        output("Dealer Wins!")
    else:
        output("It's a Tie!")
    
    disable_choice_buttons()

# New Buttons to display win, st, and los dictionaries with explanations
def show_win():
    explanation = ("Winning probabilities are calculated by considering the cards that, "
                   "when added to your current score, give you exactly 21. For each such card, "
                   "the probability is computed as (number of that card remaining) / (total cards remaining).")
    output("Win Dictionary: " + str(win))
    output(explanation)

def show_st():
    explanation = ("Staying probabilities consider cards that, when drawn, keep your total score "
                   "below 21. For each such card, the probability is (number of that card remaining) / (total cards remaining).")
    output("Staying Dictionary: " + str(st))
    output(explanation)

def show_los():
    explanation = ("Losing probabilities are based on cards that would cause your score to exceed 21. "
                   "For each such card, the probability is (number of that card remaining) / (total cards remaining).")
    output("Losing Dictionary: " + str(los))
    output(explanation)

# --------------------------
# OCR Integration Code
# --------------------------
def recognize_card(image_path):
    """
    Uses EasyOCR to process the given image and extract a card rank.
    The function crops the top-left corner of the image (adjust if needed),
    and then processes it to improve contrast before OCR.
    Returns a string corresponding to a key in the 'cards' dictionary.
    """
    reader = easyocr.Reader(['en'])
    image = cv2.imread(image_path)
    if image is None:
        output("Error: Image not found.")
        return None
    h, w, _ = image.shape
    # Define crop region (adjust these parameters if needed)
    crop_x, crop_y, crop_w, crop_h = 0, 0, int(w * 0.25), int(h * 0.25)
    cropped = image[crop_y:crop_h, crop_x:crop_w]
    
    # Preprocessing
    gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)
    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
    )
    kernel = np.ones((3, 3), np.uint8)
    processed = cv2.dilate(thresh, kernel, iterations=1)
    
    # Run OCR on processed image
    result = reader.readtext(processed, detail=1, text_threshold=0.5, low_text=0.4)
    if not result:
        output("No card detected.")
        return None
    detected_text = result[0][1]
    output("Detected Text from image: " + detected_text)
    
    # Extract the card rank from the detected text.
    card_rank = None
    if detected_text.startswith("10"):
        card_rank = "10"
    else:
        # Use the first character as the card rank
        if detected_text[0] in cards:
            card_rank = detected_text[0]
        else:
            card_rank = detected_text[0]  # fallback option
    if card_rank not in cards:
        output("Recognized card rank is not valid: " + card_rank)
        return None
    return card_rank

def ocr_player_hit():
    """
    Uses OCR to recognize a card from an image and then processes it as a player's hit.
    """
    global player_score
    disable_choice_buttons()
    image_path = "7D.jpg"  # Change this path if needed
    recognized_card = recognize_card(image_path)
    if recognized_card is None:
        output("OCR did not recognize a valid card. Please try again.")
        enable_choice_buttons()
        return
    # Add the recognized card to player's hand
    player_hand.append(recognized_card)
    player_score += cards[recognized_card]
    # Update card count in nocards
    if recognized_card in nocards and nocards[recognized_card] > 0:
        nocards[recognized_card] -= 1
    else:
        output("Card " + recognized_card + " not available in deck.")
    output("Player OCR Hits: " + recognized_card + " New Score: " + str(player_score))
    dealer_play()

# --------------------------
# GUI Buttons
# --------------------------
start_button = ctk.CTkButton(app, text="Start Game", command=start_game)
start_button.pack(pady=5)

hit_button = ctk.CTkButton(app, text="Hit", command=player_hit, state="disabled")
hit_button.pack(pady=5)

stand_button = ctk.CTkButton(app, text="Stand", command=player_stand, state="disabled")
stand_button.pack(pady=5)

ocr_button = ctk.CTkButton(app, text="OCR Hit Card", command=ocr_player_hit, state="disabled")
ocr_button.pack(pady=5)

win_button = ctk.CTkButton(app, text="Show Win Probabilities", command=show_win)
win_button.pack(pady=5)

st_button = ctk.CTkButton(app, text="Show Staying Probabilities", command=show_st)
st_button.pack(pady=5)

los_button = ctk.CTkButton(app, text="Show Losing Probabilities", command=show_los)
los_button.pack(pady=5)

# --------------------------
# (Optional) Display the cropped image using matplotlib for debugging
# Uncomment the lines below if you want to see the processed image.
# cropped_rgb = cv2.cvtColor(cv2.imread("7D.jpg")[0:int(cv2.imread("7D.jpg").shape[0]*0.25), 0:int(cv2.imread("7D.jpg").shape[1]*0.25)], cv2.COLOR_BGR2RGB)
# plt.imshow(cropped_rgb)
# plt.axis("off")
# plt.show()
# --------------------------

app.mainloop()