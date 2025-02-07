import java.util.Random;
import java.util.Scanner;

public class CBT_PART_2_QP implements Runnable {
    
	private final Player player1;
    private final Player player2;
    private final Player player3;
    private final Random random = new Random();
    private boolean gameEnded = false;
    
    private final Object lock = new Object(); //Central lock - use this for inter-thread coordination

    public CBT_PART_2_QP(String player1Name, String player2Name, String player3Name) {
        this.player1 = new Player(player1Name, this);
        this.player2 = new Player(player2Name, this);
        this.player3 = new Player(player3Name, this);
    }
    
    /******************** DON'T MODIFY THE CODE OF THIS METHOD *****************
     * 
     * This method initializes the game by dealing one visible 
     * card to each player at the start. It ensures all players begin with a 
     * known initial score and sets the game's starting state. 
     **************************************************************************/
    private void dealInitialCards() {
            int card1 = nextCard();
            player1.totalScore += card1; // Add visible card to the total score
            System.out.println(player1.name + " takes " + card1 + " (visible)");
            
            int card2 = nextCard();
            player2.totalScore += card2; // Add visible card to the total score
            System.out.println(player2.name + " takes " + card2 + " (visible)");
            
            int card3 = nextCard();
            player3.totalScore += card3; // Add visible card to the total score
            System.out.println(player3.name + " takes " + card3 + " (visible)");
            
            /*
             * IMP: The hidden card is given to the players when the dealer 
             * instantiates the Player object 
             */
    }

    /**************************************************************************
     * DON"T MODIFY THE CODE OF THIS METHOD
     * This method generates a random integer between 1 and 10 (inclusive)
     **************************************************************************/
    private int nextCard() {
        return random.nextInt(10) + 1; // Card between 1 and 10
    }
    
    /************************** Q.1 WRITE CODE FOR THIS METHOD (10 M) *********************************
	 * Check Player's Status: The method first determines if the player has already decided 
	 * to pass their turn. If so, it does nothing further for this player. 
	 * Prompt for Action: The method then allows the player to choose their action for the turn. 
	 * The player is presented with two options: 
	 * 		(a) Take a card to increase their score. 
	 * 		(b) Pass, ending their participation in the game. 
	 * Update Player's Status: Based on the player's choice: 
	 * 		(a) If they take a card, their score is updated. 
	 * 		(b) If they pass, they are marked as having finished their participation. 
	 * Once the player completes their turn, the method signals all the players (dealer or players)  
	 * that this player's turn is complete, allowing the next player to proceed.
	 **************************************************************************************************/
    void playTurn(Player player) {
    	/* 
    	 * Write your code below this comment
    	 */
          
    	
    	
    	
            System.out.print(player.name + "'s turn. Current score: " + 
            									player.totalScore + ". (1) Take a card or (2) Pass? :");
            Scanner scanner = new Scanner(System.in);
            int choice = scanner.nextInt();
            
            /* 
        	 * Some more code below this comment
        	 */
        
    }

    /************************** Q.2 WRITE CODE FOR THIS METHOD (10 M) **********************************
     * The determineWinner method identifies the winner of the game once all players have finished 
     * their turns. Here's a step-by-step description: 
     * 1. Collect Player Scores - the method evaluates the final scores of all players. 
     * 2. Check for Valid Scores: It considers only scores that are 21 or less, ignoring players who 
     * 	  exceeded this limit. 
     * 3. Find the Highest Score among the valid scores. 
     * 4. The player with the highest score is identified as the potential winner. 
     * 5. If two or more players have the same highest score, the game ends in a tie with no winner. 
     * 6. The method prints each player's final score and declares the winner or announces a tie. 
     * 7. The game is marked as ended, signaling all threads to conclude. 
     **************************************************************************************************/
    private void determineWinner() {
        
    	/* Some code goes here */ {
            
        	Player[] players = { player1, player2, player3 };
            Player winner = null;
            
            /* 
        	 * Write your code below this comment
        	 */

            System.out.println(player1.name + " has " + player1.totalScore);
            System.out.println(player2.name + " has " + player2.totalScore);
            System.out.println(player3.name + " has " + player3.totalScore);

            /* Specify the condition */  {
                System.out.println(winner.name + " wins with " + winner.totalScore + "!");
            } else {
                System.out.println("No one wins.");
            }
        
            /* 
        	 * Write more code below this comment
        	 */
        }
    }

    /************************** Q.3 WRITE CODE FOR THIS METHOD (05 M) ************************ 
     * The dealer starts by dealing the initial cards.
	 * Then, the dealer enters a loop where it waits for all players to finish their turns.
	 * If all players "PASS", the dealer determines the winner.
	 * If not all players have passed, the dealer waits for the players.
	 ****************************************************************************************/
    public void run() {
    	/* 
    	 * Write your code below this comment
    	 */
    }

    /************************* Q.4 WRITE CODE FOR THIS METHOD (04 M) ********************************
     * The main method:
     * Creates a new game instance with a dealer and three players.
     * Starts the game thread to run the game loop.
     * Starts individual threads for each player.
     ************************************************************************************************/
    public static void main(String[] args) {
    	/* 
    	 * Write your code below this comment
    	 */
    }
    
    /********************************************************************************************* 
     * Inner Player class implementing Runnable, allowing each player to play in its own thread. 
     * *******************************************************************************************/
    class Player implements Runnable {
        String name;
        int hiddenCard;
        int totalScore;
        boolean hasPassed = false;
        Dealer dealer;

        Player(String name, Dealer dealer) {
            this.name = name;
            this.dealer = dealer;
            this.hiddenCard = nextCard();	//The hidden card is given to the player
            this.totalScore = hiddenCard;
            System.out.println(name + " takes " + hiddenCard + " (hidden)");
        }

        /***************************** Q.5 WRITE CODE FOR THIS METHOD (04) ********************
         * The takeCard method:
         * 		Draws a new card and adds its value to the player's total score.
         * 		If the player's score exceeds 21, they automatically pass the game.
         **************************************************************************************/
        void takeCard() {
            int card;
            
            /* 
        	 * Write your code below this comment
        	 */
            
            System.out.println(name + " takes " + card);
            
            /* 
        	 * Write your code below this comment
        	 */
        }

        /********************* Q.6 WRITE CODE FOR THIS METHOD (02 M) **********************
         * The pass method: 
         * 		Marks the player as having passed their turn.
         * 		Prints a message indicating the player has chosen to pass.
         **********************************************************************************/
        void pass() {
        	/* 
        	 * Write your code below this comment
        	 */
        	
        	
            System.out.println(name + " passes.");
        }

        /************************ Q.7 WRITE CODE FOR THIS METHOD (05 M) ********************************
         * The run method of the Player class: 
         * Continuously allows the player to take their turn until they either pass or the game ends. 
         * Calls the game.playTurn() method to handle the player's actions during their turn. 
         * Waits for the next turn using synchronization until notified that it's their turn again.
         **********************************************************************************************/
        public void run() {
        	/* 
        	 * Write your code below this comment
        	 */        
        }
    }    
}
