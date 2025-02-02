/**********************************************************
* PROVIDE THE FOLLOWING INFORMATION
* ID Number: 2023A7PS0003P
* Name: Shriram Dhumal
* Lab Number:6117
* System Number: 20
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

	

		/************************** Q.1 WRITE CODE FOR THIS METHOD *********************************/
		class RunsComparator implements Comparator<Player> {
		    public int compare(Player p1, Player p2) {
		        return Integer.compare(p2.getRunsScored(), p1.getRunsScored());
		    }
		}

	class CricketDataHandler {
	    
		/************************** Q.2 WRITE CODE FOR THIS METHOD *********************************/
		public List<Player> readPlayersFromFile(String fileName) throws IOException {
		    List<Player> players = new ArrayList<>();
		    try (BufferedReader reader = new BufferedReader(new FileReader(fileName))) {
		        reader.readLine();
		        
		        String line;
		        while ((line = reader.readLine()) != null) {
		            String[] parts = line.split(",");
		            Player player = new Player(
		                parts[0],                    
		                Role.fromString(parts[1]),   
		                Integer.parseInt(parts[2]),  
		                Integer.parseInt(parts[3]),  
		                parts[4]                     
		            );
		            players.add(player);
		        }
		    }
		    return players;
		}

	/************************** Q.3 WRITE CODE FOR THIS METHOD *********************************/
		public void writePlayersToFile(String fileName, List<Player> players) throws IOException {
		    try (PrintWriter writer = new PrintWriter(new FileWriter(fileName))) {
		        writer.println("PlayerName,Role,RunsScored,WicketsTaken,TeamName");
		        for (Player player : players) {
		            writer.println(player.toCsvFormat());
		        }
		    }
		}
    
	/************************** Q.4 WRITE CODE FOR THIS METHOD *********************************/
		public void updatePlayerStats(List<Player> players, String playerName, int runs, int wickets) {
		    for (Player player : players) {
		        if (player.getPlayerName().equals(playerName)) {
		            player.setRunsScored(player.getRunsScored() + runs);
		            player.setWicketsTaken(player.getWicketsTaken() + wickets);
		            return;
		        }
		    }
		    throw new IllegalArgumentException("Player not found: " + playerName);
		}

	/************************** Q.5 WRITE CODE FOR THIS METHOD *********************************/
		public double calculateTeamAverageRuns(List<Player> players, String teamName) {
		    List<Player> teamPlayers = players.stream()
		        .filter(p -> p.getTeamName().equals(teamName))
		        .collect(Collectors.toList());
		        
		    if (teamPlayers.isEmpty()) {
		        throw new IllegalArgumentException("No players found for team: " + teamName);
		    }
		    
		    int totalRuns = teamPlayers.stream()
		        .mapToInt(Player::getRunsScored)
		        .sum();
		        
		    return (double) totalRuns / teamPlayers.size();
		}

@FunctionalInterface
interface PlayerFilter<T> {
    List<Player> filter(List<Player> players, T value);
}

public List<Player> filter(List<Player> players, String teamName) {
    List<Player> filteredPlayers = new ArrayList<>();
    for (Player player : players) {
        if (player.getTeamName().equals(teamName)) {
            filteredPlayers.add(player);
        }
    }
    return filteredPlayers;
}

public List<Player> filter(List<Player> players, int[] criteria) {
    List<Player> filteredPlayers = new ArrayList<>();
    for (Player player : players) {
        if (player.getRole() == Role.ALL_ROUNDER && 
            player.getRunsScored() >= criteria[0] && 
            player.getWicketsTaken() >= criteria[1]) {
            filteredPlayers.add(player);
        }
    }
    return filteredPlayers;
}

public class P2023A7PS0003_P1 {
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
}
    
