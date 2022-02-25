import urllib.request
import json
import copy
from datetime import date

today = date.today().strftime("%Y-%-m-%-d")
range_ratio = 0.75

def score_meal(nutrient_dict):
	score = 0
	score+=score_nutrient(nutrient_dict["calories"], 2000, 100, 4)
	score+=score_nutrient(nutrient_dict["protein"], 60, 20, 2)
	score+=score_nutrient(nutrient_dict["carbohydrates"], 150, 20, 1)
	score+=score_nutrient(nutrient_dict["sugar"], 10, 2, 2)
	score+=score_nutrient(nutrient_dict["total_fat"], 70, 20, 1)
	score+=score_nutrient(nutrient_dict["saturated_fat"], 0, 8, 1)
	score+=score_nutrient(nutrient_dict["cholesterol"], 0, 50, 1)
	score+=score_nutrient(nutrient_dict["dietary_fiber"], 30, 5, 1)
	score+=score_nutrient(nutrient_dict["sodium"], 1000, 300, 2)
	score+=score_nutrient(nutrient_dict["potassium"], 4700, 700, 1)
	score+=score_nutrient(nutrient_dict["calcium"], 1300, 500, 1)
	score+=score_nutrient(nutrient_dict["iron"], 10, 5, 1)
	score+=score_nutrient(nutrient_dict["vitamin_d"], 500, 200, 0.5)
	score+=score_nutrient(nutrient_dict["vitamin_c"], 90, 200, 0.5)
	score+=score_nutrient(nutrient_dict["vitamin_a"], 900, 300, 1)
	return score

def score_nutrient(total, pref_total, pref_range, weight):
	return ((range_ratio - 1) / pow(pref_range,2) * pow((total - pref_total), 2) + 1) * weight

def get_json(url):
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as json_resp:
        return json.loads(json_resp.read())

def get_period_ids(meal_date):
    old_period_dict = get_json("https://api.dineoncampus.com/v1/location/610b1f78e82971147c9f8ba5/periods?platform=0&date=" + meal_date)["periods"]
    new_period_dict = {}
    for period in old_period_dict:
        new_period_dict[period["name"]] = period["id"]
    return new_period_dict

def to_float(number_string):
    try:
        return float(number_string)
    except ValueError:
        return 0.0

def create_meal_list(meal_date):
    new_meal_list =[]
    for period in get_period_ids(meal_date).items():
        old_meal_dict = get_json("https://api.dineoncampus.com/v1/location/610b1f78e82971147c9f8ba5/periods/" + period[1] + "?platform=0&date=" + meal_date)["menu"]["periods"]["categories"]
        for place in old_meal_dict:
            for item in place["items"]:
                has_trans_fat = False
                is_vegetarian = False
                for filter in item["filters"]:
                    if (filter["name"] == "Vegetarian"):
                        is_vegetarian = True
                        break
                nutrient_dict = {}
                for nutrient in item["nutrients"]:
                    if (nutrient["name"] == "Calories"):
                        nutrient_dict["calories"] = to_float(nutrient["value_numeric"])
                    elif (nutrient["name"] == "Protein (g)"):
                        nutrient_dict["protein"] = to_float(nutrient["value_numeric"])
                    elif (nutrient["name"] == "Total Carbohydrates (g)"):
                        nutrient_dict["carbohydrates"] = to_float(nutrient["value_numeric"])
                    elif (nutrient["name"] == "Sugar (g)"):
                        nutrient_dict["sugar"] = to_float(nutrient["value_numeric"])
                    elif (nutrient["name"] == "Total Fat (g)"):
                        nutrient_dict["total_fat"] = to_float(nutrient["value_numeric"])
                    elif (nutrient["name"] == "Saturated Fat (g)"):
                        nutrient_dict["saturated_fat"] = to_float(nutrient["value_numeric"])
                    elif (nutrient["name"] == "Cholesterol (mg)"):
                        nutrient_dict["cholesterol"] = to_float(nutrient["value_numeric"])
                    elif (nutrient["name"] == "Dietary Fiber (g)"):
                        nutrient_dict["dietary_fiber"] = to_float(nutrient["value_numeric"])
                    elif (nutrient["name"] == "Sodium (mg)"):
                        nutrient_dict["sodium"] = to_float(nutrient["value_numeric"])
                    elif (nutrient["name"] == "Potassium (mg)"):
                        nutrient_dict["potassium"] = to_float(nutrient["value_numeric"])
                    elif (nutrient["name"] == "Calcium (mg)"):
                        nutrient_dict["calcium"] = to_float(nutrient["value_numeric"])
                    elif (nutrient["name"] == "Iron (mg)"):
                        nutrient_dict["iron"] = to_float(nutrient["value_numeric"])
                    elif (nutrient["name"] == "Trans Fat (g)"):
                        if (to_float(nutrient["value_numeric"]) != 0.0):
                            has_trans_fat = True
                            break
                    elif (nutrient["name"] == "Vitamin D (IU)"):
                        nutrient_dict["vitamin_d"] = to_float(nutrient["value_numeric"])
                    elif (nutrient["name"] == "Vitamin C (mg)"):
                        nutrient_dict["vitamin_c"] = to_float(nutrient["value_numeric"])
                    elif (nutrient["name"] == "Vitamin A (RE)"):
                        nutrient_dict["vitamin_a"] = to_float(nutrient["value_numeric"])
                if (is_vegetarian and not has_trans_fat):
                    new_meal_list.append({"name":item["name"],"place":place["name"],"periods":[period[0]],"ingredients":item["ingredients"],"portion":item["portion"],"nutrients":nutrient_dict})
    new_meal_list.sort(key = lambda item: item["name"])
    refined_meal_list = []
    current_name = "This is used to remove duplicates."
    current_refined = -1
    for item_num in range(len(new_meal_list)):
        if new_meal_list[item_num]["name"] != current_name:
            refined_meal_list.append(new_meal_list[item_num])
            current_name = new_meal_list[item_num]["name"]
            current_refined+=1
        elif new_meal_list[item_num]["periods"][0] not in refined_meal_list[current_refined]["periods"]:
            refined_meal_list[current_refined]["periods"].append(new_meal_list[item_num]["periods"][0])
    return refined_meal_list
    
