import numpy as np
import random

# ===== CONFIGURATION =====
# Set your network architecture here
INPUT_NEURONS = 9   # Number of input features
HIDDEN_LAYERS = [16512, 16512, 4128]  # Number of neurons in each hidden layer [layer1, layer2, layer3]
OUTPUT_NEURONS = 4   # Number of output actions (e.g., hit, stand, double, split)

LEARN_RATE = 0.001
NUM_DECKS = 6  # Number of decks in the shoe
# Performance tuning
# When False the (very large) neural network won't be allocated at startup.
ENABLE_NEURAL_NETWORK = False
# How often to print progress (increase to reduce IO overhead). Default changed
# from 1 to 10_000 to avoid printing every hand which is extremely slow.
PROGRESS_INTERVAL = 1_000_000
# =========================

# ===== CARD AND DECK FUNCTIONS =====
card_categories = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
card_list = [2, 3, 4, 5, 6, 7, 8, 9, 10, 'J', 'Q', 'K', 'A']

# Cache rank->value mapping for faster lookups
_rank_value_map = { 'J': 10, 'Q': 10, 'K': 10, 'A': 11 }
for i in range(2, 11):
    _rank_value_map[i] = i

def card_value(card):
    """Get the value of a card for blackjack"""
    # card is stored as (rank, suit) where rank can be int or str
    rank = card[0]
    # Fast path for integer ranks
    if isinstance(rank, int):
        return rank

    # Look up in precomputed map (face cards and numeric strings)
    if rank in _rank_value_map:
        return _rank_value_map[rank]

    # As a last resort try to parse numeric strings like '10'
    try:
        return int(rank)
    except Exception:
        # Unknown rank: return 10 as a safe default for face-like values
        return 10

def get_count_value(card):
    """Hi-Lo counting system: low cards +1, high cards -1, neutral 0"""
    value = card_value(card)
    if value >= 2 and value <= 6:
        return 1
    elif value >= 10:
        return -1
    else:
        return 0

# ===== SHOE CLASS (Multiple Decks with Card Counting) =====
class Shoe:
    def __init__(self, num_decks):
        self.num_decks = num_decks
        self.reset()
    
    def reset(self):
        """Create and shuffle a new shoe"""
        # Precompute single deck (52 cards) and multiply by number of decks.
        one_deck = [(card, category) for category in card_categories for card in card_list]
        self.cards = one_deck * self.num_decks
        random.shuffle(self.cards)
        self.running_count = 0
        self.cards_dealt = 0
    
    def deal_card(self):
        """Deal one card and update count"""
        if len(self.cards) == 0:
            self.reset()
        card = self.cards.pop()
        self.running_count += get_count_value(card)
        self.cards_dealt += 1
        return card
    
    def get_true_count(self):
        """Calculate true count (running count / decks remaining)"""
        decks_remaining = len(self.cards) / 52
        if decks_remaining < 0.5:
            return 0  # Don't divide by very small numbers
        return self.running_count / decks_remaining
    
    def get_cards_remaining(self):
        """Get number of cards remaining"""
        return len(self.cards)
    
    def get_decks_remaining(self):
        """Get number of decks remaining"""
        return len(self.cards) / 52

