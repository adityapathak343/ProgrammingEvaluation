/**********************************************************
* PROVIDE THE FOLLOWING INFORMATION
* ID Number:
* Name:
* Lab Number:
* System Number:
***********************************************************/

import java.io.*;
import java.util.*;
import java.util.Comparator;

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
    	@Override
        public int compare(Player p1, Player p2) {
            return Integer.compare(p2.getRunsScored(), p1.getRunsScored());
        
    }
}

class CricketDataHandler {
    
	/************************** Q.2 WRITE CODE FOR THIS METHOD *********************************/
	public List<Player> readPlayersFromFile(String fileName) throws IOException {
        // Question 2: Write code for reading players from a file [Total: 9 marks]
		
		List<Player> player_from_file = new ArrayList<>(); // Step1 
		Scanner inputStream = null;
		inputStream = new Scanner(new FileInputStream(fileName)); //Step2
		
		
		
		inputStream.nextLine();   // Step3
		
		String line = null;
		while(inputStream.hasNextLine()) {       //Step4
			
			line = inputStream.nextLine();
			List<String> result = new Scanner(line).tokens().useDelimiter("").collect(Collectors.toList()); //Step5
			
			Player p = new Player(inputStream.next(),inputStream.next(),inputStream.nextInt(),inputStream.nextInt(),inputStream.next()) ;    // Step6
			player_from_file.add(p);      // Step 7 
			
		}
		 inputStream.close();         // Step 8
		
		return player_from_file;     // Step9
		
        
	}

	/************************** Q.3 WRITE CODE FOR THIS METHOD *********************************/
    public void writePlayersToFile(String fileName, List<Player> players) throws IOException {
    	
    	BufferedWriter player_file = new BufferedWriter(new FileWriter(fileName)) 
    	player_file.write("PlayerName,Role,RunsScored,WicketsTaken,TeamName");
    	player_file.newLine();
            for (Player player : players) {
            	player_file.write(player.toCsvFormat());
            	player_file.newLine();
            }
        }
        
    }
    
	/************************** Q.4 WRITE CODE FOR THIS METHOD *********************************/
	public void updatePlayerStats(List<Player> players, String playerName, int runs, int wickets) {
	    boolean playerFound = false;
	    for (Player player : players) {
	        if (player.getPlayerName().equalsIgnoreCase(playerName)) {
	            player.setRunsScored(player.getRunsScored() + runs);
	            player.setWicketsTaken(player.getWicketsTaken() + wickets);
	            playerFound = true;
	            break;
	        }
	    }
	    if (!playerFound) {
	        throw new IllegalArgumentException("Player not found: " + playerName);
	    }
	}


	/************************** Q.5 WRITE CODE FOR THIS METHOD *********************************/
	public double calculateTeamAverageRuns(List<Player> players, String teamName) {
        List<Player> teamPlayers = new ArrayList<>();
        int totalRuns = 0;

        for (Player player : players) {
            if (player.getTeamName().equalsIgnoreCase(teamName)) {
                teamPlayers.add(player);
                totalRuns += player.getRunsScored();
            }
        }

        if (teamPlayers.isEmpty()) {
            throw new IllegalArgumentException("No players found for team: " + teamName);
        }

        return (double) totalRuns / teamPlayers.size();
    }


@FunctionalInterface
interface PlayerFilter<T> {
    List<Player> filter(List<Player> players, T value);
}

class TeamFilterStrategy implements PlayerFilter<String> {
    
	/************************** Q.6 WRITE CODE FOR THIS METHOD *********************************/
    public List<Player> filter(List<Player> players, String teamName) {
    	for (Player player : players) {
            if (player.getTeamName().equalsIgnoreCase(teamName)) {
                filteredPlayers.add(player);
            }
        }
        return filteredPlayers;
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

public class 2022B4A70804P_P1 {
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