final_list = []
high_score = -1000000000.0
base_nutrients = {"calories":0.0,"protein":0.0,"carbohydrates":0.0,"sugar":0.0,"total_fat":0.0,"saturated_fat":0.0,"cholesterol":0.0,"dietary_fiber":0.0,"sodium":0.0,"potassium":0.0,"calcium":0.0,"iron":0.0,"vitamin_d":0.0,"vitamin_c":0.0,"vitamin_a":0.0}

def str_item_list(all_items, item_list):
    return_string = ""
    for item_num in item_list:
        return_string+=all_items[item_num]["name"] + "\n"
    return return_string

def recursive_score(all_items, score, nutrient_dict, item_list, start_int):
    for item_num in range(start_int,len(all_items)):
        new_nutrients = {"calories":nutrient_dict["calories"] + all_items[item_num]["nutrients"]["calories"],"protein":nutrient_dict["protein"] + all_items[item_num]["nutrients"]["protein"],"carbohydrates":nutrient_dict["carbohydrates"] + all_items[item_num]["nutrients"]["carbohydrates"],"sugar":nutrient_dict["sugar"] + all_items[item_num]["nutrients"]["sugar"],"total_fat":nutrient_dict["total_fat"] + all_items[item_num]["nutrients"]["total_fat"],"saturated_fat":nutrient_dict["saturated_fat"] + all_items[item_num]["nutrients"]["saturated_fat"],"cholesterol":nutrient_dict["cholesterol"] + all_items[item_num]["nutrients"]["cholesterol"],"dietary_fiber":nutrient_dict["dietary_fiber"] + all_items[item_num]["nutrients"]["dietary_fiber"],"sodium":nutrient_dict["sodium"] + all_items[item_num]["nutrients"]["sodium"],"potassium":nutrient_dict["potassium"] + all_items[item_num]["nutrients"]["potassium"],"calcium":nutrient_dict["calcium"] + all_items[item_num]["nutrients"]["calcium"],"iron":nutrient_dict["iron"] + all_items[item_num]["nutrients"]["iron"],"vitamin_d":nutrient_dict["vitamin_d"] + all_items[item_num]["nutrients"]["vitamin_d"],"vitamin_c":nutrient_dict["vitamin_c"] + all_items[item_num]["nutrients"]["vitamin_c"],"vitamin_a":nutrient_dict["vitamin_a"] + all_items[item_num]["nutrients"]["vitamin_a"]}
        new_score = score_meal(new_nutrients)
        if (new_score > score):
            new_item_list = item_list.copy()
            new_item_list.append(item_num)
            global high_score
            if (new_score > high_score):
                high_score = new_score
                print("\nNew High Score: " + str(high_score))
                print(str_item_list(all_items, new_item_list))
                print(new_nutrients)
                print(len(all_items))
            if (len(new_item_list) < 1000):
                recursive_score(all_items, new_score, new_nutrients, new_item_list, item_num + 1)
            else:
                final_list.append((score, new_item_list))
        else:
            final_list.append((score, item_list))

recursive_score(create_meal_list(today), -1000000000, base_nutrients, [], 0)
