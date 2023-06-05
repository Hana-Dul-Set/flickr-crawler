import flickr_api
import file_utils

import time
import csv
from tqdm import tqdm 

#Get API key from txt file's first line and use it
def set_api_key(api_key_file_path):
    with open(api_key_file_path, 'r', encoding='utf-8') as file:
        api_key = file.readline().strip()
        flickr_api.set_api_key(api_key)

#Download photos in search_response and return downloaded/skipped/total count
def download_search_results(search_response, size_preference, already_downloaded_datas, output_img_dir, output_csv_path, csv_keys, visualize = True):
    search_results = search_response["photos"]

    #Download the photos
    downloaded_count = 0
    skipped_count = 0
    error_count = 0

    if visualize:
        collection = tqdm(search_results)
    else:
        collection = search_results

    for searched_record in collection:
        try:
            #API reqeust for getSizes
            photo_id = searched_record["id"]
            photo_owner = searched_record["owner"]
            photo_filename = photo_id + "-" + photo_owner + ".jpg"

            #Skip if already downloaded
            exists = False
            for record in already_downloaded_datas:
                if record["id"] == photo_id and record["owner"] == photo_owner:
                    exists = True
                    break
            if exists:
                skipped_count += 1
                continue
            
            photo_data = flickr_api.get_photoURLs(photo_id)

            #Set desired size
            download_size = "Original"
            for size in size_preference:
                if size in photo_data["sizes"].keys():
                    download_size = size
                    break
            if download_size == "Original" and not searched_record["candownload"]:
                download_size = photo_data["sizes"].keys()[-1]
            image_url = photo_data["sizes"][download_size]["source"]
        except:
            #Wait and skip if something went wrong
            '''try:
                print(f"\nFatal error on photo {searched_record['id']}, therefore ignoring this one")
            except:
                print("\nFatal error, therefore ignoring this one")'''
            error_count += 1
            continue

        #Download image
        file_utils.download_and_save_image(image_url, output_img_dir + photo_filename)
        downloaded_count += 1

        #Write to csv file
        with open(output_csv_path, mode='a', encoding = 'utf-8', newline='') as file:
            writer = csv.DictWriter(file, fieldnames = csv_keys)
            line = {key: searched_record[key] for key in csv_keys}
            writer.writerow(line)
    return {"downloaded" : downloaded_count, "skipped" : skipped_count, "error" : error_count}
    