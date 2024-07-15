import csv
import random
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

def load_csv(filename, encoding='utf-8'):
    data = {}
    try:
        with open(filename, mode='r', encoding=encoding, errors='replace') as file:
            reader = csv.DictReader(file)
            for row in reader:
                constituency = row['constituency']
                candidate = row['candidate']
                party = row['party']
                votes = int(row['votes'].replace(',', ''))  # Remove commas from votes and convert to int
                
                if constituency not in data:
                    data[constituency] = []
                
                data[constituency].append({'candidate': candidate, 'party': party, 'votes': votes})
    except UnicodeDecodeError:
        print(f"Error decoding file with encoding {encoding}. Trying a different encoding...")
        raise

    return data

def pick_winner(data):
    results = {}
    second_place = {}
    random_numbers = {}
    
    for constituency, candidates in data.items():
        sorted_candidates = sorted(candidates, key=lambda x: x['votes'], reverse=True)
        
        winner = sorted_candidates[0]
        second = sorted_candidates[1] if len(sorted_candidates) > 1 else None
        
        total_votes = sum(candidate['votes'] for candidate in candidates)
        random_pick = random.randint(0, total_votes - 1)
        
        random_numbers[constituency] = random_pick
        
        current_sum = 0
        for candidate in candidates:
            current_sum += candidate['votes']
            if random_pick < current_sum:
                results[constituency] = candidate
                break
        
        second_place[constituency] = second
    
    return results, second_place, random_numbers

def find_original_winner(data):
    results = {}
    
    for constituency, candidates in data.items():
        winner = max(candidates, key=lambda x: x['votes'])
        results[constituency] = winner
    
    return results

def calculate_percentage(winner_votes, total_votes):
    if total_votes == 0:
        return 0.0
    return (winner_votes / total_votes) * 100

def count_seats(data, winners):
    party_counts = {}
    
    for constituency, winner in winners.items():
        party = winner['party']
        if party not in party_counts:
            party_counts[party] = 0
        party_counts[party] += 1
    
    sorted_party_counts = dict(sorted(party_counts.items(), key=lambda item: item[1], reverse=True))
    return sorted_party_counts
    
    return party_counts

def save_results(filename, original_winners, random_winners, second_place, random_numbers, data):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        fieldnames = ['Constituency', 
                      'Original Winner Candidate', 'Original Winner Party', 'Original Winner Votes', 'Original Winner Vote Percentage',
                      'Second Place Candidate', 'Second Place Party', 'Second Place Votes', 'Second Place Vote Percentage',
                      'Random Winner Candidate', 'Random Winner Party', 'Random Winner Votes', 'Random Winner Vote Percentage',
                      'Total Votes', 'Random Number Picked']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        writer.writeheader()
        for constituency, original_winner in original_winners.items():
            random_winner = random_winners[constituency]
            second_place_candidate = second_place[constituency]
            total_votes = sum(candidate['votes'] for candidate in data[constituency])
            
            original_percentage = calculate_percentage(original_winner['votes'], total_votes)
            random_percentage = calculate_percentage(random_winner['votes'], total_votes)
            second_place_percentage = calculate_percentage(second_place_candidate['votes'], total_votes) if second_place_candidate else 0.0
            
            writer.writerow({
                'Constituency': constituency,
                'Original Winner Candidate': original_winner['candidate'],
                'Original Winner Party': original_winner['party'],
                'Original Winner Votes': original_winner['votes'],
                'Original Winner Vote Percentage': f"{original_percentage:.2f}%",
                'Second Place Candidate': second_place_candidate['candidate'] if second_place_candidate else "",
                'Second Place Party': second_place_candidate['party'] if second_place_candidate else "",
                'Second Place Votes': second_place_candidate['votes'] if second_place_candidate else "",
                'Second Place Vote Percentage': f"{second_place_percentage:.2f}%" if second_place_candidate else "",
                'Random Winner Candidate': random_winner['candidate'],
                'Random Winner Party': random_winner['party'],
                'Random Winner Votes': random_winner['votes'],
                'Random Winner Vote Percentage': f"{random_percentage:.2f}%",
                'Total Votes': total_votes,
                'Random Number Picked': random_numbers[constituency]
            })

