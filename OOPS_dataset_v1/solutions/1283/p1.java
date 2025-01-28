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
    public int compare(Player p1, Player p2) {
        // Compare runs in descending order
        return Integer.compare(p2.getRunsScored(), p1.getRunsScored());
    }
}

class CricketDataHandler {

    public List<Player> readPlayersFromFile(String fileName) throws IOException {
        List<Player> players = new ArrayList<>();
        try (BufferedReader reader = new BufferedReader(new FileReader(fileName))) {
            // Step 1: Ignore the first line (header)
            reader.readLine();

            String line;
            // Step 4: Read each line
            while ((line = reader.readLine()) != null) {
                String[] data = line.split(",");
                String playerName = data[0];
                Role role = Role.fromString(data[1]);
                int runsScored = Integer.parseInt(data[2]);
                int wicketsTaken = Integer.parseInt(data[3]);
                String teamName = data[4];

                // Step 6: Create player and add to list
                players.add(new Player(playerName, role, runsScored, wicketsTaken, teamName));
            }
        }
        return players;
    }

    public void writePlayersToFile(String fileName, List<Player> players) throws IOException {
        try (BufferedWriter writer = new BufferedWriter(new FileWriter(fileName))) {
            // Step 2: Write header
            writer.write("playerName,role,runsScored,wicketsTaken,teamName");
            writer.newLine();

            // Step 3 & 4: Write each player's details to the file
            for (Player player : players) {
                writer.write(player.toCsvFormat());
                writer.newLine();
            }
        }
    }

    public void updatePlayerStats(List<Player> players, String playerName, int runs, int wickets) {
        for (Player player : players) {
            if (player.getPlayerName().equals(playerName)) {
                player.setRunsScored(player.getRunsScored() + runs);
                player.setWicketsTaken(player.getWicketsTaken() + wickets);
                return; // Exit once the player is updated
            }
        }
        // If player is not found, throw exception
        throw new IllegalArgumentException("Player with name " + playerName + " not found.");
    }

    public double calculateTeamAverageRuns(List<Player> players, String teamName) {
        int totalRuns = 0;
        int count = 0;
        for (Player player : players) {
            if (player.getTeamName().equals(teamName)) {
                totalRuns += player.getRunsScored();
                count++;
            }
        }
        if (count == 0) {
            throw new IllegalArgumentException("No players found for team: " + teamName);
        }
        return (double) totalRuns / count;
    }
}

@FunctionalInterface
interface PlayerFilter<T> {
    List<Player> filter(List<Player> players, T value);
}

class TeamFilterStrategy implements PlayerFilter<String> {
    public List<Player> filter(List<Player> players, String teamName) {
        List<Player> filteredPlayers = new ArrayList<>();
        for (Player player : players) {
            if (player.getTeamName().equals(teamName)) {
                filteredPlayers.add(player);
            }
        }
        return filteredPlayers;
    }
}

class AllRounderStatsFilter implements PlayerFilter<int[]> {
    public List<Player> filter(List<Player> players, int[] criteria) {
        List<Player> filteredAllRounders = new ArrayList<>();
        for (Player player : players) {
            if (
