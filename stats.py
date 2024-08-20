import pandas as pd
import matplotlib.pyplot as plt

def create_data_frame(events):
    """Create a DataFrame from the list of events"""
    df = pd.DataFrame(events)

    # Explode the player column so that each dictionary in the list becomes a row
    df_exploded = df.explode('players').reset_index(drop=True)

    # Flatten the dictionary into separate columns
    df_flattened = pd.json_normalize(df_exploded['players'])

    # Rename the columns
    df_flattened.rename(columns={'name': 'player name', 'state': 'state'}, inplace=True)

    # Combine the flattened DataFrame with the original one (excluding the 'player' column)
    df_combined = pd.concat([df_exploded.drop(columns=['players']), df_flattened], axis=1)


    return df_combined

def player_attendance_stats(df):
    """Calculate player attendance statistics"""
    # Group by player name and state, then count the occurrences
    player_stats = df.groupby(['player name', 'state']).size().unstack(fill_value=0)

    # Calculate the total number of events attended by each player
    player_stats['total'] = player_stats.sum(axis=1)

    # Calculate the percentage of events attended by each player
    player_stats['percentage'] = player_stats['Confirmed'] / player_stats['total']

    # Sort the DataFrame by percentage in descending order
    player_stats_sorted = player_stats.sort_values('percentage', ascending=False)

    # Return the sorted DataFrame
    return player_stats_sorted



def plot_attendance_line(df):
    # Filter the DataFrame to include only players with "Confirmed" state
    confirmed_players = df[df['state'] == 'Confirmed']

    # Group by training date and calculate the total attendance
    attendance_over_time = confirmed_players.groupby('date')['total'].sum()

    # Plot the attendance over time
    plt.plot(attendance_over_time.index, attendance_over_time.values)
    plt.xlabel('Training Date')
    plt.ylabel('Total Attendance')
    plt.title('Overall Attendance for Each Training Over Time')
    plt.show()