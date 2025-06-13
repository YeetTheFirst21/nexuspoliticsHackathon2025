import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

# Load the issues data
issues_df = pd.read_csv('./challenge_2/complete_issues_data.csv')

# Convert issues data to a GeoDataFrame
issues_gdf = gpd.GeoDataFrame(
    issues_df,
    geometry=gpd.points_from_xy(issues_df['longitude'], issues_df['latitude']),
    crs="EPSG:4326"  # Assuming the issues data is in WGS84
)

# Load the districts data
districts = gpd.read_file("./vg5000_ebenen_1231/VG5000_KRS.shp")
print(districts.head().to_string())
# Ensure both GeoDataFrames use the same CRS
districts = districts.to_crs(issues_gdf.crs)
print(districts.columns)

# Perform a spatial join to group issues into districts
issues_with_districts = gpd.sjoin(issues_gdf, districts[['GEN', 'geometry']], how="left", predicate="within")

# Display the result
print(issues_with_districts.head().to_string())
# Rename the 'GEN' column to 'kreise'
issues_with_districts = issues_with_districts.rename(columns={'GEN': 'kreise'})
