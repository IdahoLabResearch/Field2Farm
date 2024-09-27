import os,sys
import geopandas as gpd
import pandas as pd
import numpy as np
from pert import PERT

np.random.seed(42)

def create_farms(all_fields, farm, neighbors, cat_counts, cat_lists, idx):
    """
    Create farms based on the given parameters.

    Args:
        all_fields (DataFrame): DataFrame containing all fields.
        farm (DataFrame): DataFrame representing the current farm.
        neighbors (DataFrame): DataFrame representing neighboring fields.
        cat_counts (dict): Dictionary containing counts for each cat.
        cat_lists (dict): Dictionary containing lists for each cat.
        idx (int): Index counter.

    Returns:
        GeoDataFrame: GeoDataFrame containing classified neighbouring fields.
    """
    neighbors.sort_values(by='CALCACRES', axis=0, inplace=True)

    for _, row in neighbors.iterrows():
        farm = pd.concat([farm, all_fields[all_fields.old_index == row.old_index]])
        area = sum(farm.CALCACRES)
        low, high, cat = get_range()
        if area > low:
                    std = (high-low)/6
                    mid = cat_sizes[cat]
                    if cat_sizes[cat]==0:
                        mid = (high+low)/2
                    std_low = max(mid-std, low)
                    std_high = min(mid+std, high)
                    while std_high<std_low:
                        std_high+=std_low
                    r = np.random.uniform(0,1)
                    if std_low<area<std_high:
                        all_fields.drop(farm.index.values, inplace=True)
                        farm.cat = cat
                        farm.farm_id = idx
                        cat_lists[cat].append(farm)
                        cat_counts[cat] -= 1                    
                        sys.stdout.write("\033[K")  # Clears the line
                        sys.stdout.write('\rfarms remaining: '+str(cat_counts))
                        return (farm)
                    elif low<area<high and r<0.34:
                        all_fields.drop(farm.index.values, inplace=True)
                        farm.cat = cat
                        farm.farm_id = idx
                        cat_lists[cat].append(farm)
                        cat_counts[cat] -= 1                    
                        sys.stdout.write("\033[K")  # Clears the line
                        sys.stdout.write('\rfarms remaining: '+str(cat_counts))
                        return (farm)
    return (farm)

def get_range():
    """
    Determines the range based on the category counts.

    Returns:
        tuple: A tuple containing the low and high range values along with the category.
    """
    if cat_counts[6] > 0:
        cat = 6
        low = 1000
        high = 10000
    elif cat_counts[5] > 0:
        cat = 5
        low = 500
        high = 1000
    elif cat_counts[4] > 0:
        cat = 4
        low = 180
        high = 500
    elif cat_counts[3] > 0:
        cat = 3
        low = 50
        high = 180
    elif cat_counts[2] > 0:
        cat = 2
        low = 10
        high = 50
    elif cat_counts[1] > 0:
        cat = 1
        low = 0
        high = 10
    return low, high, cat


def checkFarmNeeds(field):
    """
    Check if additional farms are needed.

    Args:
        field (GeoDataFrame): GeoDataFrame representing the field.

    Returns:
        bool: True if additional farms are not needed, False otherwise.
    """
    area = sum(field.CALCACRES.values)
    if (area > 1000 and cat_counts[6] == 0) or \
        (area > 10 and  cat_counts[2] == 0 and  cat_counts[3] == 0 and cat_counts[4] == 0 and cat_counts[5] == 0 and cat_counts[6] == 0) or \
        (area > 50 and  cat_counts[3] == 0 and cat_counts[4] == 0 and cat_counts[5] == 0 and cat_counts[6] == 0) or \
        (area > 180 and cat_counts[4] == 0 and cat_counts[5] == 0 and cat_counts[6] == 0) or \
        (area > 500 and cat_counts[5] == 0 and cat_counts[6] == 0):
        return False
    elif len(field.index)==0:
        return False
    else:
         return True

