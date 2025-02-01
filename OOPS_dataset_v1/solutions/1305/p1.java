package Questions;

import java.io.*;
import java.util.*;
import java.io.*;
import java.util.*;



		class Player {
		    private String playerName;
		    private Role role;
		    private int runsScored;
		    private int wicketsTaken;
		    private String teamName;

		    public Player(String playerName, Role role, int runsScored, int wicketsTaken, String teamName) {
		        this.playerName = playerName;
		        this.role = role;
		        this.runsScored = runsScored;
		        this.wicketsTaken = wicketsTaken;
		        this.teamName = teamName;
		    }

		    public String getPlayerName() {
		        return playerName;
		    }

		    public void setPlayerName(String playerName) {
		        this.playerName = playerName;
		    }

		    public Role getRole() {
		        return role;
		    }

		    public void setRole(Role role) {
		        this.role = role;
		    }

		    public int getRunsScored() {
		        return runsScored;
		    }

		    public void setRunsScored(int runsScored) {
		        this.runsScored = runsScored;
		    }

		    public int getWicketsTaken() {
		        return wicketsTaken;
		    }

		    public void setWicketsTaken(int wicketsTaken) {
		        this.wicketsTaken = wicketsTaken;
		    }

		    public String getTeamName() {
		        return teamName;
		    }

		    public void setTeamName(String teamName) {
		        this.teamName = teamName;
		    }

		    @Override
		    public String toString() {
		        return "Player{" +
		               "playerName='" + playerName + '\'' +
		               ", role=" + role +
		               ", runsScored=" + runsScored +
		               ", wicketsTaken=" + wicketsTaken +
		               ", teamName='" + teamName + '\'' +
		               '}';
		    }

		    public String toCsvFormat() {
		        return String.format("%s,%s,%d,%d,%s",
		                playerName, role, runsScored, wicketsTaken, teamName);
		    }
		}

		enum Role {
		    BATSMAN, BOWLER, ALL_ROUNDER;

		    public static Role fromString(String role) {
		        switch (role.toUpperCase().replace("-", "_")) {
		            case "BATSMAN":
		                return BATSMAN;
		            case "BOWLER":
		                return BOWLER;
		            case "ALL_ROUNDER":
		                return ALL_ROUNDER;
		            default:
		                throw new IllegalArgumentException("Unknown role: " + role);
		        }
		    }
		}

		class RunsComparator implements Comparator<Player> {
			/************************** Q.1 WRITE CODE FOR THIS METHOD *********************************/
		    public int compare(Player p1, Player p2) {
		       Comparable Com = new Comparable();
		       int Com = CompareTo(P1,P2);
		       if(P1.runsScored()>P2.runsScored()){
		    	   return -1;
		    	   else if(P1.runsScored()<P2.runsScored()){
		    		   return 1;
		       }
		    	   else if(P1.runsScored()<P2.runsScored()){
		    		   return 0;
		    	   }else{
		    		   System.out.println("");
		    	   }
		       
		       
		    }
		}

		class CricketDataHandler {
		    
			private static final int[] Teams = null;

			/************************** Q.2 WRITE CODE FOR THIS METHOD *********************************/
			public List<Player> readPlayersFromFile(String fileName) throws IOException {
		        
				LinkedList<String>Player = new LinkedList<>();
				
				Player player = new Player(fileName, null, 0, 0, fileName);
				Player.add("Jasprit Bumrah");
				Player.add("Adam zampa");
				Player.add("Pat Cummins");
				Player.add("Jofra archer");
				Player.add("Mitchel Starc");
				Player.add("Chris woaks");
				Player.add("Ravindra jadeja");
				Player.add("Joe Root");
				Player.add("Steve Smith");
				Player.add("Kl Rahul");
				Player.add("Sam curran");
				Player.add("Rohit sharma");
				Player.add("Virat kohli");
				Player.add("David warner");
				Player.add("Marcus Stonis");
				Player.add("Ben stokes");
				Player.add("Shubham gill");
				Player.add("Jason roy");
				Player.add("Jos buttler");
				Player.add("Glenn maxwell");
				Player.add("Hardik pandaya");
				
				System.out.println(Player);
				Player.add("Jackson smith");
		
for(int i = 0;i<=Player.size();i++){
	System.out.println(i);
}
				
		    }

			/************************** Q.3 WRITE CODE FOR THIS METHOD *********************************/
		    public void writePlayersToFile(String fileName, List<Player> players) throws IOException {
			
		    	
		    	
		    	
		    	
		    	
		    	
		    }
		    
			/************************** Q.4 WRITE CODE FOR THIS METHOD *********************************/
		    public void updatePlayerStats(List<Player> players, String playerName, int runs, int wickets) {
		        // Question 4: Write code for updating player stats [Total: 5 marks]
		        // Step 1: Go through each player in the list. [1 mark]
		        // Step 2: Check if the current player's name matches the given name. [1 mark]
		        // Step 3: If it matches, update the player's runs with the new value. Updated value will be the sum of the old runs and the argument runs. [1 mark]
		        // Step 4: Similarly, update the player's wickets with the new value. Updated value will be the sum of the old wickets and the argument wickets. [1 mark]
		        // Step 5: If no player matches the given name, throw an IllegalArgumentException exception. [1 mark]
		    }

			/************************** Q.5 WRITE CODE FOR THIS METHOD *********************************/
		    public double calculateTeamAverageRuns(List<Player> players, String teamName) {
		        HashMap<Integer,String> teams = new HashMap<Integer,String>();
		        
		    	teams.put(21,"India");
				teams.put(129,"Australia");
				teams.put(331,"Australia");
				teams.put(45,"England");
				teams.put(334,"Australia");
				teams.put(1501,"England");
				teams.put(2447,"India");
			teams.put(6241,"England");
				teams.put(5083,"Australia");
				teams.put(4973,"India");
				teams.put(256,"India");
				teams.put(9837,"India");
				teams.put(12251,"India");
				teams.put(6030,"Australia");
				teams.put(1384,"Australia");
				teams.put(4867,"England");
				teams.put(1919,"India");
				teams.put(4271,"England");
				teams.put(4245,"England");
				teams.put(3490,"Australia");
				teams.put(1513,"India");
				
				System.out.println(teams);
				
				
				
				int Avg = (teams.size());
				int TotalIndianPlayers = 7;
				int TotalAustralianPlayers = 7;
				int TotalEnglandPlayers = 5;

				int Totalruns;
				int Noofplayers;
				
				Avg = Totalruns/Noofplayers;
		if(){
	
		}
		    	
		    	
		    	try{
		    		
		    		int i;
		    		Teams[i] = teams.size();
		    		
		    		System.out.println(i);
		    		
		    	}catch(IllegalArgumentException e){
		    		
		    	System.out.println(e);
		    	
		 
		    }
		}

		@FunctionalInterface
		interface PlayerFilter<T> {
		    List<Player> filter(List<Player> players, T value);
		}

		class TeamFilterStrategy implements PlayerFilter<String> {
		    
			/************************** Q.6 WRITE CODE FOR THIS METHOD *********************************/
		    public List<Player> filter(List<Player> players, String teamName) {
		       
		    	 HashMap<String,String> teams = new HashMap<String,String>();
			        
			    	teams.put("Jasprit Bumrah","India");
					teams.put("Adam zampa","Australia");
					teams.put("Pat Cummins","Australia");
					teams.put("Jofra archer","England");
					teams.put("Mitchel Starc","Australia");
					teams.put("Chris woaks","England");
					teams.put("Ravindra jadeja","India");
				teams.put("Joe Root","England");
					teams.put("Steve Smith","Australia");
					teams.put("Kl Rahul","India");
					teams.put("Sam curran","India");
					teams.put("Rohit sharma","India");
					teams.put("Virat kohli","India");
					teams.put("David warner","Australia");
					teams.put("Marcus Stonis","Australia");
					teams.put("Ben stokes","England");
					teams.put("Shubham gill","India");
					teams.put("Jason roy","England");
					teams.put("Jos buttler","England");
					teams.put("Glenn maxwell","Australia");
					teams.put("Hardik pandaya","India");
					
					System.out.println(teams);
		    	
		    	
		    	
		    	
		    	
		    	
		    	
		    	
		    	
		    }
		}

		class AllRounderStatsFilter implements PlayerFilter<int[]> {
		    
			/************************** Q.7 WRITE CODE FOR THIS METHOD *********************************/
		    public List<Player> filter(List<Player> players, int[] criteria) {
		        LinkedList<String>Player = new LinkedList<>();
		    	 HashMap<String,String> teams = new HashMap<String,String>();

		    	for(int i = 0;i<=Player.size();i++){
		    		if(i==Player.size()){
		    			System.out.println(i);
		    		}else{
		    			System.out.println("NULL");
		    		}
		    	}
		    	
		    	
		    	
		    	teams.put("Jasprit Bumrah","India");
					teams.put("Adam zampa","Australia");
					teams.put("Pat Cummins","Australia");
					teams.put("Jofra archer","England");
					teams.put("Mitchel Starc","Australia");
					teams.put("Chris woaks","England");
					teams.put("Ravindra jadeja","India");
				teams.put("Joe Root","England");
					teams.put("Steve Smith","Australia");
					teams.put("Kl Rahul","India");
					teams.put("Sam curran","India");
					teams.put("Rohit sharma","India");
					teams.put("Virat kohli","India");
					teams.put("David warner","Australia");
					teams.put("Marcus Stonis","Australia");
					teams.put("Ben stokes","England");
					teams.put("Shubham gill","India");
					teams.put("Jason roy","England");
					teams.put("Jos buttler","England");
					teams.put("Glenn maxwell","Australia");
					teams.put("Hardik pandaya","India");
		    	
		    	
		    	
		    	
		    	
		    	
		    	
		    	
		    	
		    }
		}

		public class CBT_PART_1_QP {
		    private void printPlayers(String header, List<Player> players) {
		        System.out.println("\n--- " + header + " ---");
		        for (Player player : players) {
		            System.out.println(player);
		        }
		    }

		    public void main(String[] args) {
		        CricketDataHandler dataHandler = new CricketDataHandler();
		        List<Player> players = new ArrayList<>();

		        try {
		            // Read data from file
		            players = dataHandler.readPlayersFromFile("inputCricketData.csv");
		        } catch (FileNotFoundException e) {
		            System.out.println("Error: File not found.");
		            return;
		        } catch (IOException e) {
		            System.out.println("Error: Unable to read file.");
		            return;
		        }

		        // Perform a series of cricket analytics operations

		        // Search players by team
		        PlayerFilter<String> teamFilter = new TeamFilterStrategy();
		        List<Player> indianPlayers = teamFilter.filter(players, "India");
		        printPlayers("Players from India", indianPlayers);

		        List<Player> australianPlayers = teamFilter.filter(players, "Australia");
		        printPlayers("Players from Australia", australianPlayers);

		        // Update stats for some players
		        System.out.println("\n--- Updating Player Statistics ---");
		        dataHandler.updatePlayerStats(players, "Virat Kohli", 82, 0);
		        dataHandler.updatePlayerStats(players, "Jasprit Bumrah", 2, 3);
		        dataHandler.updatePlayerStats(players, "Steve Smith", 144, 0);
		        dataHandler.updatePlayerStats(players, "Pat Cummins", 12, 4);

		        // Sort and display by runs
		        players.sort(new RunsComparator());
		        printPlayers("Players Sorted by Runs", players);

		        // Calculate team averages
		        System.out.println("\n--- Team Averages ---");
		        double indiaAvg = dataHandler.calculateTeamAverageRuns(players, "India");
		        System.out.println("Average Runs for Team India: " + indiaAvg);

		        double ausAvg = dataHandler.calculateTeamAverageRuns(players, "Australia");
		        System.out.println("Average Runs for Team Australia: " + ausAvg);

		        double engAvg = dataHandler.calculateTeamAverageRuns(players, "England");
		        System.out.println("Average Runs for Team England: " + engAvg);

		        // Filter and print all-rounders
		        int[] criteria = {2000, 100}; // minimum runs and wickets
		        List<Player> goodAllRounders = new AllRounderStatsFilter().filter(players, criteria);
		        printPlayers("All-rounders with good stats (>2000 runs and >100 wickets)", goodAllRounders);

		        try {
		            // Save updated data to file
		            dataHandler.writePlayersToFile("outputCricketData.csv", players);
		        } catch (IOException e) {
		            System.out.println("Error: Unable to write to file.");
		        }
		    }
		}
	}

}