# ===== HAND EVALUATION =====
class Hand:
    def __init__(self):
        self.cards = []
    
    def add_card(self, card):
        """Add a card to the hand"""
        self.cards.append(card)
    
    def get_value(self):
        """Get the best possible value of the hand"""
        total = 0
        aces = 0
        
        for card in self.cards:
            value = card_value(card)
            if value == 11:  # Ace
                aces += 1
                total += 11
            else:
                total += value
        
        # Adjust for aces
        while total > 21 and aces > 0:
            total -= 10
            aces -= 1
        
        return total
    
    def is_soft(self):
        """Check if hand is soft (contains Ace counted as 11)"""
        total = 0
        aces = 0
        
        for card in self.cards:
            value = card_value(card)
            if value == 11:
                aces += 1
                total += 11
            else:
                total += value
        
        # Check if we can reduce an ace without going under 21
        if aces > 0 and total > 21:
            # Try reducing aces
            test_total = total
            test_aces = aces
            while test_total > 21 and test_aces > 0:
                test_total -= 10
                test_aces -= 1
            # If still has ace counted as 11, it's soft
            return test_total <= 21 and test_aces > 0
        
        return aces > 0 and total <= 21
    
    def is_busted(self):
        """Check if hand is busted"""
        return self.get_value() > 21
    
    def can_split(self):
        """Check if hand can be split (two cards of same value)"""
        if len(self.cards) != 2:
            return False
        return card_value(self.cards[0]) == card_value(self.cards[1])
    
    def is_blackjack(self):
        """Check if hand is blackjack"""
        return len(self.cards) == 2 and self.get_value() == 21

# ===== FEATURE EXTRACTION =====
def extract_features(player_hand, dealer_visible_card, shoe):
    """
    Extract the 9 input features for the neural network:
    1. Player hand total
    2. Dealer's visible card value (1-11)
    3. True count or running count
    4. Number of cards in player's hand (2-21)
    5. Soft hand indicator (1 if soft, 0 if hard)
    6. Can double down (1 if yes, 0 if no)
    7. Can split (1 if yes, 0 if no)
    8. Cards remaining in shoe (normalized to 0-1)
    9. Number of decks remaining
    """
    features = np.zeros((INPUT_NEURONS, 1))
    
    # Feature 1: Player hand total (normalize by dividing by 21)
    player_total = player_hand.get_value()
    features[0] = player_total / 21.0
    
    # Feature 2: Dealer's visible card value (1-11, normalized)
    dealer_card_val = card_value(dealer_visible_card)
    features[1] = dealer_card_val / 11.0
    
    # Feature 3: True count (normalize - typical range is -10 to +10, so divide by 10)
    true_count = shoe.get_true_count()
    features[2] = np.clip(true_count / 10.0, -1.0, 1.0)  # Clip to reasonable range
    
    # Feature 4: Number of cards in player's hand (normalize by dividing by 21)
    num_cards = len(player_hand.cards)
    features[3] = num_cards / 21.0
    
    # Feature 5: Soft hand indicator (1 if soft, 0 if hard)
    features[4] = 1.0 if player_hand.is_soft() else 0.0
    
    # Feature 6: Can double down (1 if yes, 0 if no) - can only double with exactly 2 cards
    features[5] = 1.0 if len(player_hand.cards) == 2 else 0.0
    
    # Feature 7: Can split (1 if yes, 0 if no)
    features[6] = 1.0 if player_hand.can_split() else 0.0
    
    # Feature 8: Cards remaining in shoe (normalized to 0-1)
    total_cards_start = NUM_DECKS * 52
    cards_remaining = shoe.get_cards_remaining()
    features[7] = cards_remaining / total_cards_start
    
    # Feature 9: Number of decks remaining (normalize by dividing by NUM_DECKS)
    decks_remaining = shoe.get_decks_remaining()
    features[8] = decks_remaining / NUM_DECKS
    
    # Return features
    return features
# ===== NEURAL NETWORK INITIALIZATION (lazy) =====
"""
w = weights, b = bias, i = input, h = hidden, o = output
This repository originally allocated a very large network at import time which
caused huge startup time and memory usage. We lazily initialize the network
only when it's first needed (e.g., when use_ai=True in play_hand).
"""
NUM_HIDDEN_LAYERS = len(HIDDEN_LAYERS)

# Placeholders for network parameters. They will be created by init_network().
weights = None
biases = None
network_initialized = False

