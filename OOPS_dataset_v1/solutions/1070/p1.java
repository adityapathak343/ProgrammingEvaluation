/**********************************************************
* PROVIDE THE FOLLOWING INFORMATION
* ID Number:
* Name:
* Lab Number:
* System Number:
***********************************************************/

import java.io.*;
import java.util.*;

import javax.management.relation.Role;

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
        // Question 1: Write code for comparing/sorting runs in descending order [Total: 2 marks]
        // Return a negative value if the first player has more runs, 
        // a positive value if the second player has more runs, or zero if they have the same number of runs.
    	int runs1 = p1.getRunsScored();
    	int runs2 = p2.getRunsScored();
    	int val;
    	if (runs1>runs2) {
    		val = -1;
    	} else if (runs1<runs2) {
			val = 1;
		} else {
			val = 0;
		}
    	return val;
    }
}

class CricketDataHandler {
    
	/************************** Q.2 WRITE CODE FOR THIS METHOD *********************************/
	public List<Player> readPlayersFromFile(String fileName) throws IOException {
        // Question 2: Write code for reading players from a file [Total: 9 marks]
        // Step 1: Create an empty list to store player details. [1 mark]
        // Step 2: Open the specified file for reading data. [1 mark]
        // Step 3: Ignore the first line since it contains the column names. [1 mark]
        // Step 4: Read each line one by one until reaching the end of the file. [1 mark]
        // Step 5: Split the line into different pieces of information. [1 mark]
        // Step 6: Create a new player using this information. [1 mark]
        // Step 7: Add the new player to the list. [1 mark]
        // Step 8: Close the file after reading all data. [1 mark]
        // Step 9: Return the complete list of players. [1 mark]
		ArrayList<Player> players = new ArrayList<>();
		int i;
		FileInputStream fInputStream;
		try {
			fInputStream = new FileInputStream(fileName);
		} catch (FileNotFoundException e) {
			System.out.println("Cannot open file");
			return players;
		}
		try {
			do {
				i = fInputStream.read();
			} while ((char) i != '\n');
		} catch (IOException e) {
			System.out.println("Error reading file");
		}
		ArrayList<String> playerdetails1 = new ArrayList<>();
		try {
			do {
				i = fInputStream.read();
				char[] k = {(char) i};
				String letter = new String(k);
				playerdetails1.add(letter);
			} while (i != -1);
		} catch (IOException e) {
			System.out.println("Error reading file");
		}
		String s1 = new String();
		s1 = "";
		ArrayList<String> playerdetails2 = new ArrayList<>();
		for (int j=0; j<playerdetails1.size(); j++) {
			String s2 = new String();
			s2 = playerdetails1.get(j);
			if (s2.equals("\n")) {
				playerdetails2.add(s1);
				s1 = "";
			} else {
				s1+=s2;
			}
		}
		ArrayList<ArrayList<String>> playerdetails3 = new ArrayList<>();
		for (int j=0; j<playerdetails2.size(); j++) {
			String s2 = new String();
			s2 = playerdetails1.get(j);
			String s3 = new String();
			s3 = "";
			ArrayList<String> playerdetails4 = new ArrayList<>();
			for (int k=0; k<s2.length(); k++) {
				char val = s2.charAt(k);
				if (val!='\t') {
					char[] d = {val};
					String letter = new String(d);
					s3+=letter;
				} else {
					playerdetails4.add(s3);
					s3="";
				}
				
			}
			playerdetails3.add(playerdetails4);
		}
		
		for (int j=0; j<playerdetails3.size(); j++) {
			ArrayList<String> playerdetails4 = new ArrayList<>();
			playerdetails4 = playerdetails3.get(j);
			String pname = new String();
			pname = playerdetails4.get(0);
			Role role = Role.fromString(playerdetails4.get(1));
			int rscored = Integer.parseInt(playerdetails4.get(2));
			int wtaken = Integer.parseInt(playerdetails4.get(3));
			String tname = new String();
			tname = playerdetails4.get(4);
			Player p1 = new Player(pname, role, rscored, wtaken, tname);
			players.add(p1);
		}
		
		try {
			fInputStream.close();
		} catch (IOException e) {
			System.out.println("Error closing file");
		}
		
		return players;
    }

	/************************** Q.3 WRITE CODE FOR THIS METHOD *********************************/
    public void writePlayersToFile(String fileName, List<Player> players) throws IOException {
        // Question 3: Write code for writing players to a file [Total: 4 marks]
        // Step 1: Prepare to write data into the specified file. [1 mark]
        // Step 2: Write the column names as the first line of the file. [1 mark]
        // Step 3: For each player in the list, convert their details to the desired format. [1 mark]
        // Step 4: Write each player's information to the file. [1 mark]
    }
    