def main():
    input_filename = 'election_data.csv'  # Replace with your CSV file path
    output_filename = 'election_results.csv'  # Output CSV file path
    
    candidates_to_check = ['Keir Starmer', 'Rishi Sunak', 'Ed Davey', 'Stephen Flynn', 'Nigel Farage', 'Jacob Rees-Mogg', 'Liz Truss', 'Lindsay Hoyle']  # Add more names as needed
    
    try:
        data = load_csv(input_filename, encoding='utf-8')
    except UnicodeDecodeError:
        data = load_csv(input_filename, encoding='ISO-8859-1')
    
    original_winners = find_original_winner(data)
    random_winners, second_place, random_numbers = pick_winner(data)
    
    save_results(output_filename, original_winners, random_winners, second_place, random_numbers, data)
    
    original_party_counts = count_seats(data, original_winners)
    random_party_counts = count_seats(data, random_winners)
    
    sorted_original_party_counts = dict(sorted(original_party_counts.items(), key=lambda item: item[1], reverse=True))
    sorted_random_party_counts = dict(sorted(random_party_counts.items(), key=lambda item: item[1], reverse=True))
    
    print("Thank you to Philip Brown and Alasdair Rae, Automatic Knowledge for the mapping data\n")
    
    print("Seats won by each party based on original votes (in descending order):")
    print(sorted_original_party_counts)
    
    print("\nSeats won by each party based on random votes (in descending order):")
    print(sorted_random_party_counts)
    print("\n")
    
    # Check specific candidates
    for candidate_name in candidates_to_check:
        found = False
        for constituency, winner in random_winners.items():
            if winner['candidate'].strip().lower() == candidate_name.strip().lower():
                print(f"{candidate_name} won their random election")
                found = True
                break
        if not found:
            print(f"{candidate_name} lost their random election")

if __name__ == "__main__":
    main()



# Load the CSV file
csv_path = r'election_results.csv'
data = pd.read_csv(csv_path)

# Load the shapefile
shapefile_path = r'uk-constituencies-2024-21-june-24.shp'
gdf = gpd.read_file(shapefile_path)

# Merge the data with the shapefile on "Name" instead of "Constituency"
merged = gdf.merge(data, left_on='Name', right_on='Constituency')