def init_network():
    """Initialize weights and biases for the neural network.

    This is intentionally lazy: call it only when the AI is actually used.
    """
    global weights, biases, network_initialized
    if network_initialized:
        return

    weights = []
    biases = []

    # Weights and biases from input to first hidden layer
    weights.append(np.random.randn(HIDDEN_LAYERS[0], INPUT_NEURONS) * np.sqrt(1 / INPUT_NEURONS))
    biases.append(np.zeros((HIDDEN_LAYERS[0], 1)))

    # Weights and biases between hidden layers
    for i in range(NUM_HIDDEN_LAYERS - 1):
        weights.append(np.random.randn(HIDDEN_LAYERS[i + 1], HIDDEN_LAYERS[i]) * np.sqrt(1 / HIDDEN_LAYERS[i]))
        biases.append(np.zeros((HIDDEN_LAYERS[i + 1], 1)))

    # Weights and biases from last hidden layer to output
    weights.append(np.random.randn(OUTPUT_NEURONS, HIDDEN_LAYERS[-1]) * np.sqrt(1 / HIDDEN_LAYERS[-1]))
    biases.append(np.zeros((OUTPUT_NEURONS, 1)))

    network_initialized = True
    if ENABLE_NEURAL_NETWORK:
        print(f"Neural Network Initialized:")
        print(f"  Input neurons: {INPUT_NEURONS}")
        print(f"  Hidden layers: {NUM_HIDDEN_LAYERS} ({HIDDEN_LAYERS})")
        print(f"  Output neurons: {OUTPUT_NEURONS}")
        print(f"  Learning rate: {LEARN_RATE}")

# ===== FORWARD PROPAGATION FUNCTION =====
def forward_propagation(input_data):
    """
    Performs forward propagation through the network
    input_data: numpy array of shape (INPUT_NEURONS, 1)
    returns: (output predictions, list of all layer activations)
    """
    # Ensure input is in the right shape
    if input_data.ndim == 1:
        input_data = input_data.reshape(INPUT_NEURONS, 1)
    # Lazy-init the network if needed
    if not network_initialized:
        init_network()
    
    # Store all activations for backpropagation
    activations = [input_data]
    current_input = input_data
    
    # Forward propagation through all hidden layers
    for i in range(len(weights) - 1):  # All layers except output
        layer_pre = biases[i] + weights[i] @ current_input
        layer_activation = 1 / (1 + np.exp(-layer_pre))  # Sigmoid activation
        activations.append(layer_activation)
        current_input = layer_activation
    
    # Forward propagation to output layer
    output_pre = biases[-1] + weights[-1] @ current_input
    output = 1 / (1 + np.exp(-output_pre))  # Sigmoid activation
    activations.append(output)
    
    return output, activations

# ===== BACKWARD PROPAGATION FUNCTION =====
def backward_propagation(activations, output_pred, label):
    """
    Performs backpropagation to update weights and biases
    activations: list of all layer activations from forward pass (including input)
    output_pred: numpy array of shape (OUTPUT_NEURONS, 1)
    label: numpy array of shape (OUTPUT_NEURONS, 1) - expected output
    """
    global weights, biases
    # Lazy-init the network if needed
    if not network_initialized:
        init_network()
    
    # Ensure label is in the right shape
    if label.ndim == 1:
        label = label.reshape(OUTPUT_NEURONS, 1)
    
    # Calculate delta for output layer
    delta = output_pred - label
    
    # Backpropagate through all layers (starting from output and going backwards)
    for layer_idx in range(len(weights) - 1, -1, -1):
        # Update weights and biases for current layer
        weights[layer_idx] += -LEARN_RATE * delta @ np.transpose(activations[layer_idx])
        biases[layer_idx] += -LEARN_RATE * delta
        
        # Calculate delta for previous layer (if not at input layer)
        if layer_idx > 0:
            # Derivative of sigmoid: sigmoid(x) * (1 - sigmoid(x))
            sigmoid_derivative = activations[layer_idx] * (1 - activations[layer_idx])
            delta = np.transpose(weights[layer_idx]) @ delta * sigmoid_derivative