	/************************** Q.4 WRITE CODE FOR THIS METHOD *********************************/
    public void updatePlayerStats(List<Player> players, String playerName, int runs, int wickets) {
        // Question 4: Write code for updating player stats [Total: 5 marks]
        // Step 1: Go through each player in the list. [1 mark]
        // Step 2: Check if the current player's name matches the given name. [1 mark]
        // Step 3: If it matches, update the player's runs with the new value. Updated value will be the sum of the old runs and the argument runs. [1 mark]
        // Step 4: Similarly, update the player's wickets with the new value. Updated value will be the sum of the old wickets and the argument wickets. [1 mark]
        // Step 5: If no player matches the given name, throw an IllegalArgumentException exception. [1 mark]
    	try {
    		int j = 0;
    		for (int i=0; i<players.size(); i++) {
        		Player p1 = players.get(i);
        		if (playerName.equals(p1.getPlayerName())) {
        			int run = p1.getRunsScored();
        			p1.setRunsScored(runs+run);
        			int wicket = p1.getWicketsTaken();
        			p1.setWicketsTaken(wickets+wicket);
        			j = 1;
        			break;
        		}
        		
        	}
    		if (j==0) {
    			Exception IllegalArgumentException;
				throw IllegalArgumentException;
    		}
    	}  catch (IllegalArgumentException e) {
    		System.out.println("No such player exists");
    	}
    }

	/************************** Q.5 WRITE CODE FOR THIS METHOD *********************************/
    public double calculateTeamAverageRuns(List<Player> players, String teamName) {
        // Question 5: Write code for calculating team average runs [Total: 5 marks]
        // Step 1: Filter players belonging to the specified team. [2 marks]
        // Step 2: If no players from the specified team are found, throw an IllegalArgumentException exception. [1 mark]
        // Step 3: Calculate the total runs scored by all players from this team. [1 mark]
        // Step 4: Compute and return the average runs scored. [1 mark]
    	ArrayList<Player> playersIndia = new ArrayList<>();
    	ArrayList<Player> playersAustralia = new ArrayList<>();
    	ArrayList<Player> playersEngland = new ArrayList<>();
    	for (int i=0; i<players.size(); i++) {
    		Player p1 = players.get(i);
    		if (p1.getTeamName().equals("India")) {
    			playersIndia.add(p1);
    		} else if (p1.getTeamName().equals("Australia")) {
    			playersAustralia.add(p1);
    		} else {
    			playersEngland.add(p1);
    		}
    	}
    	if (playersIndia.size()==0 || playersAustralia.size()==0 || playersEngland.size()==0) {
    		Exception IllegalArgumentException;
			throw IllegalArgumentException;
    	}
    	
    	if (teamName.equals("India")){
    		int truns= 0;
    		double avg;
    		for (int i=0; i<playersIndia.size();i++) {
    			Player p1 = playersIndia.get(i);
    			int run = p1.getRunsScored();
    			truns+=run;
    		}
    		return avg/playersIndia.size();
    	} else if (teamName.equals("Australia")) {
    		int truns= 0;
    		double avg;
    		for (int i=0; i<playersAustralia.size();i++) {
    			Player p1 = playersAustralia.get(i);
    			int run = p1.getRunsScored();
    			truns+=run;
    		}
    		return avg/playersAustralia.size();
		} else {
			int truns= 0;
    		double avg;
    		for (int i=0; i<playersEngland.size();i++) {
    			Player p1 = playersEngland.get(i);
    			int run = p1.getRunsScored();
    			truns+=run;
    		}
    		return avg/playersEngland.size();
		}
    }
}

@FunctionalInterface
interface PlayerFilter<T> {
    List<Player> filter(List<Player> players, T value);
}

class TeamFilterStrategy implements PlayerFilter<String> {
    
	/************************** Q.6 WRITE CODE FOR THIS METHOD *********************************/
    public List<Player> filter(List<Player> players, String teamName) {
        // Question 6: Write code for filtering players by team [Total: 5 marks]
        // Step 1: Create an empty list for players matching the criteria. [1 mark]
        // Step 2: Go through each player in the players list. [1 mark]
        // Step 3: If the player's team matches the given name, add them to the list. [2 marks]
        // Step 4: Return the list containing all matching players. [1 mark]
    }
}

class AllRounderStatsFilter implements PlayerFilter<int[]> {
    
	/************************** Q.7 WRITE CODE FOR THIS METHOD *********************************/
    public List<Player> filter(List<Player> players, int[] criteria) {
        // Question 7: Write code for filtering all-rounders by stats [Total: 5 marks]
        // criteria[0] = minimum runs, criteria[1] = minimum wickets
        // Step 1: Create an empty list for players matching the criteria. [1 mark]
        // Step 2: Go through each player in the list. [1 mark]
        // Step 3: If the player is an all-rounder and meets the given criteria for both runs and wickets, add them to the list. [2 marks]
        // Step 4: Return the list containing all matching players. [1 mark]
    }
}

public class P2022B3A70551P_P1 {
    private static void printPlayers(String header, List<Player> players) {
        System.out.println("\n--- " + header + " ---");
        for (Player player : players) {
            System.out.println(player);
        }
    }

    public static void main(String[] args) {
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