def processCounty(n_cat1,n_cat2,n_cat3,n_cat4,n_cat5,n_cat6,county):
        """
        Process the county fields to create farms.

        Args:
            n_cat1 (int): Number of farms with less than 10 acre area.
            n_cat2 (int): Number of farms with 10-50 acre area.
            n_cat3 (int): Number of farms with 50-180 acre area.
            n_cat4 (int): Number of farms with 180-500 acre area.
            n_cat5 (int): Number of farms with 500-1000 acre area.
            n_cat6 (int): Number of farms with more than 1000 acre area.
            county (str): Name of the county.

        Returns:
            GeoDataFrame: GeoDataFrame containing all classified fields.
        """

        neighborhood_size=25 # meters; assuming fields do not need to be attached to be part of farms
        county=county.title()       
        farms_to_create = n_cat1+n_cat2+n_cat3+n_cat4+n_cat5+n_cat6     

        county_fields = f"./inputs/spatial/{county}_intersect.gpkg"    
        all_fields = gpd.read_file(county_fields)        
        all_fields.loc[:,"cat"]=None
        all_fields.loc[:,'farm_id']= None
        all_fields.loc[:,"CALCACRES"]=all_fields.area*0.00025 # converting sqm to acres        
        all_fields=all_fields[(all_fields.CALCACRES>1)] #ignoring very small & large fields
        total_acres = sum(all_fields.CALCACRES)
        size_6 = (total_acres-(s_cat1+s_cat2+s_cat3+s_cat4+s_cat5))/n_cat6
        
        all_fields.sort_values(by='CALCACRES', ascending=False, axis=0, inplace=True)
        all_fields=all_fields.rename_axis('old_index').reset_index()        
        
        cultivable = raster_val_attrib[raster_val_attrib.Cultivable==1]
        cultivated = raster_val_attrib[raster_val_attrib.Cultivated==1]
        cultivable = cultivable.Value.astype(str).tolist()
        cultivated = cultivated.Value.astype(str).tolist()
        all_fields_cultivated=all_fields[all_fields.raster_val.isin (cultivated)]
        all_fields_cultivable = all_fields[all_fields.raster_val.isin(cultivable)] 
        # all_fields = all_fields_cultivable
        original_crs = all_fields.crs
        
        total_fields = len(all_fields.index)
            
        print ("county:",county)   
        print ("total fields:",total_fields)
        print ("farms to create:",farms_to_create)    
        idx=0
        iteration=0
        max_iterations = 4
        while farms_to_create>0 and iteration < max_iterations:
            field = all_fields[all_fields.index==idx]
            neighborhood_size=25
            no_of_tries = 0 

            buffer =field.buffer(neighborhood_size)
            buffer = gpd.GeoDataFrame(geometry = buffer.geometry)  
            neighbors = gpd.sjoin(all_fields_cultivated,buffer) #defining the neighborhood of the farm
            neighbors = neighbors[~neighbors.old_index.isin(field.old_index)] #avoiding duplicate geometries in the neighbors
            farm = field  
            idx+=1
            existing_farms_to_create = farms_to_create
            farm = create_farms(all_fields, farm, neighbors, cat_counts, cat_lists, idx)
            farms_to_create=sum([*cat_counts.values()])
            while existing_farms_to_create == farms_to_create and no_of_tries<=5 and checkFarmNeeds(farm):                       
                no_of_tries += 1                              
                # Gradually increasing neighborhood size with subsequent failed tries ;              
                neighborhood_size =25**no_of_tries
                # Create a buffer with the updated neighborhood size
                convex_hull = farm.unary_union.convex_hull
                convex_hull = gpd.GeoDataFrame(geometry=[convex_hull],crs=original_crs)
                buffer = convex_hull.buffer(neighborhood_size)
                buffer = gpd.GeoDataFrame(geometry=buffer.geometry)
                # buffer = gpd.GeoDataFrame(geometry=[farm.unary_union.buffer(neighborhood_size)], crs=original_crs)

                # Prioriotizing cultivated lands included in the farms
                neighbors = gpd.sjoin(all_fields_cultivable, buffer)
                if no_of_tries > 2:
                    neighbors = gpd.sjoin(all_fields, buffer)                    
                    
                # Remove duplicate fields in the expanded_neighbors
                neighbors = neighbors[~neighbors.old_index.isin(farm.old_index)]
                
                # Create farms based on the updated parameters
                farm = create_farms(all_fields, farm, neighbors, cat_counts, cat_lists, idx)
                farms_to_create=sum([*cat_counts.values()])
                if idx >= 0.999 * total_fields:
                    idx = 0
                    iteration += 1 
                    total_fields = len(all_fields.index)
                    all_fields.reset_index(drop=True, inplace=True)
                    print ("next iteration",iteration)
                    
                
        fields_classified = [*cat_lists.values()]  
        non_empty_dfs = [df for df in fields_classified if len(df)>0]
        fields_classified = pd.concat([pd.concat(df) for df in non_empty_dfs]) 
        fields_classified.index=fields_classified.old_index #reverting index back to original
        fields_classified["CALCACRES"] = fields_classified.area*0.00025
        fields_classified.drop(['old_index','level_0','level_1'],inplace=True, axis=1)
        print("\n\nfinished creating farms..")
        return fields_classified
   