# ===== BETTING SYSTEM =====
def calculate_bet(chips, true_count, base_bet=5, max_bet=5000):
    """
    Calculate bet based on true count (EXTREME scaling)
    VERY safe when count is low, EXTREMELY aggressive when count is high
    """
    # Extreme betting strategy - maximum difference between low and high counts
    
    # Defensive: coerce to float
    try:
        tc = float(true_count)
    except Exception:
        tc = 0.0

    # If the count is extremely high, go to the table maximum (subject to chips)
    AGGRESSIVE_COUNT_THRESHOLD = 5
    if tc >= AGGRESSIVE_COUNT_THRESHOLD:
        bet = min(max_bet, chips)
        bet = max(1, round(bet))
        return bet

    if tc <= -3:
        # Extremely negative count - bet absolute minimum (almost skip hand)
        bet = base_bet * 0.25  # Quarter bet - very conservative
    elif tc <= -2:
        # Very negative count - bet very little
        bet = base_bet * 0.4
    elif tc <= -1:
        # Negative count - bet less than base
        bet = base_bet * 0.6
    elif tc <= 0:
        # Neutral/slightly negative - bet base (still being cautious)
        bet = base_bet * 0.8
    elif tc <= 0.5:
        # Slightly positive - start betting more
        bet = base_bet * 1.5
    elif tc <= 1:
        # Positive - bet 3x
        bet = base_bet * 3
    elif tc <= 1.5:
        # Good count - bet 5x
        bet = base_bet * 5
    elif tc <= 2:
        # Very good count - bet 8x
        bet = base_bet * 8
    elif tc <= 2.5:
        # Excellent count - bet 12x
        bet = base_bet * 12
    elif tc <= 3:
        # Amazing count - bet 16x
        bet = base_bet * 16
    elif tc <= 4:
        # Incredible count - bet 20x
        bet = base_bet * 20
    elif tc <= 5:
        # Phenomenal count - bet 25x
        bet = base_bet * 25
    else:
        # EXTREMELY high count - bet MAXIMUM aggression
        # Scale: 25x base for count 5, then +5x per additional count point
        multiplier = 25 + int((tc - 5) * 5)
        bet = base_bet * multiplier
    
    # Cap at maximum bet
    bet = min(bet, max_bet)
    
    # Can't bet more than we have
    bet = min(bet, chips)
    
    # Round to nearest integer (bets should be whole numbers)
    bet = round(bet)
    
    # Ensure we always bet at least 1 chip (minimum possible bet)
    bet = max(1, bet)
    
    return bet

