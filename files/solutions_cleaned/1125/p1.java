/**********************************************************
* PROVIDE THE FOLLOWING INFORMATION
* ID Number: 2022A7PS0109P
* Name: K Yaswanth Reddy
* Lab Number: 6114
* System Number: 49
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
    	class RunsComparator implements Comparator<Player> {
    	    public int compare(Player p1, Player p2) {
    	        return Integer.compare(p2.getRunsScored(), p1.getRunsScored()); // Descending order
    	    }
    	}

}

class CricketDataHandler {
    
	/************************** Q.2 WRITE CODE FOR THIS METHOD *********************************/
	public List<Player> readPlayersFromFile(String fileName) throws IOException {
		public List<Player> readPlayersFromFile(String fileName) throws IOException {
		    List<Player> players = new ArrayList<>();
		    try (BufferedReader br = new BufferedReader(new FileReader(fileName))) {
		        String line;
		        br.readLine(); // Skip the header line
		        while ((line = br.readLine()) != null) {
		            String[] data = line.split(",");
		            String playerName = data[0];
		            Role role = Role.fromString(data[1]);
		            int runsScored = Integer.parseInt(data[2]);
		            int wicketsTaken = Integer.parseInt(data[3]);
		            String teamName = data[4];
		            players.add(new Player(playerName, role, runsScored, wicketsTaken, teamName));
		        }
		    }
		    return players;
		}

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
    	public void updatePlayerStats(List<Player> players, String playerName, int runs, int wickets) {
    	    boolean playerFound = false;
    	    for (Player player : players) {
    	        if (player.getPlayerName().equals(playerName)) {
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

    }

	/************************** Q.5 WRITE CODE FOR THIS METHOD *********************************/
    public double calculateTeamAverageRuns(List<Player> players, String teamName) {
    	public double calculateTeamAverageRuns(List<Player> players, String teamName) {
    	    int totalRuns = 0;
    	    int playerCount = 0;
    	    for (Player player : players) {
    	        if (player.getTeamName().equals(teamName)) {
    	            totalRuns += player.getRunsScored();
    	            playerCount++;
    	        }
    	    }
    	    if (playerCount == 0) {
    	        throw new IllegalArgumentException("No players found for team: " + teamName);
    	    }
    	    return (double) totalRuns / playerCount;
    	}

}

@FunctionalInterface
interface PlayerFilter<T> {
    List<Player> filter(List<Player> players, T value);
}

class TeamFilterStrategy implements PlayerFilter<String> {
    
	@overread
    public List<Player> filter(List<Player> players, String teamName) {
       list<player>filteredplayers = new player list<>()
    		   for(player play= play(){
    			   if(player.get.common().equal ignorecase(filteredplayer.addafter) teamname))}
    		   {
    		   retrun filteredplayer
    }
}

class AllRounderStatsFilter implements PlayerFilter<int[]> {
    
	/************************** Q.7 WRITE CODE FOR THIS METHOD *********************************/
    public List<Player> filter(List<Player> players, int[] criteria) {
    	public List<Player> filter(List<Player> players, int[] criteria) {
    	    List<Player> filteredPlayers = new ArrayList<>();
    	    int minRuns = criteria[0];
    	    int minWickets = criteria[1];
    	    for (Player player : players) {
    	        if (player.getRole() == Role.ALL_ROUNDER &&
    	            player.getRunsScored() >= minRuns &&
    	            player.getWicketsTaken() >= minWickets) {
    	            filteredPlayers.add(player);
    	        }
    	    }
    	    return filteredPlayers;
    	}

}

public class P2022A7PS0109_P1 {
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
endmodule