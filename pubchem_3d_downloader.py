import pandas as pd
import pubchempy as pcp
import requests
import argparse
import os


def search_pubchem(compound: str) -> int:
    """Search PubChem for a given compound and return its CID."""
    try:
        result = pcp.get_compounds(compound, 'name', record_type='3d')[0]
        return result.cid
    except (IndexError, pcp.PubChemHTTPError) as e:
        print(f"Error searching PubChem for {compound}: {e}")
        return None


def download_sdf3d(cid: int) -> str:
    """Download the 3D structure of a compound in SDF format from PubChem and return the SDF text."""
    try:
        url = f'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/SDF?record_type=3d'
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except (requests.exceptions.RequestException, pcp.PubChemHTTPError) as e:
        print(f"Error downloading SDF for CID {cid}: {e}")
        return None

def download_sdf2d(cid: int) -> str:
    """Download the 3D structure of a compound in SDF format from PubChem and return the SDF text."""
    try:
        url = f'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/SDF'
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except (requests.exceptions.RequestException, pcp.PubChemHTTPError) as e:
        print(f"Error downloading SDF for CID {cid}: {e}")
        return None

def log_error(cid: int, message: str) -> None:
    with open('./error.log', 'a') as f:
        f.write(f"{cid}: {message}\n")

    with open('./failed_cids.txt', 'a') as f:
        f.write(f"{cid}\n")

def main(csv_file: str) -> None:
    """Main function that reads a CSV file of compound names, 
    searches PubChem for each compound, and downloads the 3D
    structure of each compound in SDF format."""
    # Load table data into Pandas DataFrame
    try:
        df = pd.read_csv(csv_file)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return

    # Loop through DataFrame and search PubChem for each compound
    # cids = []
    # for index, row in df.iterrows():
    #     compound_name = row['compound_name']
    #     cid = search_pubchem(compound_name)
    #     cids.append(cid)
    # df['cid'] = cids

    # Loop through DataFrame and download the 3D structure of each compound
    csv_dir = os.path.dirname(os.path.abspath(args.csv_file))

    os.makedirs(str(csv_dir) + "/downloaded_sdf/3D", exist_ok=True)
    os.makedirs(str(csv_dir) + "/downloaded_sdf/2D", exist_ok=True)
    dir2D = str(csv_dir) + "/downloaded_sdf/2D"
    dir3D = str(csv_dir) + "/downloaded_sdf/3D"

    for index, row in df.iterrows():
        cid = row['cid']

        try:
            sdf3d = download_sdf3d(cid)
        except Exception as e:
            sdf3d = None

        if sdf3d is None:
            try:
                sdf2d = download_sdf2d(cid)
            except Exception as e:
                sdf2d = None

            if sdf2d is None:
                log_error(cid, "Failed to download 3D and 2D SDF")
                continue

            try:
                with open(f'{dir2D}/{cid}.sdf', 'w') as f:
                    f.write(sdf2d)
                print(f"Downloaded 2D SDF for {cid}")
            except IOError as e:
                print(f"Error saving SDF for {cid}: {e}")
                log_error(cid, "Failed to save SDF")
            continue

        try:
            with open(f'{dir3D}/{cid}.sdf', 'w') as f:
                f.write(sdf3d)
            print(f"Downloaded 3D SDF for {cid}")
        except IOError as e:
            print(f"Error saving SDF for {cid}: {e}")
            log_error(cid, "Failed to save SDF")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download 3D compound structures from PubChem using a CSV file of compound names.')
    parser.add_argument('csv_file', type=str, help='Path to the CSV file containing compound names in a column named "compound_name".')
    args = parser.parse_args()
    main(args.csv_file)