# ===== BASIC STRATEGY =====
def basic_strategy(player_hand, dealer_value):
    """
    Returns optimal action based on basic strategy
    0 = Hit, 1 = Stand, 2 = Double, 3 = Split
    """
    player_value = player_hand.get_value()
    num_cards = len(player_hand.cards)
    is_soft = player_hand.is_soft()
    can_split = player_hand.can_split() and num_cards == 2
    
    # Splitting pairs (when dealer shows 2-6, split most pairs)
    if can_split:
        card_val = card_value(player_hand.cards[0])
        if card_val == 11:  # Aces
            return 3  # Always split aces
        elif card_val == 8:  # Eights
            return 3  # Always split eights
        elif card_val in [2, 3, 6, 7]:
            if dealer_value <= 6:
                return 3  # Split against weak dealer
        elif card_val == 9:
            if dealer_value in [2, 3, 4, 5, 6, 8, 9]:
                return 3  # Split 9s except against 7, 10, A
    
    # Hard totals (no ace or ace counted as 1)
    if not is_soft:
        # Double down opportunities (only with 2 cards)
        if num_cards == 2:
            if player_value == 11:
                return 2  # Always double 11
            elif player_value == 10:
                if dealer_value <= 9:
                    return 2  # Double 10 vs 2-9
            elif player_value == 9:
                if dealer_value in [3, 4, 5, 6]:
                    return 2  # Double 9 vs 3-6
        
        # Hard totals strategy (any number of cards)
        if player_value >= 17:
            return 1  # Stand on 17+
        elif player_value <= 11:
            return 0  # Always hit 11 or less
        elif player_value == 12:
            if dealer_value >= 4 and dealer_value <= 6:
                return 1  # Stand on 12 vs 4-6
            else:
                return 0  # Hit otherwise
        elif player_value in [13, 14, 15, 16]:
            if dealer_value >= 2 and dealer_value <= 6:
                return 1  # Stand vs 2-6
            else:
                return 0  # Hit vs 7-A
    
    # Soft totals (ace counted as 11)
    if is_soft:
        # Double down opportunities (only with 2 cards)
        if num_cards == 2:
            if player_value == 17:
                if dealer_value in [3, 4, 5, 6]:
                    return 2  # Double soft 17 vs 3-6
            elif player_value in [15, 16]:
                if dealer_value in [4, 5, 6]:
                    return 2  # Double soft 15-16 vs 4-6
            elif player_value == 13 or player_value == 14:
                if dealer_value in [5, 6]:
                    return 2  # Double soft 13-14 vs 5-6
        
        # Soft totals strategy (any number of cards)
        if player_value >= 19:
            return 1  # Stand on soft 19+
        elif player_value == 18:
            if dealer_value == 9 or dealer_value == 10 or dealer_value == 11:
                return 0  # Hit soft 18 vs 9, 10, A
            else:
                return 1  # Stand otherwise
        else:
            return 0  # Hit soft 17 or less
    
    # Default: hit
    return 0

# ===== BLACKJACK GAME SIMULATION =====
def play_hand(shoe, bet, use_ai=True, use_basic_strategy=False):
    """
    Play a single hand of blackjack
    Returns: (result, chips_change, additional_bet, is_blackjack, features_used, actions_taken)
    result: 1 if win, -1 if loss, 0 if push
    chips_change: actual chips won/lost (winnings only, not including bet returned)
    additional_bet: additional chips to deduct for double down
    is_blackjack: True if player got blackjack
    use_ai: Use neural network for decisions
    use_basic_strategy: Use basic strategy (if not using AI)
    """
    # Deal initial cards
    player_hand = Hand()
    dealer_hand = Hand()
    
    player_hand.add_card(shoe.deal_card())
    dealer_hand.add_card(shoe.deal_card())  # Dealer's visible card
    player_hand.add_card(shoe.deal_card())
    dealer_hand.add_card(shoe.deal_card())  # Dealer's hidden card
    dealer_visible = dealer_hand.cards[0]  # Dealer's visible card
    
    player_blackjack = player_hand.is_blackjack()
    
    # Check for blackjack
    if player_blackjack:
        # Check dealer's hand (peek at hidden card)
        if dealer_hand.is_blackjack():
            return 0, 0, 0, True, [], []  # Push, no change
        return 1, bet * 1.5, 0, True, [], []  # Blackjack pays 3:2
    
    features_list = []
    actions_list = []
    doubled_down = False
    actual_bet = bet
    additional_bet = 0  # For double down
    
    # Player's turn
    while True:
        if player_hand.is_busted():
            return -1, -actual_bet, additional_bet, False, features_list, actions_list  # Player busted, lose bet
        
        # Extract features
        features = extract_features(player_hand, dealer_visible, shoe)
        features_list.append(features)
        
        # Get decision (0=Hit, 1=Stand, 2=Double, 3=Split)
        if use_ai:
            output, _ = forward_propagation(features)
            action = np.argmax(output)
        elif use_basic_strategy:
            # Use basic strategy
            dealer_card_value = card_value(dealer_visible)
            action = basic_strategy(player_hand, dealer_card_value)
            
            # Validate action is legal
            if action == 2 and len(player_hand.cards) != 2:
                action = 0  # Can't double if not 2 cards
            if action == 3 and not player_hand.can_split():
                action = 0  # Can't split if not valid
        else:
            # Random action for training data generation
            valid_actions = [0, 1]  # Hit and Stand always available
            if len(player_hand.cards) == 2:
                valid_actions.append(2)  # Double down
            if player_hand.can_split():
                valid_actions.append(3)  # Split
            action = random.choice(valid_actions)
        
        actions_list.append(action)
        
        if action == 1:  # Stand
            break
        elif action == 0:  # Hit
            player_hand.add_card(shoe.deal_card())
        elif action == 2:  # Double down
            player_hand.add_card(shoe.deal_card())
            additional_bet = bet  # Need to pay additional bet amount
            actual_bet = bet * 2  # Total bet is doubled
            doubled_down = True
            break  # Must stand after double
        elif action == 3:  # Split (simplified - treat as hit for now)
            player_hand.add_card(shoe.deal_card())
    
    if player_hand.is_busted():
        return -1, -actual_bet, additional_bet, False, features_list, actions_list
    
    # Dealer's turn (must hit on 16, stand on 17+) 
    # Note: Some casinos hit on soft 17, but for simplicity we'll stand on all 17s
    # This is actually better for the player (fewer dealer busts on soft 17)
    while dealer_hand.get_value() < 17:
        dealer_hand.add_card(shoe.deal_card())
        if dealer_hand.is_busted():
            return 1, actual_bet, additional_bet, False, features_list, actions_list  # Dealer busted, win bet
    
    # Compare hands
    player_value = player_hand.get_value()
    dealer_value = dealer_hand.get_value()
    
    if player_value > dealer_value:
        return 1, actual_bet, additional_bet, False, features_list, actions_list
    elif player_value < dealer_value:
        return -1, -actual_bet, additional_bet, False, features_list, actions_list
    else:
        return 0, 0, additional_bet, False, features_list, actions_list  # Push