# Define the color mapping for each party
party_colors = {
    'Abolish the Welsh Assembly Party': '#810000',
    'Alba': '#005EB8',
    'Alliance for Democracy and Freedom': '#F8F9FA',
    'Alliance for Green Socialism': '#00A86B',
    'Alliance Party': '#F6CB2F',
    'Animal Welfare Party': '#EE3263',
    'Aontú': '#44532A',
    'Ashfield Independents': 'pink',
    'Blue Revolution': '#0000FF',
    'British Democratic Party': '#284571',
    'British Unionist Party': '#000080',
    'Chesterfield And North Derbyshire Independents': '#F8F9FA',
    'Christian Party': '#9966CC',
    'Christian Peoples Alliance': '#813887',
    'Climate Party': '#36D0B6',
    'Common Good': '#F77FBE',
    'Communist Future': '#F8F9FA',
    'Communist League': '#C71585',
    'Communist Party of Britain': '#F93822',
    'Confelicity': '#15988E',
    'Consensus': '#00BDA1',
    'Conservative': '#0087DC',
    'Count Binface Party': '#F8F9FA',
    'Cross-Community Labour Alternative': '#cd5c5c',
    'Democracy for Chorley': '#000000',
    'Democratic Unionist Party': '#D46A4C',
    'English Constitution Party': '#CE142C',
    'English Democrats': '#915F6D',
    'Fairer Voting Party': '#F8F9FA',
    'Freedom Alliance': '#CC1280',
    'Green': '#02A95B',
    'Hampshire Independents': '#00E5FF',
    'Heritage Party': '#0A00A5',
    'Independence for Scotland Party': '#2980B9',
    'Independent': '#DCDCDC',
    'Independent Alliance (Kent)': '#7B9B5C',
    'Independent Network': '#483D8B',
    'Independent Oxford Alliance': '#702CA1',
    'Independents for Direct Democracy': '#F8F9FA',
    'Kingston Independent Residents Group': '#A21f5E',
    'Labour': '#E4003B',
    'Liberal Democrat': '#FAA61A',
    'Liberal Party': '#EB7A43',
    'Libertarian Party': '#FCC820',
    'Lincolnshire Independents': '#000000',
    'Liverpool Community Independents': '#800000',
    'Monster Raving Loony Party': '#FFF000',
    'National Health Action Party': '#0071BB',
    'New Open Non-Political Organised Leadership': '#F8F9FA',
    'Newham Independents Party': '#EAE33B',
    'North East Party': '#800000',
    'One Leicester': '#862E8B',
    'Party of Women': '#ff0f7b',
    'People Before Profit': '#E91D50',
    'Plaid Cymru': '#005B54',
    'Portsmouth Independent Party': '#D9B3FF',
    'Propel': '#0b8e36',
    'Psychedelic Movement': '#F8F9FA',
    'Putting Crewe and Nantwich First': '#F8F9FA',
    'Rebooting Democracy': '#F8F9FA',
    'Reform UK': '#12B6CF',
    'Rejoin EU': '#003399',
    'Save Us Now': '#F8F9FA',
    'Scottish Family Party': '#19369A',
    'Scottish Libertarian Party': '#F0DC83',
    'Scottish National Party': '#FDF38E',
    'Scottish Socialist Party': '#ff0000',
    'Shared Ground': '#FAFB09',
    'Sinn Fein': '#326760',
    'Social Democratic & Labour Party': '#2AA82C',
    'Social Democratic Party': '#D25469',
    'Social Justice Party': '#437048',
    'Socialist Equality': '#960018',
    'Socialist Labour Party': '#EE1C25',
    'Socialist Party of Great Britain': '#DC241f',
    'South Devon Alliance': '#1F8442',
    'Sovereignty': '#F8F9FA',
    'Speaker of the House of Commons': 'black',
    'Stockport Fights Austerity No to Cuts': '#F8F9FA',
    'Swale Independents': '#FF5800',
    'Taking The Initiative Party': '#7D6AAA',
    'The Common People': '#F8F9FA',
    'The Mitre TW9': '#F8F9FA',
    'The Peace Party': '#F58231',
    'The Yorkshire Party': '#00AEEF',
    'Trade Unionist and Socialist Coalition': '#EC008C',
    'Traditional Unionist Voice': '#0C3A6A',
    'Transform Party': '#EC548A',
    'True & Fair Party': '#FFFFFF',
    'UK Independence Party': '#6D3177',
    'UK Voice': '#F8F9FA',
    'Ulster Unionist Party': '#48A5EE',
    'Volt United Kingdom': '#502379',
    'Women\'s Equality Party': '#432360',
    'Workers Party of Britain': '#780021',
    'Workers Revolutionary Party': '#AA0000',
    'Yoruba Party in the UK': '#00AEEF',

}

# Assign colors to each constituency based on the "Random Winner Party"
merged['color'] = merged['Random Winner Party'].map(party_colors)

# Handle missing values (NaN) in 'color' column
merged['color'].fillna('#808080', inplace=True)  # Assigning gray color as default for missing parties

# Plot the map with assigned colors
fig, ax = plt.subplots(1, 1, figsize=(15, 10))
merged.plot(ax=ax, color=merged['color'], legend=True)

# Add a legend manually
handles = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=color, markersize=10, label=party) 
           for party, color in party_colors.items() if party in merged['Random Winner Party'].unique()]

ax.legend(handles=handles, title="Random Winner Party", bbox_to_anchor=(1.05, 1), loc='upper left')

# Add title and show the plot
plt.title("Map of Random Winner Party by Constituency")
plt.show()
