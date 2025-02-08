/**********************************************************
* PROVIDE THE FOLLOWING INFORMATION
* ID Number:2023A7PS0567P
* Name:Arnav Chhabra
* Lab Number:6016
* System Number:10
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
    	if(p1.getRunsScored()> p2.getRunsScored())return -1;
    	if(p1.getRunsScored()< p2.getRunsScored())return 1;
    	if(p1.getRunsScored()== p2.getRunsScored())return 0;
        // Return a negative value if the first player has more runs, 
        // a positive value if the second player has more runs, or zero if they have the same number of runs.
    }
}

class CricketDataHandler {
    
	/************************** Q.2 WRITE CODE FOR THIS METHOD *********************************/
	public List<Player> readPlayersFromFile(String fileName) throws IOException {
        // Question 2: Write code for reading players from a file [Total: 9 marks]
		List<Player> players=new ArrayList<>();
		Scanner inputStream=null;
		try{
			inputStream=new Scanner(new FileInputSream("inputCricketData.csv"));
		}
		catch(FileNotFoundException e){
			System.out.println("File was not found");
			System.out.println("or could not be found");
			System.exit(0);
		}
		int count=0;
		inputStream.nextLine();
		while(inputStream.hasNextLine()){
			l1.add(inputstream.nextline());
			count++;
		}
		inputstream.close();
		for (Player a: l1){
			System.out.println(a);
		}
    }

	/************************** Q.3 WRITE CODE FOR THIS METHOD *********************************/
    public void writePlayersToFile(String fileName, List<Player> players) throws IOException {
        // Question 3: Write code for writing players to a file [Total: 4 marks]
    	PrintWriter outStream=null;
    	try{
    		outStream=new PrintWriter(new FileOutputStream("inputCricketData.csv"));
    	}
    	catch(FileNotFoundException e){
    		System.err.println("Error openning the file");
    		System.exit(0);
    	}
    	outStream.println("PlayerName"+"Role"+"RunsScored"+"WicketsTaken"+"Teamname");
    	for(Player p: players){
    		outStream.println(p.getPlayerName()+p.getRole()+p.getRunsScored()+p.getWicketsTaken()+p.getTeamName());
    	}
    	outStream.close();
    }
    
	/************************** Q.4 WRITE CODE FOR THIS METHOD *********************************/
    public void updatePlayerStats(List<Player> players, String playerName, int runs, int wickets) {
        // Question 4: Write code for updating player stats [Total: 5 marks]
    	for(Player s: players){
    		try{
    			if(s.getPlayerName()== playerName){
    				int val,wt;
    				val=runs+s.getRunsScored();
        			s.setRunsScored(val);
        			wt=wickets+s.getWicketsTaken();
        			s.setWicketsTaken(wt);
    			}
    		}
    		catch(IllegalArgumentException e){
    			System.out.println("Illegal Argument");
    		}
    	}
   
    }

	/************************** Q.5 WRITE CODE FOR THIS METHOD *********************************/
    public double calculateTeamAverageRuns(List<Player> players, String teamName) {
    	int sum=0;
    	int count=0;
    	for(Player p: players){
    		try{
    			if(p.getTeamName()== teamName){
        			sum+=p.getRunsScored();
        			count++
        		}
    		}
    		catch(IllegalArgumentException e){
    			System.out.println("Illegal Argument");
    		}
    		double avg;
    		avg=sum/count;
    		return avg;
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
    	List<Player> p2=new ArrayList<>();
    	for(Player p: players){
    		if(p.getTeamName()== teamName){
    			p2.add(p);
    		}
    	}
    	System.out.println("The list containing matching players are:"+p2);
    }
}

class AllRounderStatsFilter implements PlayerFilter<int[]> {
    
	/************************** Q.7 WRITE CODE FOR THIS METHOD *********************************/
    public List<Player> filter(List<Player> players, int[] criteria) {
        // Question 7: Write code for filtering all-rounders by stats [Total: 5 marks]
        // criteria[0] = minimum runs, criteria[1] = minimum wickets
    	List<Player> l4=new ArrayList<>();
    	for(Player p: players){
    		if(p.getRole()== Role.ALL_ROUNDER){
    			if(p.getRunsScored()>=criteria[0]&& p.getWicketsTaken()>=criteria[1]){
    				l4.add(p);
    			}
    		}
    	}
        return l4;
    }
}

public class CBT_PART_1_QP {
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