# ===== ACTION ENCODING =====
def action_to_label(action):
    """Convert action number to one-hot encoded label"""
    label = np.zeros((OUTPUT_NEURONS, 1))
    label[action] = 1.0
    return label

# ===== SIMULATION =====
if __name__ == "__main__":
    # Configuration
    TOTAL_HANDS = 100_000_000_000
    STARTING_CHIPS = 5000000000000
    BASE_BET = 1
    MAX_BET = 50000
    # Initialize
    shoe = Shoe(NUM_DECKS)
    chips = STARTING_CHIPS
    
    # Statistics tracking
    stats = {
        'wins': 0,
        'losses': 0,
        'pushes': 0,
        'blackjacks': 0,
        'total_won': 0,
        'total_lost': 0,
        'biggest_win': 0,
        'biggest_loss': 0,
        'hands_played': 0,
        'chips_history': []
    }
    
    print("="*70)
    print("BLACKJACK SIMULATION - 1 MILLION HANDS")
    print("="*70)
    print(f"Starting chips: ${STARTING_CHIPS:,}")
    print(f"Bet range: ${BASE_BET} - ${MAX_BET:,}")
    print(f"Strategy: Basic Strategy with Card Counting")
    print("="*70)
    print()
    
    # Main simulation loop
    for hand_num in range(1, TOTAL_HANDS + 1):
        # Reshuffle if needed (when less than 25% of shoe remains)
        if shoe.get_cards_remaining() < NUM_DECKS * 52 * 0.25:
            shoe.reset()
        
        # Check if player has enough chips (need at least 1 chip to bet)
        if chips < 1:
            print(f"\nOut of chips at hand {hand_num:,}!")
            break
        
        # Calculate bet based on true count
        true_count = shoe.get_true_count()
        bet = calculate_bet(chips, true_count, BASE_BET, MAX_BET)
        
        # Place bet (deduct from chips)
        chips -= bet
        
        # Play hand with basic strategy
        result, chips_change, additional_bet, is_blackjack, features_used, actions_taken = play_hand(shoe, bet, use_ai=False, use_basic_strategy=True)
        
        # Calculate total bet placed
        total_bet = bet + additional_bet
        
        # Deduct additional bet for double down (if any) - this is the extra bet amount
        chips -= additional_bet
        
        # Update chips: chips_change is profit (positive) or loss (negative)
        # For wins: chips_change is profit, add back total bet + profit
        # For losses: chips_change is negative (loss), but we need to account that we already deducted total_bet
        # For pushes: chips_change is 0, get total bet back
        
        if result == 1:  # Win - chips_change is positive profit
            chips += total_bet + chips_change
        elif result == -1:  # Loss - chips_change is negative, but we already deducted total_bet
            # chips_change already accounts for the loss, we don't add anything back
            # The chips are already reduced by total_bet, and chips_change shows the loss amount
            pass
        else:  # Push - get bet back, no profit/loss
            chips += total_bet
        
        # Net change for statistics (profit/loss for this hand)
        if result == 1:
            net_change = chips_change  # Profit (positive)
        elif result == -1:
            net_change = chips_change  # Loss (negative, already negative from play_hand)
        else:
            net_change = 0  # Push
        
        # Update statistics
        stats['hands_played'] += 1
        if is_blackjack:
            stats['blackjacks'] += 1
        
        if result == 1:  # Win
            stats['wins'] += 1
            stats['total_won'] += abs(net_change)
            stats['biggest_win'] = max(stats['biggest_win'], abs(net_change))
        elif result == -1:  # Loss
            stats['losses'] += 1
            stats['total_lost'] += abs(net_change)
            stats['biggest_loss'] = max(stats['biggest_loss'], abs(net_change))
        else:  # Push
            stats['pushes'] += 1
        
        # Progress update every 10k hands
        if hand_num % PROGRESS_INTERVAL == 0:
            hands_won = stats['wins']
            hands_lost = stats['losses']
            hands_played = stats['hands_played']
            win_rate = (hands_won / hands_played * 100) if hands_played > 0 else 0
            
            print(f"Hand {hand_num:,} | Chips: ${chips:,.2f} | "
                  f"Won: {hands_won:,} | Lost: {hands_lost:,} | "
                  f"Win Rate: {win_rate:.2f}% | "
                  f"Net: ${chips - STARTING_CHIPS:+,.2f}")
    
    # Final Statistics
    print("\n" + "="*70)
    print("FINAL STATISTICS")
    print("="*70)
    print(f"Starting Chips:     ${STARTING_CHIPS:,.2f}")
    print(f"Ending Chips:       ${chips:,.2f}")
    print(f"Net Profit/Loss:    ${chips - STARTING_CHIPS:+,.2f}")
    print(f"Return on Investment: {(chips - STARTING_CHIPS) / STARTING_CHIPS * 100:+.2f}%")
    print()
    print(f"Total Hands Played:  {stats['hands_played']:,}")
    print(f"Wins:               {stats['wins']:,} ({stats['wins'] / stats['hands_played'] * 100:.2f}%)")
    print(f"Losses:             {stats['losses']:,} ({stats['losses'] / stats['hands_played'] * 100:.2f}%)")
    print(f"Pushes:             {stats['pushes']:,} ({stats['pushes'] / stats['hands_played'] * 100:.2f}%)")
    print()
    print(f"Total Won:          ${stats['total_won']:,.2f}")
    print(f"Total Lost:         ${stats['total_lost']:,.2f}")
    print(f"Biggest Win:         ${stats['biggest_win']:,.2f}")
    print(f"Biggest Loss:        ${stats['biggest_loss']:,.2f}")
    print()
    print(f"Blackjacks:          {stats['blackjacks']:,} ({stats['blackjacks'] / stats['hands_played'] * 100:.4f}%)")
    print(f"Average per Hand:    ${(chips - STARTING_CHIPS) / stats['hands_played']:+.4f}")
    print("="*70)