if __name__=="__main__":
    path = 'fields2farms_template'  
    county = 'Iowa133' 
    if len(sys.argv)>1:
        county = sys.argv[1]
    # os.chdir(os.path.expanduser(f'~/{path}'))
    lookup = pd.read_csv('./inputs/tabular/lookup_NASS.csv')
    lookup = lookup[lookup.countycode==county.upper()]

    farm_distribution = pd.read_csv('./inputs/tabular/farmDistribution.csv')
    farm_distribution = farm_distribution[farm_distribution.county==county.upper()]
    raster_val_attrib = pd.read_csv("./inputs/tabular/cultivable_CDL.csv") #the table contains list of cultivable/cultivated NASS raster values
    # farm size categories
    cat1 = [] # farms with less than 10 acre area
    cat2 = [] # farms with 10-50 acre area
    cat3 = [] # farms with 50-180 acre area
    cat4 = [] # farms with 180-500 acre area
    cat5 = [] # farms with 500-1000 acre area
    cat6 = [] # farms with more than 1000 acre area
    county_name = lookup['countycode'].values[0]

    #NASS reported number of farms for given size category
    n_cat1=lookup['<10'].values[0]
    n_cat2=lookup['10-50'].values[0]
    n_cat3=lookup['50-180'].values[0]
    n_cat4=lookup['180-500'].values[0]
    n_cat5=lookup['500-1000'].values[0]
    n_cat6=lookup['>1000'].values[0]

    #NASS reported size distribution of farms for given size category
    s_cat1=farm_distribution['<10'].values[0]
    s_cat2=farm_distribution['10-50'].values[0]
    s_cat3=farm_distribution['50-180'].values[0]
    s_cat4=farm_distribution['180-500'].values[0]
    s_cat5=farm_distribution['500-1000'].values[0]
    s_cat6=farm_distribution['>1000'].values[0]
    
    cat_counts = {1: n_cat1, 2: n_cat2, 3: n_cat3, 4: n_cat4, 5: n_cat5, 6: n_cat6}
    cat_lists = {1: cat1, 2: cat2, 3: cat3, 4: cat4, 5: cat5, 6: cat6}  
    cat_sizes = {1: s_cat1/n_cat1, 2: s_cat2/n_cat2, 3: s_cat3/n_cat3, 4: s_cat4/n_cat4, 5: s_cat5/n_cat5, 6: s_cat6/n_cat6}  
    fields_classified=processCounty(n_cat1, n_cat2, n_cat3, n_cat4, n_cat5, n_cat6, county_name)
    max_value_index = fields_classified.groupby('farm_id')['CALCACRES'].idxmax()
    farms_classified = fields_classified.dissolve(by='farm_id',aggfunc={'CALCACRES':'sum','cat':'max'})
    farms_classified['raster_val'] = farms_classified.index.map(lambda idx: fields_classified.loc[max_value_index.loc[idx], 'raster_val'])
    print ("\rtotal farms classified: ",len(farms_classified.index))
    fields_classified.to_file(f'./outputs/{county.capitalize()}_fields.gpkg', driver="GPKG", overwrite=True)
    farms_classified.to_file(f'./outputs/{county.capitalize()}_farms.gpkg', driver="GPKG", overwrite=True)

